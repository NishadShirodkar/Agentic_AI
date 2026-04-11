const form = document.getElementById("research-form");
const queryInput = document.getElementById("query");
const submitBtn = document.getElementById("submit-btn");
const statusBox = document.getElementById("status");
const resultsPanel = document.getElementById("results");

const shortAnswerEl = document.getElementById("short-answer");
const findingsEl = document.getElementById("key-findings");
const sourcesEl = document.getElementById("sources");
const confidenceEl = document.getElementById("confidence");
const sourceCountEl = document.getElementById("source-count");
const planStepsEl = document.getElementById("plan-steps");
const limitationsEl = document.getElementById("limitations");
const nextStepsEl = document.getElementById("next-steps");

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
      const a = document.createElement("a");
      a.href = item;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = item;
      li.appendChild(a);
    } else {
      li.textContent = item;
    }

    container.appendChild(li);
  }
}

function renderResult(response) {
  const result = response.result || {};

  shortAnswerEl.textContent = result.short_answer || "No short answer generated.";
  confidenceEl.textContent = `Confidence: ${result.confidence || "Unknown"}`;
  sourceCountEl.textContent = `Sources analyzed: ${response.source_count ?? 0}`;

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
  }
});
