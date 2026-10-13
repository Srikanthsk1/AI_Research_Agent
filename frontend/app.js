const form = document.querySelector("#research-form");
const submitButton = document.querySelector("#submit-button");
const errorBox = document.querySelector("#form-error");
const runPanel = document.querySelector("#run-panel");
const runHeading = document.querySelector("#run-status");
const runMessage = document.querySelector("#run-message");
const runIndicator = document.querySelector("#run-indicator");
const runStateLabel = document.querySelector("#run-state-label");
const progressTrack = document.querySelector(".progress-track");
const progressBar = document.querySelector("#progress-bar");
const resultArea = document.querySelector("#result-area");
const reportOutput = document.querySelector("#report-output");
const downloadButton = document.querySelector("#download-pdf");
const newRunButton = document.querySelector("#new-run");

let activePdfUrl = null;
const docsLink = document.querySelector(".workspace-footer a");

function apiBase() {
  return document.querySelector("#api-url").value.trim().replace(/\/+$/, "");
}

function updateDocsLink() {
  try { docsLink.href = new URL("/docs", apiBase()).href; } catch { /* Keep default docs link while editing. */ }
}

function authHeaders(json = false) {
  const headers = {};
  if (json) headers["Content-Type"] = "application/json";
  const apiKey = document.querySelector("#api-key").value.trim();
  if (apiKey) headers.Authorization = `Bearer ${apiKey}`;
  return headers;
}

async function readResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : `Request failed (${response.status}).`;
    throw new Error(detail);
  }
  return payload;
}

function setStatus(status, message) {
  const labels = { queued: "QUEUED", running: "IN PROGRESS", completed: "COMPLETE", failed: "FAILED" };
  runStateLabel.textContent = labels[status] || status.toUpperCase();
  runHeading.textContent = status === "completed" ? "Your research is ready." : status === "failed" ? "This research run failed." : "Preparing your research…";
  runMessage.textContent = message;
  runIndicator.className = `run-indicator ${status === "failed" ? "is-failed" : status === "completed" ? "is-complete" : status === "running" ? "is-running" : ""}`;
  progressTrack.className = `progress-track ${status === "failed" ? "is-failed" : status === "completed" ? "is-complete" : status === "running" ? "is-running" : ""}`;
  progressBar.setAttribute("aria-valuenow", status === "completed" ? "100" : status === "running" ? "55" : "15");
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function inlineMarkdown(line) {
  let html = escapeHtml(line);
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (_match, label, url) => {
    const safeUrl = url.replace(/&amp;/g, "&");
    return `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noreferrer">${label}</a>`;
  });
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>");
  return html;
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const output = [];
  let paragraph = [];
  let listType = null;

  const flushParagraph = () => {
    if (paragraph.length) {
      output.push(`<p>${paragraph.map(inlineMarkdown).join(" ")}</p>`);
      paragraph = [];
    }
  };
  const closeList = () => {
    if (listType) output.push(`</${listType}>`);
    listType = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) { flushParagraph(); closeList(); continue; }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph(); closeList();
      const level = heading[1].length;
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }
    const item = line.match(/^([-*]|\d+\.)\s+(.+)$/);
    if (item) {
      flushParagraph();
      const type = item[1].endsWith(".") ? "ol" : "ul";
      if (listType !== type) { closeList(); listType = type; output.push(`<${type}>`); }
      output.push(`<li>${inlineMarkdown(item[2])}</li>`);
      continue;
    }
    closeList();
    paragraph.push(line);
  }
  flushParagraph(); closeList();
  return output.join("");
}

function showResult(result) {
  const report = result.report;
  if (typeof report === "string") {
    reportOutput.innerHTML = renderMarkdown(report);
  } else {
    reportOutput.innerHTML = `<pre>${escapeHtml(JSON.stringify(report, null, 2))}</pre>`;
  }
  document.querySelector("#evidence-count").textContent = `${result.evidence_count} sources used`;
  document.querySelector("#output-label").textContent = result.output_format;
  activePdfUrl = result.pdf_url || null;
  downloadButton.hidden = !activePdfUrl;
  resultArea.hidden = false;
}

async function pollJob(statusUrl) {
  while (true) {
    const response = await fetch(statusUrl, { headers: authHeaders() });
    const job = await readResponse(response);

    if (job.status === "queued") {
      setStatus("queued", "Your question is waiting to start.");
    } else if (job.status === "running") {
      setStatus("running", "Searching sources and preparing your report. This can take a few minutes.");
    } else if (job.status === "completed") {
      setStatus("completed", "The report has finished. Review it below.");
      showResult(job.result);
      submitButton.disabled = false;
      return;
    } else if (job.status === "failed") {
      setStatus("failed", job.error || "The research workflow failed.");
      submitButton.disabled = false;
      return;
    }
    await new Promise((resolve) => window.setTimeout(resolve, 2200));
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  resultArea.hidden = true;
  runPanel.hidden = false;
  submitButton.disabled = true;
  setStatus("queued", "Submitting your question to the research agent.");

  const body = {
    query: document.querySelector("#query").value.trim(),
    research_depth: document.querySelector("#depth").value,
    output_format: document.querySelector("#format").value,
    max_sources: Number(document.querySelector("#sources").value),
    include_citations: document.querySelector("#citations").checked,
  };

  try {
    const response = await fetch(`${apiBase()}/research/jobs`, {
      method: "POST",
      headers: authHeaders(true),
      body: JSON.stringify(body),
    });
    const accepted = await readResponse(response);
    await pollJob(accepted.status_url);
  } catch (error) {
    setStatus("failed", error.message || "Could not connect to the API.");
    submitButton.disabled = false;
    errorBox.textContent = error.message || "Could not connect to the API. Check that it is running and CORS is configured.";
    errorBox.hidden = false;
  }
});

downloadButton.addEventListener("click", async () => {
  if (!activePdfUrl) return;
  downloadButton.disabled = true;
  const originalLabel = downloadButton.textContent;
  downloadButton.textContent = "Preparing PDF…";
  try {
    const response = await fetch(activePdfUrl, { headers: authHeaders() });
    if (!response.ok) throw new Error(`PDF download failed (${response.status}).`);
    const blobUrl = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = "research-report.pdf";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  } finally {
    downloadButton.disabled = false;
    downloadButton.textContent = originalLabel;
  }
});

newRunButton.addEventListener("click", () => {
  runPanel.hidden = true;
  document.querySelector("#query").focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

document.querySelector("#api-url").addEventListener("change", updateDocsLink);
