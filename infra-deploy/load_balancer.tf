# resource "yandex_alb_target_group" "web-store-target-group" {
#   name = "web-store-target-group"
#
#   target {
#     subnet_id  = yandex_vpc_subnet.web-store-subnet.id
#     ip_address = yandex_compute_instance.web-store-instance.network_interface.0.ip_address
#   }
# }
#
# resource "yandex_alb_http_router" "web-router" {
#   name = "web-router"
# }
#
# resource "yandex_alb_backend_group" "grafana-backend" {
#   name = "grafana-backend-group"
#
#   http_backend {
#     name = "grafana-backend"
#     port = 3000
#     target_group_ids = [yandex_alb_target_group.web-store-target-group.id]
#
#     healthcheck {
#       http_healthcheck {
#         path = "/"
#       }
#       interval = "1s"
#       timeout = "1s"
#     }
#   }
# }
#
# resource "yandex_alb_backend_group" "jenkins-backend" {
#   name = "jenkins-backend-group"
#
#   http_backend {
#     name = "jenkins-backend"
#     port = 8080
#     target_group_ids = [yandex_alb_target_group.web-store-target-group.id]
#
#     healthcheck {
#       http_healthcheck {
#         path = "/"
#       }
#       interval = "1s"
#       timeout = "1s"
#     }
#   }
# }
#
# resource "yandex_alb_backend_group" "app-backend" {
#   name = "app-backend-group"
#
#   http_backend {
#     name = "app-backend"
#     port = 80
#     target_group_ids = [yandex_alb_target_group.web-store-target-group.id]
#
#     healthcheck {
#       http_healthcheck {
#         path = "/"
#       }
#       interval = "1s"
#       timeout = "1s"
#     }
#   }
# }
#
# resource "yandex_alb_load_balancer" "test-balancer" {
#   name       = "my-load-balancer"
#   network_id = yandex_vpc_network.web-store-network.id
#
#   allocation_policy {
#     location {
#       zone_id   = "ru-central1-a"
#       subnet_id = yandex_vpc_subnet.web-store-subnet.id
#     }
#   }
#
#   listener {
#     name = "my-listener"
#     endpoint {
#       address {
#         external_ipv4_address {}
#       }
#       ports = [80]  # HTTP слушает на порту 80
#     }
#     http {
#       handler {
#         http_router_id = yandex_alb_http_router.web-router.id
#       }
#     }
#   }
# }
