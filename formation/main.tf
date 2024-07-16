resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

resource "azurerm_storage_account" "storage_account" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_postgresql_flexible_server" "postgresql" {
  name                = var.postgres_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  administrator_login          = var.admin_user
  administrator_password       = var.admin_password
  sku_name                     = "B_Standard_B1ms"
  storage_mb                   = 32768
  version                      = "13"
  public_network_access_enabled = true
  storage_tier                 = "P4"  
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "firewall_rule" {
  name             = "postgresql-rule"
  server_id        = azurerm_postgresql_flexible_server.postgresql.id
  start_ip_address = var.postgres_ip_access_start
  end_ip_address   = var.postgres_ip_access_end
  
}

resource "azurerm_service_plan" "service_plan" {
  name                = "example-app-service-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "Y1"

  depends_on = [azurerm_postgresql_flexible_server.postgresql] # Cette ressource sera créée après que le PostgreSQL sera créé.
}

resource "azurerm_linux_function_app" "linux_function_app" {
  name                       = "ScrapyFunction"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.storage_account.name
  storage_account_access_key = azurerm_storage_account.storage_account.primary_access_key
  service_plan_id            = azurerm_service_plan.service_plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }
  app_settings = {
    IS_POSTGRES = var.IS_POSTGRES
    DB_USERNAME = var.DB_USERNAME
    DB_HOSTNAME = "${azurerm_postgresql_flexible_server.postgresql.name}.postgres.database.azure.com"
    DB_PORT = var.DB_PORT
    DB_NAME = var.DB_NAME
    DB_PASSWORD = var.DB_PASSWORD
  }
  
}
resource "null_resource" "publish_function_app" {
    # c'est la ressource qui permet de publier la fonction sur azure
  depends_on = [azurerm_function_app.functionapp]

  provisioner "local-exec" {
    command = "func azure functionapp publish ${var.function_app_name} --publish-local-settings"
  }
}