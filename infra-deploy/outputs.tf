output "ssh-connect" {
  value = "ssh ${var.username}@${yandex_compute_instance.web-store-instance.network_interface.0.nat_ip_address}"
}
