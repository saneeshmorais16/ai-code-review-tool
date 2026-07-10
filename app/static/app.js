const codeInput = document.querySelector("#codeInput");
const filePathInput = document.querySelector("#filePath");
const fileInput = document.querySelector("#fileInput");
const reviewButton = document.querySelector("#reviewButton");
const statusNode = document.querySelector("#status");
const summaryNode = document.querySelector("#summary");
const issuesNode = document.querySelector("#issues");

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  filePathInput.value = file.name;
  codeInput.value = await file.text();
});

reviewButton.addEventListener("click", async () => {
  statusNode.textContent = "Reviewing";
  summaryNode.innerHTML = "";
  issuesNode.innerHTML = "";

  const response = await fetch("/review/code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      code: codeInput.value,
      file_path: filePathInput.value || "snippet.txt",
    }),
  });

  if (!response.ok) {
    statusNode.textContent = "Review failed";
    issuesNode.textContent = await response.text();
    return;
  }

  const result = await response.json();
  statusNode.textContent = `Review #${result.id}`;
  renderSummary(result.summary);
  renderIssues(result.issues);
});

function renderSummary(summary) {
  summaryNode.innerHTML = `
    <div class="metric"><span>Files</span><strong>${summary.files_reviewed}</strong></div>
    <div class="metric"><span>Issues</span><strong>${summary.issue_count}</strong></div>
    <div class="metric"><span>Critical</span><strong>${summary.by_severity.critical || 0}</strong></div>
  `;
}

function renderIssues(issues) {
  if (issues.length === 0) {
    issuesNode.innerHTML = '<div class="issue">No issues found by the static rules.</div>';
    return;
  }

  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  issues
    .sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9))
    .forEach((issue) => {
      const item = document.createElement("article");
      item.className = "issue";
      item.innerHTML = `
        <div class="issue-title">
          <span>${issue.issue_type.replaceAll("_", " ")}</span>
          <span class="severity ${issue.severity}">${issue.severity}</span>
        </div>
        <div class="meta">${issue.category} · ${issue.file_path}${issue.line_number ? `:${issue.line_number}` : ""}</div>
        <p>${issue.explanation}</p>
        <div class="fix"><strong>Suggested fix:</strong> ${issue.suggested_fix}</div>
      `;
      issuesNode.appendChild(item);
    });
}
