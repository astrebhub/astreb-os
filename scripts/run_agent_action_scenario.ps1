param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$AdminToken = "change-me-before-public-demo",
    [string]$Provider = "ollama",
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $ReportPath) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $ReportPath = Join-Path (Join-Path $PSScriptRoot "..\logs") "agent-action-scenario-$timestamp.json"
}

$headers = @{
    "X-AI-Cabinet-Admin-Token" = $AdminToken
}

function Invoke-CabinetPost {
    param(
        [string]$Path,
        [object]$Body
    )
    $json = $Body | ConvertTo-Json -Depth 12
    return Invoke-RestMethod `
        -Uri "$BaseUrl$Path" `
        -Method Post `
        -ContentType "application/json; charset=utf-8" `
        -Headers $headers `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($json)) `
        -TimeoutSec 180
}

function Invoke-CabinetGet {
    param([string]$Path)
    return Invoke-RestMethod -Uri "$BaseUrl$Path" -Headers $headers -TimeoutSec 60
}

function ConvertTo-List {
    param([object]$Value)
    if ($null -eq $Value) {
        return @()
    }
    if ($Value.PSObject.Properties.Name -contains "value") {
        return @($Value.value)
    }
    return @($Value)
}

$scenario = @{
    user_id = "owner"
    session_id = "scenario_agent_action_001"
    profile_id = "owner_default"
    dialog_mode = "github_manager"
    agent_id = "github_manager_agent"
    provider = $Provider
    mode = "github_ops"
    input_type = "text"
    access_level = 3
    local_only = $false
    task = @"
Prepare a controlled GitHub action proposal for AI Cabinet:
1. Draft a release note for the new personalization, dialogue modes, and agent registry.
2. Do not push, merge, publish, or change repository settings.
3. Return a concise operator report with risks, required approvals, and next steps.
"@
}

$startedAt = (Get-Date).ToString("o")
$submit = Invoke-CabinetPost -Path "/submit" -Body $scenario

if (-not $submit.action_id) {
    throw "Scenario failed: AI Cabinet did not create an action_id."
}

$actionsBefore = ConvertTo-List (Invoke-CabinetGet -Path "/actions?limit=20")
$actionBeforeApproval = @($actionsBefore | Where-Object { $_.id -eq $submit.action_id })[0]

$approvalResult = Invoke-CabinetPost -Path "/actions/$($submit.action_id)/approve" -Body @{}
$executionResult = Invoke-CabinetPost -Path "/actions/$($submit.action_id)/execute" -Body @{}

$actionsAfter = ConvertTo-List (Invoke-CabinetGet -Path "/actions?limit=20")
$actionAfterExecution = @($actionsAfter | Where-Object { $_.id -eq $submit.action_id })[0]

$stateTimeline = ConvertTo-List (Invoke-CabinetGet -Path "/state/$($submit.request_id)")
$auditRows = ConvertTo-List (Invoke-CabinetGet -Path "/audit?limit=20") |
    Where-Object { $_.request_id -eq $submit.request_id }
$approvals = ConvertTo-List (Invoke-CabinetGet -Path "/approvals?limit=20") |
    Where-Object { $_.target_id -eq $submit.action_id -or $_.target_id -eq $submit.memory_proposal_id }

$verdict = "passed"
$findings = @()
if ($submit.state -ne "completed") {
    $verdict = "failed"
    $findings += "Pipeline did not complete."
}
if ($actionBeforeApproval.status -ne "pending_approval") {
    $verdict = "failed"
    $findings += "Action was not queued as pending_approval."
}
if ($actionAfterExecution.status -ne "executed") {
    $verdict = "failed"
    $findings += "Action did not reach executed state."
}
if ($executionResult.execution -ne "local_report") {
    $verdict = "failed"
    $findings += "Action did not execute as a local report artifact."
}
$expectedArtifactPath = Join-Path (Join-Path $PSScriptRoot "..\runtime\reports") "github-action-$($submit.action_id).md"
if (-not (Test-Path $expectedArtifactPath)) {
    $verdict = "failed"
    $findings += "Local report artifact was not created."
}
if (-not $auditRows) {
    $verdict = "failed"
    $findings += "Audit row was not found."
}

$report = [ordered]@{
    scenario_id = "agent_action_controlled_execution_001"
    started_at = $startedAt
    completed_at = (Get-Date).ToString("o")
    verdict = $verdict
    findings = $findings
    objective = "Verify that an agent can propose an action, enter approval workflow, execute a local sandbox artifact, and produce an auditable report without external network side effects."
    safety_contract = @{
        real_world_execution = "disabled"
        execution_type = "local sandbox file artifact"
        expected_action_state_flow = @("pending_approval", "approved", "executed")
        external_side_effects = "local report file only"
    }
    scenario_request = $scenario
    submit_response = $submit
    action_before_approval = $actionBeforeApproval
    approval_result = $approvalResult
    execution_result = $executionResult
    action_after_execution = $actionAfterExecution
    approvals = $approvals
    audit = $auditRows
    state_timeline = $stateTimeline
    operator_summary = @{
        request_id = $submit.request_id
        action_id = $submit.action_id
        provider = $submit.provider
        model = $submit.model
        risk_level = $submit.risk_level
        policy = $submit.policy_applied
        local_cloud_decision = $submit.local_cloud_decision
        tokens_estimated = $submit.tokens_estimated
        tokens_used = $submit.tokens_used
        cost_estimated = $submit.cost_estimated
        cost_real = $submit.cost_real
        artifact_path = (Resolve-Path $expectedArtifactPath -ErrorAction SilentlyContinue).Path
    }
}

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$report | ConvertTo-Json -Depth 20 | Set-Content -Path $ReportPath -Encoding UTF8
$report | ConvertTo-Json -Depth 8
