#!/bin/bash
# Terraform Environment Variables Setup Script
# Usage: source ./terraform/scripts/set-env-vars.sh

echo "Setting up Terraform environment variables..."

# New Relic
export TF_VAR_newrelic_account_id="${NEWRELIC_ACCOUNT_ID}"
export TF_VAR_newrelic_api_key="${NEWRELIC_API_KEY}"
export TF_VAR_newrelic_license_key="${NEWRELIC_LICENSE_KEY}"

# Grafana
export TF_VAR_grafana_url="${GRAFANA_URL}"
export TF_VAR_grafana_auth_token="${GRAFANA_AUTH_TOKEN}"
export TF_VAR_grafana_api_key="${GRAFANA_API_KEY}"

# Render
export TF_VAR_render_api_key="${RENDER_API_KEY}"
export TF_VAR_render_service_name="${RENDER_SERVICE_NAME:-english-cafe-api}"

# Vercel (if using)
export TF_VAR_vercel_api_token="${VERCEL_API_TOKEN}"

# Application
export TF_VAR_application_name="${APPLICATION_NAME:-english-cafe-prod}"
export TF_VAR_aws_region="${AWS_REGION:-ap-northeast-1}"

echo "Environment variables set successfully!"
echo "You can now run: terraform plan or terraform apply"