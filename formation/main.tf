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

  administrator_login           = var.admin_user
  administrator_password        = var.admin_password
  sku_name                      = "B_Standard_B1ms"
  storage_mb                    = 32768
  version                       = "13"
  public_network_access_enabled = true
  storage_tier                  = "P4"
  lifecycle {
    ignore_changes = [
      # Ignore changes to tags, e.g. because a management agent
      # updates these based on some ruleset managed elsewhere.
      zone,
    ]
  }
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "firewall_rule" {
  name             = "postgresql-rule"
  server_id        = azurerm_postgresql_flexible_server.postgresql.id
  start_ip_address = var.postgres_ip_access_start
  end_ip_address   = var.postgres_ip_access_end

}



resource "azurerm_log_analytics_workspace" "log_analytics" {
  name                = "log-analytics-workspace-scrapy"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
}

resource "azurerm_container_app_environment" "container_env" {
  name                       = var.container_env_name
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log_analytics.id
  depends_on = [azurerm_postgresql_flexible_server_firewall_rule.firewall_rule]
}

resource "azurerm_container_app_job" "container_job" {
  name                         = "container-app-job-scrapy"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  container_app_environment_id = azurerm_container_app_environment.container_env.id

  replica_timeout_in_seconds = 600
  replica_retry_limit        = 0
  
  schedule_trigger_config{
    cron_expression="0 */2 * * *"
  }
  template {
    
    container {
      image = "${var.server_name}/${var.image_name}"

      name  = var.image_name
      cpu    = 0.5
      memory = "1Gi"
      

      env {
        name  = "IS_POSTGRES"
        value = var.IS_POSTGRES
      }
      env {
        name  = "DB_USERNAME"
        value = var.DB_USERNAME
      }
      env {
        name  = "DB_HOSTNAME"
        value = "${azurerm_postgresql_flexible_server.postgresql.name}.postgres.database.azure.com"
      }
      env {
        name  = "DB_PORT"
        value = var.DB_PORT
      }
      env {
        name  = "DB_NAME"
        value = var.DB_NAME
      }
      env {
        name  = "DB_PASSWORD"
        value = var.DB_PASSWORD
      }
    }
    
  }
  
}