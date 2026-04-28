#!/bin/bash
set -e

apt-get update
apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib nginx sudo curl git

useradd -m -s /bin/bash student
usermod -aG sudo student

useradd -m -s /bin/bash teacher
usermod -aG sudo teacher
echo "teacher:12345678" | chpasswd
chage -d 0 teacher

useradd -r -s /bin/false app

useradd -m -s /bin/bash operator
echo "operator:12345678" | chpasswd
chage -d 0 operator

cat <<EOF > /etc/sudoers.d/operator
operator ALL=(ALL) NOPASSWD: /bin/systemctl start mywebapp.service, /bin/systemctl stop mywebapp.service, /bin/systemctl restart mywebapp.service, /bin/systemctl status mywebapp.service, /bin/systemctl reload nginx.service
EOF
chmod 0440 /etc/sudoers.d/operator

echo "17" > /home/student/gradebook
chown student:student /home/student/gradebook

sudo -u postgres psql -c "CREATE DATABASE inventory;"
sudo -u postgres psql -c "CREATE USER app WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory TO app;"
sudo -u postgres psql -d inventory -c "ALTER SCHEMA public OWNER TO app;"

mkdir -p /opt/mywebapp
cp -r ./* /opt/mywebapp/
chown -R app:app /opt/mywebapp

mkdir -p /etc/mywebapp
cat <<EOF > /etc/mywebapp/config.json
{
    "port": 3000,
    "db_host": "127.0.0.1",
    "db_name": "inventory",
    "db_user": "app",
    "db_password": "password"
}
EOF
chown -R app:app /etc/mywebapp

cd /opt/mywebapp
sudo -u app python3 -m venv venv
sudo -u app ./venv/bin/pip install -r requirements.txt

cat <<EOF > /etc/systemd/system/mywebapp.socket
[Unit]
Description=My Web App Socket

[Socket]
ListenStream=3000

[Install]
WantedBy=sockets.target
EOF

cat <<EOF > /etc/systemd/system/mywebapp.service
[Unit]
Description=My Web App
Requires=mywebapp.socket
After=network.target postgresql.service

[Service]
User=app
WorkingDirectory=/opt/mywebapp
ExecStartPre=/opt/mywebapp/venv/bin/python /opt/mywebapp/migrate.py
ExecStart=/opt/mywebapp/venv/bin/gunicorn app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mywebapp.socket
systemctl start mywebapp.socket

cat <<EOF > /etc/nginx/sites-available/mywebapp
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/
systemctl restart nginx

DEFAULT_USER=${SUDO_USER:-ubuntu}
if id "$DEFAULT_USER" &>/dev/null; then
    usermod -L "$DEFAULT_USER"
fi