#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y docker.io nginx postgresql postgresql-contrib curl

sudo systemctl enable --now docker
sudo systemctl enable --now nginx
sudo systemctl enable --now postgresql

sudo -u postgres psql -c "CREATE DATABASE inventory;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER mywebapp WITH PASSWORD 'password';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory TO mywebapp;" 2>/dev/null || true

sudo mkdir -p /etc/mywebapp
cat <<EOF | sudo tee /etc/mywebapp/config.json > /dev/null
{
    "port": 3000,
    "db_host": "127.0.0.1",
    "db_name": "inventory",
    "db_user": "mywebapp",
    "db_password": "password"
}
EOF

cat <<EOF | sudo tee /etc/systemd/system/mywebapp-container.service > /dev/null
[Unit]
Description=My Web App Container
After=docker.service postgresql.service
Requires=docker.service

[Service]
TimeoutStartSec=0
Restart=always
ExecStartPre=-/usr/bin/docker stop mywebapp
ExecStartPre=-/usr/bin/docker rm mywebapp
ExecStart=/usr/bin/docker run --name mywebapp --net=host -v /etc/mywebapp/config.json:/etc/mywebapp/config.json:ro ghcr.io/${GITHUB_REPOSITORY_PLACEHOLDER}:stable
ExecStop=/usr/bin/docker stop mywebapp

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF | sudo tee /etc/nginx/sites-available/mywebapp > /dev/null
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
    }

    location /items {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
    }

    location /health {
        deny all;
        return 404;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/
sudo systemctl restart nginx

sudo systemctl daemon-reload
sudo systemctl enable mywebapp-container.service