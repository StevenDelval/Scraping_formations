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
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "firewall_rule" {
  name             = "postgresql-rule"
  server_id        = azurerm_postgresql_flexible_server.postgresql.id
  start_ip_address = var.postgres_ip_access_start
  end_ip_address   = var.postgres_ip_access_end

}

resource "azurerm_container_app_environment" "container_app_environment" {
  name                = "sfm-container-app-environment"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  depends_on = [azurerm_postgresql_flexible_server.postgresql]
}

resource "azurerm_container_registry" "acr" {
  name                = var.container_registry_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    command = <<EOT
    ACR_NAME=${azurerm_container_registry.acr.name}
    RESOURCE_GROUP=${azurerm_resource_group.rg.name}
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
    ACR_IMAGE_NAME=${var.image_name}

    az acr login --name $ACR_NAME
    docker tag $ACR_IMAGE_NAME $ACR_LOGIN_SERVER/$ACR_IMAGE_NAME
    docker push $ACR_LOGIN_SERVER/$ACR_IMAGE_NAME

    EOT
  }
  depends_on = [azurerm_container_registry.acr]
}



resource "azurerm_service_plan" "service_plan" {
  name                = "sfm_app_service_plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "EP1"

  depends_on = [azurerm_postgresql_flexible_server.postgresql] # Cette ressource sera créée après que le PostgreSQL sera créé.
}

resource "azurerm_application_insights" "insights" {
  name                = "sfm-appinsights"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  depends_on = [azurerm_service_plan.service_plan]
}


resource "azurerm_linux_function_app" "funcApp" {
  name                       = "sfm-azure-functions"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  service_plan_id            = azurerm_service_plan.service_plan.id
  storage_account_name       = azurerm_storage_account.storage_account.name
  storage_account_access_key = azurerm_storage_account.storage_account.primary_access_key
  functions_extension_version = "~4" 
  
  site_config {
    application_stack {
      docker {
        registry_url      = azurerm_container_registry.acr.login_server
        image_name        = var.image_name
        image_tag         = "latest"  # Replace with your specific image tag
        registry_username = azurerm_container_registry.acr.admin_username
        registry_password = azurerm_container_registry.acr.admin_password
      }
    }
    application_insights_connection_string = azurerm_application_insights.insights.connection_string
    application_insights_key = azurerm_application_insights.insights.instrumentation_key
  }

  app_settings = {
    DOCKER_REGISTRY_SERVER_URL                = "${azurerm_container_registry.acr.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME           = "${azurerm_container_registry.acr.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD           = "${azurerm_container_registry.acr.admin_password}"
    IS_POSTGRES = var.IS_POSTGRES
    DB_USERNAME = var.DB_USERNAME
    DB_HOSTNAME = "${azurerm_postgresql_flexible_server.postgresql.name}.postgres.database.azure.com"
    DB_PORT     = var.DB_PORT
    DB_NAME     = var.DB_NAME
    DB_PASSWORD = var.DB_PASSWORD
  }

  depends_on = [
    null_resource.docker_push,
    azurerm_application_insights.insights,
    azurerm_service_plan.service_plan
  ]

  
}