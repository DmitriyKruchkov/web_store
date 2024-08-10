variable "username" {
  description = "(Optional) - Username in created compute instance"
  type        = string
  default     = "kryuchkov"
}

variable "opened_ports" {
    description = "Listened ports for LB"
  type = list(number)
  default = [8080, 3000, 80]
}

