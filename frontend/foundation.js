const foundationData = {
  local: {
    Netherlands: {
      "Den Haag": {
        signal: "Public institutions are translating AI accountability into procurement and service rules.",
        policy: "Monitor Dutch public-sector AI registers and EU implementation guidance.",
        opportunity: "Connect local research, municipalities and civic literacy groups around transparent deployment."
      },
      Amsterdam: {
        signal: "Urban innovation networks are testing accountable data and AI uses in public services.",
        policy: "Track municipal algorithm transparency and public participation requirements.",
        opportunity: "Build bridges between applied AI teams and community oversight."
      }
    },
    Belgium: {
      Brussels: {
        signal: "European governance decisions move quickly from policy discussion to institutional impact.",
        policy: "Follow EU institutional briefings and national transposition decisions.",
        opportunity: "Coordinate policy literacy with research and civil society networks."
      }
    },
    Germany: {
      Berlin: {
        signal: "Industrial AI adoption is increasing attention on compliance, energy and worker impact.",
        policy: "Observe deployment standards and labor participation frameworks.",
        opportunity: "Link applied research with accountable implementation projects."
      }
    }
  },
  sources: [
    { source: "European Commission", position: "Implementation guidance", strength: "High", divergence: "Low" },
    { source: "Public research institute", position: "Impact analysis", strength: "Medium", divergence: "Moderate" },
    { source: "Industry consortium", position: "Adoption readiness", strength: "Medium", divergence: "High" },
    { source: "Civil society review", position: "Rights and oversight", strength: "Medium", divergence: "Moderate" }
  ],
  signals: [
    {
      category: "AI & Society", title: "Institutions are moving from AI pilots to accountable operating rules",
      summary: "Public and professional organizations increasingly need audit, approval and explanation layers rather than isolated AI experiments.",
      context: "AI is becoming workflow infrastructure.",
      matters: "Operational responsibility must remain visible.",
      confidence: "High", relevant: "Institutions", orientation: "Track governance mechanisms, not capability headlines."
    },
    {
      category: "Europe & Governance", title: "Digital sovereignty is becoming practical procurement architecture",
      summary: "European initiatives increasingly connect data control, model choice and public accountability.",
      context: "Trust is shifting into infrastructure.",
      matters: "Procurement rules shape future autonomy.",
      confidence: "Medium", relevant: "Europe", orientation: "Compare declared policy with deployed requirements."
    },
    {
      category: "Human Sustainability", title: "Attention quality is now a coordination constraint",
      summary: "Teams and citizens face too much information with too little context for responsible decisions.",
      context: "More content does not create orientation.",
      matters: "Cognitive overload weakens judgment.",
      confidence: "High", relevant: "Citizens", orientation: "Choose contextual signals over high-volume feeds."
    }
  ]
};

function qs(selector) { return document.querySelector(selector); }
function qsa(selector) { return [...document.querySelectorAll(selector)]; }
function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[character]));
}
function safeArticleLink(value) {
  return /^\/jazekker\/articles\/[a-z0-9-]+$/i.test(String(value ?? ""))
    ? value
    : "/jazekker/orientation";
}

function bindModeButtons() {
  qsa("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      qsa("[data-mode]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      const status = qs("#modeStatus");
      if (status) status.textContent = `${button.dataset.mode} mode: signal density adjusted without engagement ranking.`;
      const localMode = qs("#localMode");
      if (localMode) localMode.textContent = `${button.dataset.mode} mode`;
    });
  });
}

function renderFallbackSignals() {
  const stream = qs("#orientationStream");
  if (!stream) return;
  stream.innerHTML = foundationData.signals.map((signal) => `
    <article class="orientation-card">
      <div class="card-meta"><span class="pill">${safeText(signal.category)}</span><span class="pill confidence">Confidence ${safeText(signal.confidence)}</span><span class="pill risk">Reviewed locally</span></div>
      <h2>${safeText(signal.title)}</h2>
      <p class="summary">${safeText(signal.summary)}</p>
      <div class="object-fields">
        <div class="object-field"><label>Context</label><div>${safeText(signal.context)}</div></div>
        <div class="object-field"><label>Why it matters</label><div>${safeText(signal.matters)}</div></div>
        <div class="object-field"><label>Orientation</label><div>${safeText(signal.orientation)}</div></div>
      </div>
      <div class="card-actions"><button class="icon-btn save-signal" type="button" aria-pressed="false">Save</button><a class="icon-btn btn" href="/jazekker/research">Open Research</a><a class="icon-btn btn" href="/jazekker/ai-cabinet">Discuss with Agent</a><a class="icon-btn btn" href="/jazekker/research?view=contradictions">Compare Narratives</a></div>
    </article>
  `).join("");
  bindStreamActions();
}

