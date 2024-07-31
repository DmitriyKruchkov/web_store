source "yandex" "kube-worker" {
  # OAuth-токен и folder_id лучше задать переменными окружения YC_TOKEN
#  token               = "<OAuth-токен>"
  folder_id           = var.folder_id
  source_image_family = "debian-12"
  ssh_username        = "kube-worker"
  use_ipv4_nat        = "true"
  image_description   = "kube worker image based on Debian 12"
  image_family        = "kube-worker-debian-12"
  image_name          = "kube-worker"
  disk_type           = var.disk_type
  zone                = var.zone
}

build {
  sources = ["source.yandex.kube-worker"]

  provisioner "ansible" {
    playbook_file = "./playbook.yml"
  }
}