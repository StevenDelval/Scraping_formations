# Resource group for organizing related Azure resources
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

# Flexible PostgreSQL server within the specified resource group
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

# Firewall rule for allowing specific IP range to access the PostgreSQL server
resource "azurerm_postgresql_flexible_server_firewall_rule" "firewall_rule" {
  name             = "postgresql-rule"
  server_id        = azurerm_postgresql_flexible_server.postgresql.id
  start_ip_address = var.postgres_ip_access_start
  end_ip_address   = var.postgres_ip_access_end

}


# Log Analytics workspace for monitoring and logging
resource "azurerm_log_analytics_workspace" "log_analytics" {
  name                = "log-analytics-workspace-scrapy"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
}

# Container App Environment for running containerized applications
resource "azurerm_container_app_environment" "container_env" {
  name                       = var.container_env_name
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log_analytics.id
  depends_on = [azurerm_postgresql_flexible_server_firewall_rule.firewall_rule]
}

# Container App Job for running scheduled tasks within the specified environment
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
      image = "${var.server_name}/${var.image_name_scrapy}"

      name  = var.image_name_scrapy
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

# Container Group for deploying containerized applications with public IP
resource "azurerm_container_group" "container_group" {
  name                = var.container_group_name_api
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ip_address_type     = "Public"
  os_type             = "Linux"
  restart_policy      = "Never"

  

  container {
    name   = var.container_name_api
    image  = "${var.server_name}/${var.image_name_api}"
    cpu    = "1"
    memory = "1"

    ports {
      port     = 80
      protocol = "TCP"
    }

    environment_variables = {
      IS_POSTGRES = var.IS_POSTGRES
      DB_USERNAME = var.DB_USERNAME
      DB_HOSTNAME = "${azurerm_postgresql_flexible_server.postgresql.name}.postgres.database.azure.com"
      DB_PORT = var.DB_PORT
      DB_NAME = var.DB_NAME
    }

    secure_environment_variables = {
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  depends_on = [azurerm_container_app_job.container_job]
}