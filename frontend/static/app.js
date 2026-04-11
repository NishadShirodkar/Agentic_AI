const form = document.getElementById("research-form");
const queryInput = document.getElementById("query");
const submitBtn = document.getElementById("submit-btn");
const statusBox = document.getElementById("status");
const resultsPanel = document.getElementById("results");
const loadingStepper = document.getElementById("loading-stepper");

const shortAnswerEl = document.getElementById("short-answer");
const findingsEl = document.getElementById("key-findings");
const sourcesEl = document.getElementById("sources");
const confidenceEl = document.getElementById("confidence");
const sourceCountEl = document.getElementById("source-count");
const planStepsEl = document.getElementById("plan-steps");
const limitationsEl = document.getElementById("limitations");
const nextStepsEl = document.getElementById("next-steps");
const sourceCountSummaryEl = document.getElementById("source-count-summary");
const findingsCountSummaryEl = document.getElementById("findings-count-summary");
const confidenceSummaryEl = document.getElementById("confidence-summary");

const loadingSteps = Array.from(document.querySelectorAll(".loading-stepper .step"));

function showStatus(message, isError = false) {
  statusBox.classList.remove("hidden", "error");
  statusBox.textContent = message;
  if (isError) {
    statusBox.classList.add("error");
  }
}

function clearStatus() {
  statusBox.classList.add("hidden");
  statusBox.classList.remove("error");
  statusBox.textContent = "";
}

function formatDomain(value) {
  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return value;
  }
}

function renderList(container, items, isLink = false) {
  container.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No data available.";
    container.appendChild(li);
    return;
  }

  for (const item of items) {
    const li = document.createElement("li");

    if (isLink) {
      const domain = formatDomain(item);

      const domainBadge = document.createElement("span");
      domainBadge.className = "source-domain";
      domainBadge.textContent = domain;

      const a = document.createElement("a");
      a.href = item;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = item;
      a.className = "source-link";

      li.appendChild(domainBadge);
      li.appendChild(a);
    } else {
      li.textContent = item;
    }

    container.appendChild(li);
  }
}

function setLoadingState(isLoading) {
  loadingStepper.classList.toggle("hidden", !isLoading);

  if (isLoading) {
    loadingSteps.forEach((step, index) => {
      step.classList.toggle("active", index === 0);
    });
  }
}

function cycleLoadingSteps() {
  let activeIndex = 0;

  loadingSteps.forEach((step, index) => {
    step.classList.toggle("active", index === activeIndex);
  });

  const timer = window.setInterval(() => {
    activeIndex = Math.min(activeIndex + 1, loadingSteps.length - 1);

    loadingSteps.forEach((step, index) => {
      step.classList.toggle("active", index === activeIndex);
    });

    if (activeIndex >= loadingSteps.length - 1) {
      window.clearInterval(timer);
    }
  }, 900);

  return timer;
}

function renderResult(response) {
  const result = response.result || {};
  const findingsCount = Array.isArray(result.key_findings) ? result.key_findings.length : 0;

  shortAnswerEl.textContent = result.short_answer || "No short answer generated.";
  confidenceEl.textContent = `Confidence: ${result.confidence || "Unknown"}`;
  sourceCountEl.textContent = `Sources analyzed: ${response.source_count ?? 0}`;
  sourceCountSummaryEl.textContent = `${response.source_count ?? 0}`;
  findingsCountSummaryEl.textContent = `${findingsCount}`;
  confidenceSummaryEl.textContent = result.confidence || "Unknown";

  renderList(findingsEl, result.key_findings || []);
  renderList(sourcesEl, result.sources || [], true);
  renderList(planStepsEl, response.plan?.steps || []);
  renderList(limitationsEl, result.limitations || []);
  renderList(nextStepsEl, result.next_steps || []);

  resultsPanel.classList.remove("hidden");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();

  if (!query) {
    showStatus("Please enter a research query.", true);
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";
  clearStatus();
  showStatus("Running planner, executor, and synthesizer...");
  setLoadingState(true);
  const loadingTimer = cycleLoadingSteps();

  try {
    const response = await fetch("/api/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Failed to run analysis.");
    }

    renderResult(payload);
    showStatus("Analysis complete.");
  } catch (error) {
    showStatus(error.message || "Unexpected error while analyzing query.", true);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Run Analysis";
    window.clearInterval(loadingTimer);
    setLoadingState(false);
  }
});
