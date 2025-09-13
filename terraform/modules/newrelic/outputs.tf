# New Relic Module Outputs

output "application_id" {
  description = "New Relic application ID"
  value       = newrelic_application.english_cafe.id
}

output "application_guid" {
  description = "New Relic application GUID"
  value       = newrelic_application.english_cafe.guid
}

output "alert_policy_ids" {
  description = "Map of alert policy names to IDs"
  value = {
    performance = newrelic_alert_policy.performance.id
    errors      = newrelic_alert_policy.errors.id
    business    = newrelic_alert_policy.business.id
  }
}

output "alert_condition_ids" {
  description = "Map of alert condition names to IDs"
  value = {
    high_error_rate      = newrelic_alert_condition.high_error_rate.id
    slow_response_time   = newrelic_alert_condition.slow_response_time.id
    high_memory_usage    = newrelic_alert_condition.high_memory_usage.id
    poor_lcp            = newrelic_nrql_alert_condition.poor_lcp.id
    poor_fid            = newrelic_nrql_alert_condition.poor_fid.id
    poor_cls            = newrelic_nrql_alert_condition.poor_cls.id
  }
}

output "dashboard_id" {
  description = "New Relic dashboard ID"
  value       = newrelic_one_dashboard.performance_overview.id
}

output "dashboard_permalink" {
  description = "New Relic dashboard permalink"
  value       = newrelic_one_dashboard.performance_overview.permalink
}

output "workload_id" {
  description = "New Relic workload ID"
  value       = newrelic_workload.english_cafe.id
}

output "workload_permalink" {
  description = "New Relic workload permalink"
  value       = newrelic_workload.english_cafe.permalink
}

output "notification_destination_ids" {
  description = "Map of notification destination names to IDs"
  value = {
    slack = length(newrelic_notification_destination.slack) > 0 ? newrelic_notification_destination.slack[0].id : null
    email = length(newrelic_notification_destination.email) > 0 ? newrelic_notification_destination.email[0].id : null
  }
}

output "workflow_ids" {
  description = "Map of workflow names to IDs"
  value = {
    performance_alerts = newrelic_workflow.performance_alerts.id
    error_alerts      = newrelic_workflow.error_alerts.id
  }
}

output "application_id" {
  description = "New Relic application ID"
  value       = newrelic_application.english_cafe.id
}

output "application_guid" {
  description = "New Relic application GUID"
  value       = newrelic_application.english_cafe.guid
}

output "application_name" {
  description = "New Relic application name"
  value       = newrelic_application.english_cafe.name
}

output "alert_policy_ids" {
  description = "Alert policy IDs"
  value = {
    performance = newrelic_alert_policy.performance.id
    errors      = newrelic_alert_policy.errors.id
    business    = newrelic_alert_policy.business.id
  }
}

output "dashboard_url" {
  description = "URL to the performance dashboard"
  value       = "https://one.newrelic.com/redirect/entity/${newrelic_application.english_cafe.guid}"
}

output "dashboard_id" {
  description = "Performance dashboard ID"
  value       = newrelic_one_dashboard.performance_overview.id
}

output "workload_id" {
  description = "Workload ID"
  value       = newrelic_workload.english_cafe.id
}

output "workload_guid" {
  description = "Workload GUID"
  value       = newrelic_workload.english_cafe.guid
}

output "notification_destinations" {
  description = "Notification destination IDs"
  value = {
    slack = length(newrelic_notification_destination.slack) > 0 ? newrelic_notification_destination.slack[0].id : null
    email = length(newrelic_notification_destination.email) > 0 ? newrelic_notification_destination.email[0].id : null
  }
}

output "workflow_ids" {
  description = "Workflow IDs for alert routing"
  value = {
    performance = newrelic_workflow.performance_alerts.id
    errors      = newrelic_workflow.error_alerts.id
  }
}

output "alert_condition_ids" {
  description = "Alert condition IDs"
  value = {
    high_error_rate      = newrelic_alert_condition.high_error_rate.id
    slow_response_time   = newrelic_alert_condition.slow_response_time.id
    high_memory_usage    = newrelic_alert_condition.high_memory_usage.id
    poor_lcp            = newrelic_nrql_alert_condition.poor_lcp.id
    poor_fid            = newrelic_nrql_alert_condition.poor_fid.id
    poor_cls            = newrelic_nrql_alert_condition.poor_cls.id
  }
}

output "monitoring_urls" {
  description = "Important monitoring URLs"
  value = {
    application_overview = "https://one.newrelic.com/redirect/entity/${newrelic_application.english_cafe.guid}"
    performance_dashboard = "https://one.newrelic.com/redirect/entity/${newrelic_one_dashboard.performance_overview.guid}"
    alert_policies = "https://alerts.newrelic.com/accounts/${var.newrelic_account_id}/policies"
    workload = "https://one.newrelic.com/redirect/entity/${newrelic_workload.english_cafe.guid}"
  }
}