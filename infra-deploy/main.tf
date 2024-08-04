locals {
  ssh-key               = file("~/.ssh/id_rsa.pub")
  ssh-key-private-file  = "~/.ssh/id_rsa"
  ansible-playbook-name = "playbook.yml"
}


resource "yandex_compute_disk" "web-store-disk" {
  name     = "web-store-disk"
  type     = "network-hdd"
  size     = "30"
  image_id = "fd8in27h07j9pfapcduu"
}

resource "yandex_vpc_network" "web-store-network" {
  name = "web-store-network"
}

resource "yandex_vpc_subnet" "web-store-subnet" {
  name           = "web-store-subnet"
  v4_cidr_blocks = ["10.2.0.0/16"]
  network_id     = yandex_vpc_network.web-store-network.id
}


resource "yandex_compute_instance" "web-store-instance" {
  name        = "web-store-instance"
  platform_id = "standard-v3"

  scheduling_policy {
    preemptible = true
  }
  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }
  boot_disk {
    disk_id = yandex_compute_disk.web-store-disk.id
  }
  network_interface {
    subnet_id = yandex_vpc_subnet.web-store-subnet.id
    nat       = true
  }
  metadata = {
    user-data = templatefile("cloud-init.tftpl", {
      username = var.username,
      ssh-key  = local.ssh-key
    })
  }
  provisioner "remote-exec" {
    inline = ["echo 'Ready to connect!'"]

    connection {
      type        = "ssh"
      host        = self.network_interface.0.nat_ip_address
      user        = var.username
      private_key = file(local.ssh-key-private-file)
    }
  }

  provisioner "local-exec" {

    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -u ${var.username} -i '${self.network_interface.0.nat_ip_address},' -e ansible_ssh_pipelining=True --private-key ${local.ssh-key-private-file} ${local.ansible-playbook-name}"
  }

}
