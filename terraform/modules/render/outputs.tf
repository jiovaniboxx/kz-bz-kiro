# Render Module Outputs

output "service_id" {
  description = "Render service ID"
  value       = null_resource.render_service.id
}

output "service_url" {
  description = "Render service URL"
  value       = "https://${var.service_name}.onrender.com"
}

output "database_id" {
  description = "Render database ID"
  value       = var.create_database ? null_resource.render_database[0].id : null
}

output "database_connection_string" {
  description = "Database connection string (placeholder)"
  value       = var.create_database ? "postgresql://user:password@${var.database_name}.render.com:5432/${var.database_name}" : null
  sensitive   = true
}

output "health_check_url" {
  description = "Health check URL"
  value       = "https://${var.service_name}.onrender.com${var.health_check_path}"
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    service_name    = var.service_name
    environment     = var.environment
    region          = var.region
    auto_deploy     = var.auto_deploy
    github_repo     = var.github_repo
    branch          = var.branch
  }
}