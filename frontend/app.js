const $ = (id) => document.getElementById(id);
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";

function adminHeaders() {
  const token = $("adminToken")?.value || localStorage.getItem("AI_CABINET_ADMIN_TOKEN") || "";
  if (token) localStorage.setItem("AI_CABINET_ADMIN_TOKEN", token);
  return token ? {"X-AI-Cabinet-Admin-Token": token} : {};
}

async function postJSON(url, body = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: "POST",
    headers: {"Content-Type": "application/json", ...adminHeaders()},
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

async function getJSON(url) {
  const res = await fetch(`${API_BASE}${url}`, {headers: adminHeaders()});
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

window.addEventListener("DOMContentLoaded", () => {
  const savedToken = localStorage.getItem("AI_CABINET_ADMIN_TOKEN");
  if (savedToken && $("adminToken")) $("adminToken").value = savedToken;
});

function renderSide(data) {
  $("sideOutput").textContent = JSON.stringify(data, null, 2);
}

function setMetrics(data) {
  $("riskMetric").textContent = data.risk_level || "-";
  $("classMetric").textContent = data.data_class || "-";
  $("decisionMetric").textContent = data.local_cloud_decision || "-";
  $("costMetric").textContent = data.cost_estimated === undefined ? "-" : `$${data.cost_estimated.toFixed(6)}`;
}

$("sendBtn").onclick = async () => {
  $("status").textContent = "Running governed pipeline...";
  $("result").textContent = "";
  $("meta").innerHTML = "";

  try {
    const data = await postJSON("/submit", {
      agent_id: $("mode").value === "github_ops" ? "github_manager_agent" : "default_agent",
      provider: $("provider").value,
      mode: $("mode").value,
      input_type: $("inputType").value,
      access_level: Number($("accessLevel").value),
      local_only: $("localOnly").checked,
      task: $("task").value
    });

    setMetrics(data);
    $("meta").innerHTML = `
      <span class="badge">provider: ${data.provider}</span>
      <span class="badge">model: ${data.model}</span>
      <span class="badge">route: ${data.route_reason}</span>
      <span class="badge">input: ${data.normalized_input_type}</span>
      <span class="badge">state: ${data.state}</span>
      <span class="badge">policy: ${data.policy_applied}</span>
      <span class="badge">tokens: ${data.tokens_estimated}/${data.tokens_used}</span>
      ${data.action_id ? `<span class="badge">action: ${data.action_status}</span>` : ""}
      ${data.memory_proposal_id ? `<span class="badge">memory proposal</span>` : ""}
    `;
    $("result").textContent = [
      data.result,
      "",
      `Action ID: ${data.action_id || "-"}`,
      `Memory proposal ID: ${data.memory_proposal_id || "-"}`,
      `PII detected: ${JSON.stringify(data.pii_detected)}`,
      `Output scan: ${JSON.stringify(data.output_scan)}`
    ].join("\n");
    $("status").textContent = "Completed";
  } catch (e) {
    $("status").textContent = "Blocked/Error";
    $("result").textContent = e.message;
  }
};

$("healthBtn").onclick = async () => renderSide(await getJSON("/health"));
$("policyBtn").onclick = async () => renderSide(await getJSON("/config/policy"));
$("routingBtn").onclick = async () => renderSide(await getJSON("/config/model-routing"));
$("budgetBtn").onclick = async () => renderSide(await getJSON("/budget/status"));
$("pluginsBtn").onclick = async () => renderSide(await getJSON("/plugins"));
$("actionsBtn").onclick = async () => renderSide(await getJSON("/actions"));
$("approvalsBtn").onclick = async () => renderSide(await getJSON("/approvals"));
$("memoryLayersBtn").onclick = async () => renderSide(await getJSON("/memory/layers"));
$("auditBtn").onclick = async () => renderSide(await getJSON("/audit"));
$("localRuntimeBtn").onclick = async () => renderSide(await getJSON("/local-runtime/status"));
$("vectorBtn").onclick = async () => {
  const data = await postJSON("/vector-memory/search", {
    namespace: "project",
    query: $("task").value || "AI Cabinet",
    limit: 5
  });
  renderSide({namespace: "project", results: data});
};
$("voiceBtn").onclick = async () => renderSide(await getJSON("/voice/status"));
$("multimodalBtn").onclick = async () => renderSide(await getJSON("/multimodal/status"));
$("accessBtn").onclick = async () => renderSide(await getJSON("/access/users"));
$("agentsBtn").onclick = async () => renderSide(await getJSON("/agents"));
$("evidenceBtn").onclick = async () => renderSide(await getJSON("/evidence"));
$("observabilityBtn").onclick = async () => renderSide(await getJSON("/observability/events"));
$("forecastsBtn").onclick = async () => renderSide(await getJSON("/forecasts"));
$("calibrationBtn").onclick = async () => renderSide(await getJSON("/forecasts/calibration-profile"));
$("createForecastBtn").onclick = async () => {
  $("forecastStatus").textContent = "Creating forecast...";
  try {
    const data = await postJSON("/forecasts", {
      raw_question: $("forecastQuestion").value,
      domain: $("forecastDomain").value,
      deadline: $("forecastDeadline").value,
      success_condition: $("forecastSuccess").value,
      user_initial_probability: Number($("forecastProbability").value),
      available_evidence: ["operator-provided structured forecast evidence"],
      factors: JSON.parse($("forecastFactors").value || "[]"),
      risks: JSON.parse($("forecastRisks").value || "[]")
    });
    $("forecastStatus").textContent = `Saved ${data.forecast_id}`;
    $("result").textContent = data.report;
    setMetrics({
      risk_level: data.risk_summary.total_risk_score >= 2 ? "high" : "medium",
      data_class: data.domain,
      local_cloud_decision: "local deterministic engine",
      cost_estimated: 0
    });
    renderSide(data);
  } catch (e) {
    $("forecastStatus").textContent = "Blocked/Error";
    $("result").textContent = e.message;
  }
};
