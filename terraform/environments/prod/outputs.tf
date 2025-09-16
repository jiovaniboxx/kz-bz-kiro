# Production Environment Outputs

# New Relic Outputs
output "newrelic_application_id" {
  description = "New Relic application ID"
  value       = module.newrelic.application_id
}

output "newrelic_application_guid" {
  description = "New Relic application GUID"
  value       = module.newrelic.application_guid
}

output "newrelic_alert_policies" {
  description = "New Relic alert policy IDs"
  value       = module.newrelic.alert_policy_ids
}

# Grafana Outputs
output "grafana_dashboard_urls" {
  description = "Grafana dashboard URLs"
  value       = module.grafana.dashboard_urls
}

output "grafana_folder_ids" {
  description = "Grafana folder IDs"
  value       = module.grafana.folder_ids
}

# Vercel Outputs
output "vercel_project_id" {
  description = "Vercel project ID"
  value       = vercel_project.english_cafe_frontend.id
}

output "vercel_deployment_url" {
  description = "Vercel deployment URL"
  value       = "https://${var.vercel_project_name}.vercel.app"
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured)"
  value       = var.custom_domain != "" ? "https://${var.custom_domain}" : null
}

# Render Outputs
output "render_service_id" {
  description = "Render service ID"
  value       = module.render.service_id
}

output "render_service_url" {
  description = "Render service URL"
  value       = module.render.service_url
}

output "render_database_id" {
  description = "Render database ID"
  value       = module.render.database_id
}

output "render_health_check_url" {
  description = "Render health check URL"
  value       = module.render.health_check_url
}

# Monitoring URLs
output "monitoring_urls" {
  description = "All monitoring service URLs"
  value = {
    newrelic_app     = "https://one.newrelic.com/launcher/nr1-core.explorer?pane=eyJuZXJkbGV0SWQiOiJucjEtY29yZS5saXN0aW5nIn0=&cards[0]=eyJuZXJkbGV0SWQiOiJhcG0uYXBwbGljYXRpb25zLWxpc3RpbmciLCJlbnRpdHlHdWlkIjoiJHtbXX0ifQ==&platform[accountId]=${var.newrelic_account_id}"
    grafana_org      = var.grafana_url
    vercel_project   = "https://vercel.com/dashboard/projects/${vercel_project.english_cafe_frontend.id}"
    render_service   = "https://dashboard.render.com/web/${var.render_service_name}"
  }
}

# Health Check URLs
output "health_check_urls" {
  description = "Health check endpoints"
  value = {
    frontend = "https://${var.vercel_project_name}.vercel.app"
    backend  = "https://${var.render_service_name}.onrender.com/health"
    api      = "https://${var.render_service_name}.onrender.com/api/health"
  }
}

# Cost Summary
output "cost_summary" {
  description = "Monthly cost summary for all services"
  value = local.cost_summary
}

# Configuration Summary
output "configuration_summary" {
  description = "Summary of monitoring configuration"
  value = {
    environment           = local.environment
    application_name     = var.application_name
    alert_policies_count = length(module.newrelic.alert_policy_ids)
    dashboards_count     = length(module.grafana.dashboard_urls)
    notification_channels = {
      slack_enabled = length(var.slack_webhook_url) > 0
      email_enabled = length(var.admin_email) > 0
    }
    thresholds = local.alert_thresholds
  }
}