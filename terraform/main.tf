terraform {
  required_providers {
    virtualbox = {
      source  = "shekeriev/virtualbox"
      version = "0.0.4"
    }
  }
}

provider "virtualbox" {
  delay      = 60
  mintimeout = 5
}

resource "virtualbox_vm" "db" {
  name   = "database-node"
  image  = "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64-vagrant.box"
  cpus   = 1
  memory = "1024 mib"

  user_data = file("${path.module}/cloud_init.yml")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Wi-Fi 6 AX201 160MHz" 
  }
}

resource "virtualbox_vm" "worker" {
  name   = "worker-node"
  image  = "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64-vagrant.box"
  cpus   = 1
  memory = "1024 mib"

  depends_on = [virtualbox_vm.db]
  user_data  = file("${path.module}/cloud_init.yml")

  network_adapter {
    type           = "bridged"
    host_interface = "Intel(R) Wi-Fi 6 AX201 160MHz"
  }
}