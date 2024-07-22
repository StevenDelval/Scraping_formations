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

resource "null_resource" "deploy_container_app" {
  provisioner "local-exec" {
    command = <<EOT
    RESOURCE_GROUP=${azurerm_resource_group.rg.name}
    ENVIRONMENT_NAME=${var.container_env_name}
    LOCATION=${azurerm_resource_group.rg.location}

    az containerapp env create --name $ENVIRONMENT_NAME \
      --enable-workload-profiles \
      --resource-group $RESOURCE_GROUP \
      --location $LOCATION

    EOT
  }
  depends_on = [
    null_resource.docker_push,
    azurerm_postgresql_flexible_server.postgresql

  ]
}

resource "null_resource" "deploy_function_app" {
  provisioner "local-exec" {
    command = <<EOT
    RESOURCE_GROUP=${azurerm_resource_group.rg.name}
    ACR_LOGIN_SERVER=${azurerm_container_registry.acr.login_server}
    ACR_IMAGE_NAME=${var.image_name}
    IMAGE="$ACR_LOGIN_SERVER/$ACR_IMAGE_NAME"
    ENVIRONMENT_NAME=${var.container_env_name}
    STORAGE_NAME=${azurerm_storage_account.storage_account.name}
    APP_FUNCTION_NAME=${var.function_app_name}
    REGISTRY_URL="${azurerm_container_registry.acr.login_server}"
    REGISTRY_USERNAME=${azurerm_container_registry.acr.admin_username}
    REGISTRY_PASSWORD=${azurerm_container_registry.acr.admin_password}

    
    az functionapp create --name $APP_FUNCTION_NAME \
      --storage-account $STORAGE_NAME \
      --environment $ENVIRONMENT_NAME \
      --workload-profile-name "Consumption" \
      --resource-group $RESOURCE_GROUP \
      --functions-version 4 \
      --runtime dotnet-isolated \
      --registry-server $REGISTRY_URL \
      --registry-username $REGISTRY_USERNAME  \
      --registry-password $REGISTRY_PASSWORD \
      --image $IMAGE

    EOT
  }
  depends_on = [null_resource.deploy_container_app]
}

resource "null_resource" "function_app_settings" {
  provisioner "local-exec" {
    command = <<EOT
    RESOURCE_GROUP=${azurerm_resource_group.rg.name}
    APP_FUNCTION_NAME=${var.function_app_name}
    IS_POSTGRES=${var.IS_POSTGRES}
    DB_USERNAME=${var.DB_USERNAME}
    DB_HOSTNAME="${azurerm_postgresql_flexible_server.postgresql.name}.postgres.database.azure.com"
    DB_PORT=${var.DB_PORT}
    DB_NAME=${var.DB_NAME}
    DB_PASSWORD=${var.DB_PASSWORD}
    MAX_RETRIES=5
    RETRY_DELAY=10
    COUNT=0

    while [ $COUNT -lt $MAX_RETRIES ]; do
      az functionapp config appsettings set --name $APP_FUNCTION_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings "IS_POSTGRES=$IS_POSTGRES" \
        "DB_USERNAME=$DB_USERNAME" \
        "DB_HOSTNAME=$DB_HOSTNAME" \
        "DB_PORT=$DB_PORT" \
        "DB_NAME=$DB_NAME" \
        "DB_PASSWORD=$DB_PASSWORD"
      
      if [ $? -eq 0 ]; then
        echo "App settings updated successfully."
        exit 0
      else
        echo "Failed to update app settings. Retrying in $RETRY_DELAY seconds..."
        COUNT=$((COUNT + 1))
        sleep $RETRY_DELAY
      fi
    done

    echo "Failed to update app settings after $MAX_RETRIES attempts."
    exit 1
    EOT
  }
  depends_on = [null_resource.deploy_function_app]
}