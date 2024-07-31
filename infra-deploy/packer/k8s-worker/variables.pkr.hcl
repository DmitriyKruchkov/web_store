variable "folder_id" {
  description = "(Optional) - Yandex Cloud Folder ID where image will be created."
  type = string
}
variable "zone" {
  description = "(Optional) - Yandex Cloud Zone for created image."
  type        = string
  default     = "ru-central1-a"
  validation {
    condition     = contains(["ru-central1-a", "ru-central1-b", "ru-central1-c", "ru-central1-d"], var.zone)
    error_message = "Allowed Yandex Cloud zones are ru-central1-a, ru-central1-b, ru-central1-c, ru-central1-d."
  }

}

variable "disk_type" {
  description = "(Optional) - Disk type for image."
  type = string
  default = "network-ssd"
  validation {
    condition     = contains(["network-ssd", "network-hdd", "network-ssd-nonreplicated", "network-ssd-io-m3"], var.disk_type)
    error_message = "Allowed Yandex Cloud disks are network-ssd, network-hdd, network-ssd-nonreplicated, network-ssd-io-m3."
  }

}