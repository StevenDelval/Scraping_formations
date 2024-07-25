# Scraping_formations


cd formation
func init . --worker-runtime python --model V2
func new --name ScrapyFunction --template "HTTP trigger" --authlevel "anonymous"

```
# Cree les ressources
terraform init -upgrade
terraform plan -var-file="terraform.tfvars" -out main.tfplan
terraform apply -var-file="terraform.tfvars" -auto-approve

# Supprimer les ressources
terraform plan -destroy -out main.destroy.tfplan
terraform apply main.destroy.tfplan
```