async function loadOrientationArticles() {
  const stream = qs("#orientationStream");
  if (!stream) return;
  try {
    const response = await fetch("/jazekker/articles");
    const data = await response.json();
    if (!response.ok || !data.articles?.length) throw new Error("No article data");
    stream.innerHTML = data.articles.slice(0, 5).map((item) => `
      <article class="orientation-card">
        <div class="card-meta"><span class="pill">${safeText(item.category_label || "Signal")}</span><span class="pill confidence">Confidence ${safeText(item.confidence_level || "medium")}</span><span class="pill risk">Orientation ${safeText(item.orientation_score || "review")}</span></div>
        <h2>${safeText(item.title)}</h2>
        <p class="summary">${safeText(item.dek || "")}</p>
        <div class="object-fields">
          <div class="object-field"><label>Context</label><div>${safeText(item.orientation_lens || "Contextual review required.")}</div></div>
          <div class="object-field"><label>Relevant for</label><div>${safeText(item.category_label || "Civic orientation")}</div></div>
          <div class="object-field"><label>Orientation</label><div>${safeText(item.next_orientation_step || "Read source context.")}</div></div>
        </div>
        <div class="card-actions"><button class="icon-btn save-signal" type="button" aria-pressed="false">Save</button><a class="icon-btn btn" href="/jazekker/research">Open Research</a><a class="icon-btn btn" href="/jazekker/ai-cabinet">Discuss with Agent</a><a class="icon-btn btn" href="/jazekker/research?view=contradictions">Compare Narratives</a><a class="icon-btn btn" href="${safeArticleLink(item.url)}">Read</a></div>
      </article>
    `).join("");
    bindStreamActions();
  } catch (error) {
    renderFallbackSignals();
  }
}

