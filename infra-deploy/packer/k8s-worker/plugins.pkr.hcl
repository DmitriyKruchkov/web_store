packer {
  required_plugins {
    yandex = {
      version = "~> 1"
      source  = "github.com/hashicorp/yandex"
    }
    ansible = {
      version = "~> 1"
      source = "github.com/hashicorp/ansible"
    }
  }
}