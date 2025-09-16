# Test Configuration - Minimal Terraform Setup
# 英会話カフェWebサイト本番環境の監視設定テスト

terraform {
  required_version = ">= 1.6"
  
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 0.15"
    }
  }
}

# Provider Configuration
provider "vercel" {
  api_token = var.vercel_api_token
}

# Local Values
locals {
  environment = "prod"
  
  common_tags = {
    Environment   = local.environment
    Project      = "english-cafe"
    ManagedBy    = "terraform"
    Owner        = "engineering-team"
    Platform     = "vercel-render"
    Application  = var.application_name
  }
  
  # Vercel + Render configuration
  deployment_config = {
    frontend_url = "https://${var.vercel_project_name}.vercel.app"
    backend_url  = "https://${var.render_service_name}.onrender.com"
  }
}

# Vercel Project Configuration (Simplified)
resource "vercel_project" "english_cafe_frontend" {
  name      = var.vercel_project_name
  framework = "nextjs"
  
  git_repository = {
    type = "github"
    repo = var.github_repository
  }
  
  environment = [
    {
      key    = "NEXT_PUBLIC_API_URL"
      value  = local.deployment_config.backend_url
      target = ["production"]
    },
    {
      key    = "NEXT_PUBLIC_VERCEL_ANALYTICS"
      value  = "true"
      target = ["production"]
    }
  ]
}

# Vercel Domain Configuration
resource "vercel_project_domain" "english_cafe_domain" {
  count = var.custom_domain != "" ? 1 : 0
  
  project_id = vercel_project.english_cafe_frontend.id
  domain     = var.custom_domain
}

# Cost Summary (無料サービスのため最小限)
locals {
  cost_summary = {
    vercel = "Free (Hobby Plan)"
    render = "Free (up to 750 hours/month)"
    terraform_cloud = "Free (up to 5 users)"
    total_monthly_cost = "$0"
  }
}