function bindStreamActions() {
  qsa(".save-signal").forEach((button) => button.addEventListener("click", () => {
    const isSaved = button.getAttribute("aria-pressed") === "true";
    button.setAttribute("aria-pressed", String(!isSaved));
    button.textContent = isSaved ? "Save" : "Saved";
    button.classList.toggle("active", !isSaved);
  }));
  const search = qs("#orientationSearch");
  if (search && !search.dataset.bound) {
    search.dataset.bound = "true";
    search.addEventListener("input", () => {
      const query = search.value.trim().toLowerCase();
      let shown = 0;
      qsa(".orientation-card").forEach((card) => {
        const visible = !query || card.textContent.toLowerCase().includes(query);
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      const status = qs("#modeStatus");
      if (status && query) status.textContent = `${shown} orientation object(s) match "${search.value.trim()}".`;
      if (status && !query) {
        const activeMode = qs("[data-mode].active")?.dataset.mode || "Calm";
        status.textContent = `${activeMode} mode: signal density adjusted without engagement ranking.`;
      }
    });
  }
}

function localOrientation() {
  const country = qs("#country");
  const city = qs("#city");
  const domain = qs("#domain");
  if (!country || !city) return;
  function availableCities() {
    const cities = Object.keys(foundationData.local[country.value]);
    city.innerHTML = cities.map((name) => `<option>${name}</option>`).join("");
  }
  function updateBrief() {
    const record = foundationData.local[country.value][city.value];
    qs("#briefLocation").textContent = `${city.value}, ${country.value}`;
    qs("#localSignal").textContent = record.signal;
    qs("#localPolicy").textContent = record.policy;
    qs("#localOpportunity").textContent = record.opportunity;
    const choices = qsa(".toggle.selected").map((item) => item.textContent).join(", ");
    const focus = choices || "General orientation";
    qs("#localContext").textContent = domain ? `${focus} | ${domain.value}` : focus;
  }
  country.addEventListener("change", () => { availableCities(); updateBrief(); });
  city.addEventListener("change", updateBrief);
  if (domain) domain.addEventListener("change", updateBrief);
  qsa(".toggle").forEach((button) => button.addEventListener("click", () => { button.classList.toggle("selected"); updateBrief(); }));
  availableCities();
  updateBrief();
}

function researchDesk() {
  const body = qs("#sourceRows");
  if (!body) return;
  body.innerHTML = foundationData.sources.map((row) => `
    <tr><td>${row.source}</td><td>${row.position}</td><td>${row.strength}</td><td>${row.divergence}</td></tr>
  `).join("");
  qsa("[data-research]").forEach((button) => button.addEventListener("click", () => {
    qsa("[data-research]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    qs("#researchStatus").textContent = `${button.dataset.research}: evidence view prepared. Contradictions remain visible.`;
  }));
  const query = new URLSearchParams(window.location.search);
  if (query.get("view") === "contradictions") {
    const divergence = qs('[data-research="Narrative divergence"]');
    if (divergence) divergence.click();
    qsa(".graph .node").forEach((node) => node.classList.toggle("active", node.textContent === "Contradiction"));
  }
  const exportButton = qs("#exportPreview");
  if (exportButton) exportButton.addEventListener("click", () => {
    const topic = qs("#researchStatus").textContent;
    const sourceLines = foundationData.sources.map((row) =>
      `${row.source} | ${row.position} | evidence ${row.strength} | divergence ${row.divergence}`
    ).join("\n");
    const exportText = `JAZEKKER Research Desk Preview\n\n${topic}\n\nSources\n${sourceLines}\n\nExported as orientation preview; human review required before publication.\n`;
    const file = new Blob([exportText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "jazekker-research-preview.txt";
    link.click();
    URL.revokeObjectURL(link.href);
    exportButton.textContent = "Exported";
  });
}

function runtimeDemo() {
  const run = qs("#runWorkflow");
  if (!run) return;
  run.addEventListener("click", () => {
    qsa(".node").forEach((item) => item.classList.add("active"));
    qs("#workflowResult").textContent = "Draft ready for human review. No external action executed.";
    qs("#workflowResult").classList.remove("muted");
  });
}

function testboxPreview() {
  const simulate = qs("#simulateRoute");
  if (!simulate) return;
  simulate.addEventListener("click", () => {
    qs("#simulationState").textContent = "Simulation captured: route selected, policy applied, approval required, audit recorded.";
    qsa(".event").forEach((item) => item.classList.remove("hide"));
  });
}

let activeEvolutionProposalId = "";

function privilegedRuntimeHeaders() {
  const token = window.sessionStorage.getItem("astreb.admin_token");
  return token ? { "X-AI-Cabinet-Admin-Token": token } : {};
}

function renderEvolutionProposal(proposal) {
  const target = qs("#metaQmsProposal");
  if (!target || !proposal) return;
  activeEvolutionProposalId = proposal.id;
  target.innerHTML = `
    <div class="proposal-data">
      <div><strong>Deviation</strong><span>${safeText(proposal.deviation_category)}</span></div>
      <div><strong>Improvement</strong><span>${safeText(proposal.proposed_improvement)}</span></div>
      <div><strong>Acceptance condition</strong><span>${safeText(proposal.acceptance_condition)}</span></div>
      <div><strong>Status</strong><span>${safeText(proposal.status)}</span></div>
    </div>`;
  const pending = proposal.status === "review_required";
  qs("#approveEvolution").disabled = !pending;
  qs("#rejectEvolution").disabled = !pending;
}

function metaQmsPreview() {
  const review = qs("#runMetaQmsReview");
  if (!review) return;
  const status = qs("#metaQmsStatus");
  const result = qs("#metaQmsResult");
  const decisionButtons = [
    [qs("#approveEvolution"), "approve"],
    [qs("#rejectEvolution"), "reject"]
  ];
  review.addEventListener("click", async () => {
    review.disabled = true;
    status.textContent = "assessing";
    try {
      const response = await fetch("/api/testbox/runtime/meta-qms/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...privilegedRuntimeHeaders() },
        body: JSON.stringify({
          user_session: "jazekker-foundation-demo",
          role: "Governance Officer",
          trigger: "orientation_signal_review",
          observation: "A signal card communicates relevance while source provenance is incomplete.",
          deviation_category: "trust_visibility_gap",
          affected_layers: ["Orientation Layer", "Governance Layer", "Audit Layer", "Learning Layer", "Evolution Layer"],
          risk_level: "medium",
          evidence: ["TESTBOX visual review: confidence is visible; provenance requires explicit verification."],
          proposed_improvement: "Require provenance status and review timestamp before any signal is eligible for publication.",
          acceptance_condition: "A regression check verifies provenance and review timestamp on each publishable orientation object."
        })
      });
      if (!response.ok) throw new Error("assessment_unavailable");
      const payload = await response.json();
      renderEvolutionProposal(payload.proposal);
      status.textContent = "human review required";
      result.textContent = "Deviation recorded. An improvement proposal is awaiting human decision.";
    } catch (error) {
      status.textContent = "runtime unavailable";
      result.textContent = "Quality review could not reach the local runtime. No proposal was assumed.";
    } finally {
      review.disabled = false;
    }
  });
  decisionButtons.forEach(([button, decision]) => button.addEventListener("click", async () => {
    if (!activeEvolutionProposalId) return;
    button.disabled = true;
    try {
      const response = await fetch(`/api/testbox/runtime/meta-qms/proposals/${activeEvolutionProposalId}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...privilegedRuntimeHeaders() },
        body: JSON.stringify({
          user_session: "jazekker-foundation-demo",
          role: "Governance Officer",
          decision,
          reason: decision === "approve"
            ? "Accept for separately governed implementation and regression verification."
            : "Proposal requires revision before implementation planning."
        })
      });
      if (!response.ok) throw new Error("decision_unavailable");
      const payload = await response.json();
      renderEvolutionProposal(payload.proposal);
      status.textContent = decision === "approve" ? "approved, not executed" : "rejected";
      result.textContent = decision === "approve"
        ? "Human approval recorded. No system change has been executed."
        : "Human rejection recorded. The proposal remains in audit evidence.";
    } catch (error) {
      status.textContent = "decision failed";
      result.textContent = "Decision was not recorded; review state remains unchanged.";
    }
  }));
}

document.addEventListener("DOMContentLoaded", () => {
  bindModeButtons();
  loadOrientationArticles();
  localOrientation();
  researchDesk();
  runtimeDemo();
  testboxPreview();
  metaQmsPreview();
});
