# Backend parcial — o workflow preenche via -backend-config (storage de state remoto).
# Assim re-runs do Actions atualizam o mesmo ambiente em vez de criar RG duplicado.
terraform {
  backend "azurerm" {}
}
