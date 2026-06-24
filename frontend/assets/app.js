/* ===========================================================
   Resume Matcher — Single Page Application
   =========================================================== */

// ----- State -----
const state = {
  theme: localStorage.getItem("theme") || "light",
  results: [],
  parsedInfos: [],
  history: JSON.parse(localStorage.getItem("history") || "[]"),
  jdInput: "",
  lastSettings: JSON.parse(localStorage.getItem("lastSettings") || "{}"),
  currentResult: null,
};

function saveState() {
  localStorage.setItem("history", JSON.stringify(state.history));
  localStorage.setItem("lastSettings", JSON.stringify(state.lastSettings));
  localStorage.setItem("theme", state.theme);
}

// ----- API Client -----
const API = {
  async matchBatch(files, jd, weights) {
    const form = new FormData();
    for (const f of files) form.append("files", f);
    form.append("job_description", jd);
    form.append("text_weight", String(weights.text));
    form.append("skill_weight", String(weights.skill));
    form.append("experience_weight", String(weights.exp));
    const res = await fetch("/api/match-batch", { method: "POST", body: form });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    return res.json();
  },
  async listSkills() {
    const res = await fetch("/api/skills");
    return res.json();
  },
  async health() {
    const res = await fetch("/api/health");
    return res.json();
  },
};

// ----- Router -----
function navigate(hash) {
  const page = hash.replace("#", "") || "dashboard";
  document.querySelectorAll(".nav-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.page === page);
  });
  document.querySelectorAll(".page").forEach((el) => el.classList.remove("active"));
  const target = document.getElementById("page-" + page);
  if (target) {
    target.classList.add("active");
    const fn = renderers[page];
    if (fn) fn(target);
  }
}

window.addEventListener("hashchange", () => navigate(location.hash));
window.addEventListener("load", () => navigate(location.hash || "#dashboard"));

// ----- Toast -----
function toast(msg, type = "info") {
  const container = document.getElementById("toast-container");
  const el = document.createElement("div");
  el.className = "toast " + type;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity 0.3s"; setTimeout(() => el.remove(), 300); }, 3000);
}

// ----- Theme -----
function applyTheme() {
  document.documentElement.setAttribute("data-theme", state.theme);
  document.querySelector(".theme-toggle").textContent = state.theme === "dark" ? "\u25D0" : "\u25D1";
}
document.addEventListener("click", (e) => {
  const t = e.target.closest(".theme-toggle");
  if (t) {
    state.theme = state.theme === "dark" ? "light" : "dark";
    applyTheme();
    saveState();
  }
});
applyTheme();

// ----- Helpers -----
function esc(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function scoreBadge(val) {
  if (val >= 70) return '<span class="cell-badge high">High</span>';
  if (val >= 40) return '<span class="cell-badge med">Medium</span>';
  return '<span class="cell-badge low">Low</span>';
}

function skillTags(skillsStr, kind) {
  if (!skillsStr) return "";
  return skillsStr.split(",").map((s) => s.trim()).filter(Boolean).map((s) =>
    `<span class="skill-badge ${kind}">${esc(s)}</span>`
  ).join("");
}

function renderScoreCard(r) {
  const score = r["Final Score (%)"] || 0;
  return `
    <div class="score-card" data-candidate="${esc(r.Candidate)}">
      <div class="score-top">
        <div>
          <div class="candidate-name">${esc(r.Candidate)}</div>
          <div class="sub-scores">Text: ${r["Text Similarity (%)"]}% &middot; Skills: ${r["Skill Match (%)"]}% &middot; Exp: ${r["Experience Score (%)"]}%</div>
        </div>
        <div class="score-value">${score}%</div>
      </div>
      <div class="score-bar"><div class="score-bar-fill" style="width:${score}%"></div></div>
      <div style="margin-top:8px;display:flex;flex-wrap:wrap;">
        ${skillTags(r["Matched Skills"], "matched")}
        ${skillTags(r["Missing Skills"], "missing")}
      </div>
    </div>`;
}

function resultTableRows(results, showDetails = false) {
  return results.map((r) => {
    const score = r["Final Score (%)"] || 0;
    return `<tr>
      <td>${esc(r.Candidate)}</td>
      <td><div class="progress-cell"><div class="bar"><div class="fill" style="width:${score}%;background:var(--primary)"></div></div>${score}%</div></td>
      <td>${r["Text Similarity (%)"]}%</td>
      <td>${r["Skill Match (%)"]}%</td>
      <td>${r["Experience Score (%)"]}%</td>
      ${showDetails ? `<td>${skillTags(r["Matched Skills"], "matched")}</td><td>${skillTags(r["Missing Skills"], "missing")}</td>` : ""}
      <td>${scoreBadge(score)}</td>
    </tr>`;
  }).join("");
}

function downloadCSV(results, filename) {
  const headers = ["Candidate", "Final Score (%)", "Text Similarity (%)", "Skill Match (%)", "Experience Score (%)", "Matched Skills", "Missing Skills"];
  const rows = results.map((r) => headers.map((h) => `"${(r[h] || "").toString().replace(/"/g, '""')}"`).join(","));
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function renderMetric(label, value) {
  return `<div class="metric-card"><div class="metric-label">${esc(label)}</div><div class="metric-value">${esc(String(value))}</div></div>`;
}

// ----- Page Renderers -----
const renderers = {};

// ===== DASHBOARD =====
renderers.dashboard = function (container) {
  const allResults = [...state.results];
  for (const s of state.history) {
    if (s.results) allResults.push(...s.results);
  }

  const total = allResults.length;
  const sessions = state.history.length + (state.results.length > 0 ? 1 : 0);
  const avg = total ? (allResults.reduce((s, r) => s + (r["Final Score (%)"] || 0), 0) / total).toFixed(1) : 0;
  const top = total ? Math.max(...allResults.map((r) => r["Final Score (%)"] || 0)).toFixed(1) : 0;

  const allSkills = [];
  for (const r of allResults) {
    if (r["Matched Skills"]) allSkills.push(...r["Matched Skills"].split(",").map((s) => s.trim()).filter(Boolean));
  }
  const uniqueSkills = new Set(allSkills).size;

  if (!total) {
    container.innerHTML = `
      <div class="section-header">Dashboard</div>
      <div class="card" style="text-align:center;padding:48px 24px;">
        <div style="font-size:1.5em;font-weight:700;margin-bottom:8px;">Welcome to Resume Matcher</div>
        <div style="color:var(--text-secondary);margin-bottom:20px;max-width:480px;margin-left:auto;margin-right:auto;">
          Upload resumes, describe your ideal role, and let the system rank candidates by skill match, experience, and text similarity.
        </div>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
          <button class="btn btn-primary" onclick="location.hash='#matcher'">Get Started</button>
          <button class="btn" onclick="location.hash='#settings'">Configure Settings</button>
        </div>
      </div>`;
    return;
  }

  // Score distribution data for chart
  const scores = allResults.map((r) => r["Final Score (%)"] || 0);

  // Skill frequency
  const skillFreq = {};
  for (const s of allSkills) skillFreq[s] = (skillFreq[s] || 0) + 1;
  const topSkills = Object.entries(skillFreq).sort((a, b) => b[1] - a[1]).slice(0, 15);

  container.innerHTML = `
    <div class="section-header">Dashboard</div>
    <div class="metrics">
      ${renderMetric("Candidates Processed", total)}
      ${renderMetric("Matching Sessions", sessions)}
      ${renderMetric("Average Score", avg + "%")}
      ${renderMetric("Top Score", top + "%")}
    </div>
    <div class="quick-actions">
      <button class="btn btn-primary" onclick="location.hash='#matcher'">New Match</button>
      <button class="btn" onclick="location.hash='#compare'">Compare Candidates</button>
      <button class="btn" onclick="location.hash='#analytics'">View Analytics</button>
    </div>
    <div class="cols">
      <div class="card">
        <div class="card-header">Score Distribution</div>
        <div class="chart-container"><canvas id="dashboard-histogram"></canvas></div>
      </div>
      <div class="card">
        <div class="card-header">Most Common Skills</div>
        <div class="chart-container"><canvas id="dashboard-barchart"></canvas></div>
      </div>
    </div>
    <div id="dashboard-timeline"></div>`;

  // Render histogram
  setTimeout(() => {
    const bins = Array(10).fill(0);
    for (const s of scores) {
      const idx = Math.min(Math.floor(s / 10), 9);
      bins[idx]++;
    }
    new Chart(document.getElementById("dashboard-histogram"), {
      type: "bar",
      data: {
        labels: bins.map((_, i) => `${i * 10}-${(i + 1) * 10}%`),
        datasets: [{ data: bins, backgroundColor: getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#2563eb", borderRadius: 4 }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, grid: { color: "var(--border)" } }, x: { grid: { display: false } } } },
    });
  }, 0);

  // Render bar chart
  setTimeout(() => {
    new Chart(document.getElementById("dashboard-barchart"), {
      type: "bar",
      data: {
        labels: topSkills.map(([k]) => k).reverse(),
        datasets: [{ data: topSkills.map(([, v]) => v).reverse(), backgroundColor: getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#2563eb", borderRadius: 4 }],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { y: { grid: { display: false } }, x: { beginAtZero: true, grid: { color: "var(--border)" } } } },
    });
  }, 0);

  // Timeline
  const recent = state.history.slice(-8).reverse();
  if (recent.length) {
    let html = '<div class="card"><div class="card-header">Recent Sessions</div><div class="timeline">';
    for (const s of recent) {
      const ts = s.timestamp || "unknown";
      const jd = (s.job_description || "").slice(0, 70);
      const jdShort = jd.length > 70 ? jd + "..." : (jd || "(no description)");
      const count = (s.results || []).length;
      const topSc = s.results && s.results.length ? Math.max(...s.results.map((r) => r["Final Score (%)"] || 0)) : 0;
      html += `<div class="timeline-item" onclick="location.hash='#history'">
        <div class="tl-header"><span class="tl-title">${esc(jdShort)}</span><span class="tl-time">${esc(ts)}</span></div>
        <div class="tl-meta">${count} candidates &middot; top score: ${topSc}%</div>
      </div>`;
    }
    html += "</div></div>";
    document.getElementById("dashboard-timeline").innerHTML = html;
  }
};

// ===== MATCHER =====
renderers.matcher = function (container) {
  const ls = state.lastSettings;
  const defaultTW = ls.text_weight !== undefined ? ls.text_weight : 0.5;
  const defaultSW = ls.skill_weight !== undefined ? ls.skill_weight : 0.4;
  const defaultEW = ls.exp_weight !== undefined ? ls.exp_weight : 0.1;
  const defaultMode = ls.mode || "TF-IDF (Fast)";

  container.innerHTML = `
    <div class="section-header">Resume Matcher</div>
    <div style="display:grid;grid-template-columns:280px 1fr;gap:20px;">
      <div class="card" style="height:fit-content;position:sticky;top:32px;">
        <div class="card-header">Weights</div>
        <div class="range-group">
          <label>Scoring Mode
            <select id="matcher-mode">
              <option value="TF-IDF (Fast)" ${defaultMode === "TF-IDF (Fast)" ? "selected" : ""}>TF-IDF (Fast)</option>
              <option value="Semantic (Accurate)" ${defaultMode === "Semantic (Accurate)" ? "selected" : ""}>Semantic (Accurate)</option>
            </select>
          </label>
        </div>
        <div class="range-group">
          <label>Text Similarity <span id="matcher-tw-val">${defaultTW}</span></label>
          <input type="range" id="matcher-tw" min="0" max="1" step="0.05" value="${defaultTW}">
        </div>
        <div class="range-group">
          <label>Skill Match <span id="matcher-sw-val">${defaultSW}</span></label>
          <input type="range" id="matcher-sw" min="0" max="1" step="0.05" value="${defaultSW}">
        </div>
        <div class="range-group">
          <label>Experience <span id="matcher-ew-val">${defaultEW}</span></label>
          <input type="range" id="matcher-ew" min="0" max="1" step="0.05" value="${defaultEW}">
        </div>
        <hr style="border-color:var(--border);margin:12px 0;">
        <label style="display:flex;align-items:center;gap:8px;font-size:0.88em;cursor:pointer;">
          <input type="checkbox" id="matcher-parsed" checked> Show parsed info
        </label>
      </div>

      <div>
        <div class="tabs" id="matcher-tabs">
          <button class="tab active" data-tab="upload">Upload</button>
          <button class="tab" data-tab="results">Results</button>
          <button class="tab" data-tab="details">Details</button>
        </div>

        <div class="tab-content active" id="tab-upload">
          <div class="form-group">
            <label>Job Description</label>
            <textarea id="matcher-jd" placeholder="Paste the job description here...">${esc(state.jdInput)}</textarea>
          </div>
          <div class="form-group">
            <label>Resumes (PDF, DOCX)</label>
            <div class="file-upload" id="drop-zone">
              <div style="font-size:2em;margin-bottom:8px;">&#128206;</div>
              <div>Drop resumes here or click to browse</div>
              <input type="file" id="file-input" multiple accept=".pdf,.docx">
            </div>
            <div class="file-list" id="file-list"></div>
          </div>
          <button class="btn btn-primary" id="matcher-go" style="width:100%;">Analyse &amp; Rank</button>
          <div id="matcher-progress" style="display:none;margin-top:12px;">
            <div class="progress-bar"><div class="fill" id="matcher-progress-fill" style="width:0%"></div></div>
            <div style="font-size:0.85em;color:var(--text-secondary);text-align:center;" id="matcher-progress-text">Processing...</div>
          </div>
        </div>

        <div class="tab-content" id="tab-results">
          <div id="results-empty" class="info-box">No results yet. Go to the Upload tab and run a matching session.</div>
          <div id="results-content" style="display:none;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
              <span style="font-weight:700;" id="results-count"></span>
              <button class="btn btn-sm" id="results-download">Download CSV</button>
            </div>
            <div class="candidate-grid" id="results-cards"></div>
            <div class="table-wrap"><table><thead><tr>
              <th>Candidate</th><th>Score</th><th>Text</th><th>Skills</th><th>Exp</th><th>Matched</th><th>Missing</th><th>Status</th>
            </tr></thead><tbody id="results-table-body"></tbody></table></div>
          </div>
        </div>

        <div class="tab-content" id="tab-details">
          <div class="info-box">Select a candidate from the Results tab to see details here.</div>
          <div id="details-content" style="display:none;">
            <select id="detail-select" style="margin-bottom:16px;"></select>
            <div class="cols" id="detail-cols">
              <div class="card"><div class="chart-container"><canvas id="detail-radar"></canvas></div></div>
              <div class="card" id="detail-info"></div>
            </div>
            <div class="card" id="detail-skills"></div>
            <div class="card" id="detail-parsed" style="display:none;"></div>
          </div>
        </div>
      </div>
    </div>`;

  // Range sliders live update
  ["tw", "sw", "ew"].forEach((key) => {
    const el = document.getElementById("matcher-" + key);
    if (el) el.addEventListener("input", () => { document.getElementById("matcher-" + key + "-val").textContent = parseFloat(el.value).toFixed(2); });
  });

  // File upload
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const fileList = document.getElementById("file-list");
  let selectedFiles = [];

  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", (e) => { e.preventDefault(); dropZone.classList.remove("dragover"); handleFiles(e.dataTransfer.files); });
  fileInput.addEventListener("change", () => handleFiles(fileInput.files));

  function handleFiles(files) {
    for (const f of files) {
      if (!selectedFiles.find((x) => x.name === f.name && x.size === f.size)) {
        if (f.name.endsWith(".pdf") || f.name.endsWith(".docx")) selectedFiles.push(f);
        else toast(f.name + " is not a PDF or DOCX", "error");
      }
    }
    renderFileList();
  }

  function renderFileList() {
    fileList.innerHTML = selectedFiles.map((f, i) =>
      `<span class="file-tag">${esc(f.name)} <span class="remove" data-idx="${i}">&times;</span></span>`
    ).join("");
    fileList.querySelectorAll(".remove").forEach((el) => {
      el.addEventListener("click", () => { selectedFiles.splice(parseInt(el.dataset.idx), 1); renderFileList(); });
    });
  }

  // Tabs
  document.getElementById("matcher-tabs").addEventListener("click", (e) => {
    const tab = e.target.closest(".tab");
    if (!tab) return;
    document.querySelectorAll("#matcher-tabs .tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll("#tab-upload, #tab-results, #tab-details").forEach((t) => t.classList.remove("active"));
    document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
  });

  // Results tab data
  if (state.results.length) {
    showResults(state.results);
  }

  function showResults(results) {
    document.getElementById("results-empty").style.display = "none";
    document.getElementById("results-content").style.display = "block";
    document.getElementById("results-count").textContent = results.length + " Candidates Ranked";
    document.getElementById("results-cards").innerHTML = results.map(renderScoreCard).join("");

    // Click on card opens details
    document.querySelectorAll("#results-cards .score-card").forEach((el) => {
      el.addEventListener("click", () => {
        const name = el.dataset.candidate;
        const r = results.find((x) => x.Candidate === name);
        if (r) showDetails(r, results);
      });
    });

    document.getElementById("results-table-body").innerHTML = resultTableRows(results, true);
    document.getElementById("results-download").onclick = () => downloadCSV(results, "resume_ranking_results.csv");

    // Populate detail select
    const sel = document.getElementById("detail-select");
    sel.innerHTML = results.map((r) => `<option value="${esc(r.Candidate)}">${esc(r.Candidate)}</option>`).join("");
    sel.onchange = () => {
      const r = results.find((x) => x.Candidate === sel.value);
      if (r) showDetails(r, results);
    };
  }

  function showDetails(result, allResults) {
    document.getElementById("details-content").style.display = "block";
    document.getElementById("detail-select").value = result.Candidate;

    const infoHtml = `
      <div class="card-header">${esc(result.Candidate)}</div>
      <div style="margin-bottom:8px;">
        <div>Final Score: <strong>${result["Final Score (%)"]}%</strong></div>
        <div>Text Similarity: ${result["Text Similarity (%)"]}%</div>
        <div>Skill Match: ${result["Skill Match (%)"]}%</div>
        <div>Experience: ${result["Experience Score (%)"]}%</div>
      </div>
      <div style="margin-top:12px;">
        <div style="font-weight:600;margin-bottom:4px;">Matched</div>
        <div>${skillTags(result["Matched Skills"], "matched")}</div>
        <div style="font-weight:600;margin:8px 0 4px;">Missing</div>
        <div>${skillTags(result["Missing Skills"], "missing")}</div>
      </div>`;
    document.getElementById("detail-info").innerHTML = infoHtml;

    // Radar chart
    setTimeout(() => {
      const ctx = document.getElementById("detail-radar");
      if (window._detailRadar) window._detailRadar.destroy();
      window._detailRadar = new Chart(ctx, {
        type: "radar",
        data: {
          labels: ["Text Similarity", "Skill Match", "Experience"],
          datasets: [{
            data: [result["Text Similarity (%)"], result["Skill Match (%)"], result["Experience Score (%)"]],
            backgroundColor: "rgba(37,99,235,0.15)",
            borderColor: getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#2563eb",
            borderWidth: 2,
            pointBackgroundColor: getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#2563eb",
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 100, ticks: { stepSize: 20 } } },
          plugins: { legend: { display: false } } },
      });
    }, 0);

    // Matched/missing skills
    document.getElementById("detail-skills").innerHTML = `
      <div class="card-header">Skills</div>
      <div style="font-weight:600;color:var(--success);margin-bottom:4px;">Matched (${(result["Matched Skills"] || "").split(",").filter(Boolean).length})</div>
      <div style="margin-bottom:12px;">${skillTags(result["Matched Skills"], "matched")}</div>
      <div style="font-weight:600;color:var(--danger);margin-bottom:4px;">Missing (${(result["Missing Skills"] || "").split(",").filter(Boolean).length})</div>
      <div>${skillTags(result["Missing Skills"], "missing")}</div>`;

    // Parsed info
    const pi = state.parsedInfos[allResults.indexOf(result)];
    if (pi && (pi.email || pi.phone || pi.experience_years || (pi.degrees && pi.degrees.length))) {
      document.getElementById("detail-parsed").style.display = "block";
      let phtml = '<div class="card-header">Parsed Resume Info</div>';
      if (pi.email) phtml += `<div>Email: ${esc(pi.email)}</div>`;
      if (pi.phone) phtml += `<div>Phone: ${esc(pi.phone)}</div>`;
      if (pi.experience_years) phtml += `<div>Experience: ${esc(pi.experience_years)}+ years</div>`;
      if (pi.degrees && pi.degrees.length) phtml += `<div>Education: ${esc(pi.degrees.join(", "))}</div>`;
      document.getElementById("detail-parsed").innerHTML = phtml;
    }
  }

  // Analyse button
  document.getElementById("matcher-go").addEventListener("click", async () => {
    const jd = document.getElementById("matcher-jd").value.trim();
    if (!jd) { toast("Please paste a job description.", "error"); return; }
    if (!selectedFiles.length) { toast("Please upload at least one resume.", "error"); return; }

    const mode = document.getElementById("matcher-mode").value;
    const tw = parseFloat(document.getElementById("matcher-tw").value);
    const sw = parseFloat(document.getElementById("matcher-sw").value);
    const ew = parseFloat(document.getElementById("matcher-ew").value);
    const showParsed = document.getElementById("matcher-parsed").checked;

    const progress = document.getElementById("matcher-progress");
    const progressFill = document.getElementById("matcher-progress-fill");
    const progressText = document.getElementById("matcher-progress-text");
    progress.style.display = "block";

    try {
      progressText.textContent = "Uploading and processing resumes...";
      progressFill.style.width = "30%";

      const data = await API.matchBatch(selectedFiles, jd, { text: tw, skill: sw, exp: ew });
      progressFill.style.width = "80%";
      progressText.textContent = "Computing scores...";

      if (data.error) { toast(data.error, "error"); progress.style.display = "none"; return; }

      const results = (data.results || []).filter((r) => !r.error);
      if (!results.length) { toast("No resumes could be processed.", "error"); progress.style.display = "none"; return; }

      // Convert to display format
      state.results = results.map((r) => ({
        Candidate: r.filename || "Unknown",
        "Final Score (%)": r.final_score,
        "Text Similarity (%)": r.text_similarity,
        "Skill Match (%)": r.skill_score,
        "Experience Score (%)": r.experience_score,
        "Matched Skills": (r.matched_skills || []).join(", "),
        "Missing Skills": (r.missing_skills || []).join(", "),
      }));
      state.jdInput = jd;

      if (showParsed) {
        progressText.textContent = "Parsing resume info...";
        state.parsedInfos = results.map(() => ({}));
      }

      state.lastSettings = { text_weight: tw, skill_weight: sw, exp_weight: ew, mode };

      // Save to history
      const entry = {
        id: new Date().toISOString().replace(/[:.]/g, "-"),
        timestamp: new Date().toISOString(),
        job_description: jd,
        settings: state.lastSettings,
        results: JSON.parse(JSON.stringify(state.results)),
      };
      state.history.push(entry);
      saveState();

      progressFill.style.width = "100%";
      progressText.textContent = "Done!";
      toast(`Processed ${state.results.length} resumes successfully!`, "success");

      showResults(state.results);

      // Switch to results tab
      document.querySelectorAll("#matcher-tabs .tab").forEach((t) => t.classList.remove("active"));
      document.querySelector('[data-tab="results"]').classList.add("active");
      document.querySelectorAll("#tab-upload, #tab-results, #tab-details").forEach((t) => t.classList.remove("active"));
      document.getElementById("tab-results").classList.add("active");

    } catch (err) {
      toast(err.message || "Server error", "error");
    } finally {
      setTimeout(() => { progress.style.display = "none"; }, 1000);
    }
  });
};

// ===== COMPARE =====
renderers.compare = function (container) {
  const results = state.results;
  if (!results.length) {
    container.innerHTML = `<div class="section-header">Candidate Comparison</div><div class="info-box">No results available. Run a matching session first.</div>`;
    return;
  }

  container.innerHTML = `
    <div class="section-header">Candidate Comparison</div>
    <div class="form-group">
      <label>Select candidates to compare (max 5)</label>
      <select id="compare-select" multiple style="height:150px;">
        ${results.map((r) => `<option value="${esc(r.Candidate)}">${esc(r.Candidate)} (${r["Final Score (%)"]}%)</option>`).join("")}
      </select>
    </div>
    <div id="compare-content"></div>`;

  document.getElementById("compare-select").addEventListener("change", renderCompare);
  // Select first 3 by default
  const sel = document.getElementById("compare-select");
  for (let i = 0; i < Math.min(3, sel.options.length); i++) sel.options[i].selected = true;
  renderCompare();

  function renderCompare() {
    const sel2 = document.getElementById("compare-select");
    const selected = Array.from(sel2.selectedOptions).map((o) => o.value);
    const container2 = document.getElementById("compare-content");
    if (!selected.length) { container2.innerHTML = '<div class="info-box">Select at least one candidate.</div>'; return; }

    const filtered = results.filter((r) => selected.includes(r.Candidate));

    let html = '<div class="card"><div class="card-header">Score Comparison</div><div class="chart-container"><canvas id="compare-radar"></canvas></div></div>';

    // Table
    html += `<div class="card"><div class="card-header">Detailed Comparison</div><div class="table-wrap"><table><thead><tr>
      <th>Candidate</th><th>Score</th><th>Text</th><th>Skills</th><th>Exp</th><th>Status</th>
    </tr></thead><tbody>${resultTableRows(filtered)}</tbody></table></div></div>`;

    // Skill matrix
    html += '<div class="card"><div class="card-header">Skill Matrix</div>';
    for (const r of filtered) {
      html += `<div style="margin-bottom:12px;"><strong>${esc(r.Candidate)}</strong><br>
        ${skillTags(r["Matched Skills"], "matched")} ${skillTags(r["Missing Skills"], "missing")}</div>`;
    }
    html += "</div>";

    container2.innerHTML = html;

    // Radar chart
    setTimeout(() => {
      const ctx = document.getElementById("compare-radar");
      if (window._compareRadar) window._compareRadar.destroy();
      const colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#dc2626"];
      window._compareRadar = new Chart(ctx, {
        type: "radar",
        data: {
          labels: ["Text Similarity", "Skill Match", "Experience"],
          datasets: filtered.map((r, i) => ({
            label: r.Candidate,
            data: [r["Text Similarity (%)"], r["Skill Match (%)"], r["Experience Score (%)"]],
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + "22",
            borderWidth: 2,
            pointBackgroundColor: colors[i % colors.length],
          })),
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 100, ticks: { stepSize: 20 } } } },
      });
    }, 0);
  }
};

// ===== ANALYTICS =====
renderers.analytics = function (container) {
  const allResults = [...state.results];
  for (const s of state.history) {
    if (s.results) allResults.push(...s.results);
  }

  if (!allResults.length) {
    container.innerHTML = `<div class="section-header">Skills Analytics</div><div class="info-box">No data yet. Run a matching session first.</div>`;
    return;
  }

  const matched = [];
  const missing = [];
  const allSkills = [];

  for (const r of allResults) {
    const m = r["Matched Skills"] || "";
    const miss = r["Missing Skills"] || "";
    if (m) { const s = m.split(",").map((x) => x.trim()).filter(Boolean); matched.push(...s); allSkills.push(...s); }
    if (miss) { const s = miss.split(",").map((x) => x.trim()).filter(Boolean); missing.push(...s); allSkills.push(...s); }
  }

  const skillFreq = {};
  for (const s of allSkills) skillFreq[s] = (skillFreq[s] || 0) + 1;
  const sorted = Object.entries(skillFreq).sort((a, b) => b[1] - a[1]);

  const missingFreq = {};
  for (const s of missing) missingFreq[s] = (missingFreq[s] || 0) + 1;
  const sortedMissing = Object.entries(missingFreq).sort((a, b) => b[1] - a[1]).slice(0, 10);

  const catMap = {
    "Languages": ["python","java","javascript","typescript","c++","rust","golang","ruby","php","swift","kotlin","scala","r","matlab"],
    "Frontend": ["react","angular","vue","svelte","html","css","jquery","bootstrap","tailwind"],
    "Backend": ["django","flask","fastapi","spring","node.js","nodejs","express","dotnet","rails","laravel"],
    "Databases": ["sql","mysql","postgresql","mongodb","redis","elasticsearch","cassandra","sqlite","oracle"],
    "Cloud & DevOps": ["aws","azure","gcp","docker","kubernetes","terraform","jenkins","git","github actions","ci/cd"],
    "Data & ML": ["pytorch","tensorflow","scikit-learn","pandas","numpy","machine learning","deep learning","nlp","llm"],
  };
  const catDist = {};
  let otherCount = 0;
  for (const [s, c] of sorted) {
    let found = false;
    for (const [cat, skills] of Object.entries(catMap)) {
      if (skills.includes(s.toLowerCase())) { catDist[cat] = (catDist[cat] || 0) + c; found = true; break; }
    }
    if (!found) otherCount += c;
  }
  if (otherCount) catDist["Other"] = otherCount;

  container.innerHTML = `
    <div class="section-header">Skills Analytics</div>
    <div class="metrics">
      ${renderMetric("Unique Skills Found", Object.keys(skillFreq).length)}
      ${renderMetric("Total Occurrences", allSkills.length)}
      ${renderMetric("Most Common", sorted.length ? sorted[0][0] + " (" + sorted[0][1] + ")" : "N/A")}
      ${renderMetric("Most Missing", sortedMissing.length ? sortedMissing[0][0] + " (" + sortedMissing[0][1] + ")" : "N/A")}
    </div>
    <div class="cols">
      <div class="card"><div class="card-header">Top Skills</div><div class="chart-container"><canvas id="ana-barchart"></canvas></div></div>
      <div class="card"><div class="card-header">Skills by Category</div><div class="chart-container"><canvas id="ana-pie"></canvas></div></div>
    </div>
    <div class="card"><div class="card-header">Most Missing Skills</div><div class="chart-container"><canvas id="ana-missing"></canvas></div></div>`;

  setTimeout(() => {
    const pColor = getComputedStyle(document.documentElement).getPropertyValue("--primary").trim() || "#2563eb";
    const top15 = sorted.slice(0, 15);
    new Chart(document.getElementById("ana-barchart"), {
      type: "bar", data: { labels: top15.map(([k]) => k).reverse(), datasets: [{ data: top15.map(([, v]) => v).reverse(), backgroundColor: pColor, borderRadius: 4 }] },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { display: false } }, x: { beginAtZero: true, grid: { color: "var(--border)" } } } },
    });

    const catEntries = Object.entries(catDist);
    const pieColors = ["#2563eb","#059669","#d97706","#7c3aed","#dc2626","#0891b2","#84cc16","#db2777"];
    new Chart(document.getElementById("ana-pie"), {
      type: "doughnut", data: { labels: catEntries.map(([k]) => k), datasets: [{ data: catEntries.map(([, v]) => v), backgroundColor: pieColors.slice(0, catEntries.length) }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } } },
    });

    if (sortedMissing.length) {
      new Chart(document.getElementById("ana-missing"), {
        type: "bar", data: { labels: sortedMissing.map(([k]) => k).reverse(), datasets: [{ data: sortedMissing.map(([, v]) => v).reverse(), backgroundColor: "#dc2626", borderRadius: 4 }] },
        options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { display: false } }, x: { beginAtZero: true, grid: { color: "var(--border)" } } } },
      });
    }
  }, 0);
};

// ===== HISTORY =====
renderers.history = function (container) {
  if (!state.history.length) {
    container.innerHTML = `<div class="section-header">History</div><div class="info-box">No previous sessions found.</div>`;
    return;
  }

  const searchBox = `
    <div class="section-header">History</div>
    <div class="form-group search-box">
      <input type="text" id="history-search" placeholder="Filter by job description...">
    </div>
    <div style="margin-bottom:16px;"><span id="history-count">${state.history.length}</span> sessions found
      <button class="btn btn-sm btn-danger" id="history-clear" style="float:right;">Clear All</button>
    </div>
    <div id="history-list"></div>`;
  container.innerHTML = searchBox;

  function renderList(filter) {
    const list = document.getElementById("history-list");
    let filtered = state.history;
    if (filter) filtered = state.history.filter((s) => (s.job_description || "").toLowerCase().includes(filter));

    if (!filtered.length) { list.innerHTML = '<div class="info-box">No matching sessions.</div>'; return; }

    let html = "";
    for (let i = filtered.length - 1; i >= 0; i--) {
      const s = filtered[i];
      const ts = s.timestamp || "unknown";
      const jd = (s.job_description || "").slice(0, 120);
      const jdShort = jd.length > 120 ? jd + "..." : (jd || "(no description)");
      const count = (s.results || []).length;
      const topSc = s.results && s.results.length ? Math.max(...s.results.map((r) => r["Final Score (%)"] || 0)) : 0;
      const settingsUsed = s.settings || {};

      html += `<div class="card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
          <div><strong>${esc(ts)}</strong> &mdash; ${esc(jdShort)}</div>
          <button class="btn btn-sm" data-history-idx="${i}" data-history-load>Load</button>
        </div>
        <div class="tl-meta" style="margin-bottom:8px;">${count} candidates, top score: ${topSc}%</div>
        <div style="font-size:0.82em;color:var(--text-secondary);margin-bottom:8px;">
          Weights: T=${settingsUsed.text_weight || 0.7}, S=${settingsUsed.skill_weight || 0.3}, E=${settingsUsed.exp_weight || 0.0} &middot; Mode: ${settingsUsed.mode || "TF-IDF"}
        </div>
        <div class="table-wrap"><table><thead><tr><th>Candidate</th><th>Score</th><th>Text</th><th>Skills</th><th>Exp</th><th>Status</th></tr></thead>
        <tbody>${resultTableRows(s.results || [])}</tbody></table></div>
        <button class="btn btn-sm" style="margin-top:8px;" data-history-csv="${i}">Download CSV</button>
      </div>`;
    }
    list.innerHTML = html;

    // CSV download
    list.querySelectorAll("[data-history-csv]").forEach((el) => {
      el.addEventListener("click", () => {
        const idx = parseInt(el.dataset.historyCsv);
        const s = filtered[idx];
        if (s && s.results) downloadCSV(s.results, `session_${(s.timestamp || "unknown").replace(/[:.]/g, "-")}.csv`);
      });
    });

    // Load session
    list.querySelectorAll("[data-history-load]").forEach((el) => {
      el.addEventListener("click", () => {
        const idx = parseInt(el.dataset.historyIdx);
        const s = filtered[idx];
        if (s && s.results) {
          state.results = JSON.parse(JSON.stringify(s.results));
          state.jdInput = s.job_description || "";
          toast("Session loaded. Go to Resume Matcher to view.", "success");
        }
      });
    });
  }

  document.getElementById("history-search").addEventListener("input", function () {
    renderList(this.value.toLowerCase());
  });
  document.getElementById("history-clear").addEventListener("click", () => {
    if (confirm("Clear all history?")) {
      state.history = [];
      saveState();
      toast("History cleared.", "info");
      renderers.history(container);
    }
  });

  renderList("");
};

// ===== SETTINGS =====
renderers.settings = function (container) {
  const ls = state.lastSettings;
  const defaultTW = ls.text_weight !== undefined ? ls.text_weight : 0.5;
  const defaultSW = ls.skill_weight !== undefined ? ls.skill_weight : 0.4;
  const defaultEW = ls.exp_weight !== undefined ? ls.exp_weight : 0.1;
  const defaultMode = ls.mode || "TF-IDF (Fast)";

  container.innerHTML = `
    <div class="section-header">Settings</div>
    <div class="cols">
      <div>
        <div class="card">
          <div class="card-header">Default Weights</div>
          <div class="range-group">
            <label>Text Similarity <span id="set-tw-val">${defaultTW}</span></label>
            <input type="range" id="set-tw" min="0" max="1" step="0.05" value="${defaultTW}">
          </div>
          <div class="range-group">
            <label>Skill Match <span id="set-sw-val">${defaultSW}</span></label>
            <input type="range" id="set-sw" min="0" max="1" step="0.05" value="${defaultSW}">
          </div>
          <div class="range-group">
            <label>Experience <span id="set-ew-val">${defaultEW}</span></label>
            <input type="range" id="set-ew" min="0" max="1" step="0.05" value="${defaultEW}">
          </div>
          <button class="btn btn-sm" id="set-save-weights">Save as Defaults</button>
        </div>

        <div class="card">
          <div class="card-header">Appearance</div>
          <button class="btn" id="set-toggle-theme">Switch to ${state.theme === "dark" ? "Light" : "Dark"} Mode</button>
        </div>

        <div class="card">
          <div class="card-header">Scoring Mode</div>
          <select id="set-mode">
            <option value="TF-IDF (Fast)" ${defaultMode === "TF-IDF (Fast)" ? "selected" : ""}>TF-IDF (Fast)</option>
            <option value="Semantic (Accurate)" ${defaultMode === "Semantic (Accurate)" ? "selected" : ""}>Semantic (Accurate)</option>
          </select>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-header">Data Management</div>
          <div style="margin-bottom:12px;">
            <strong>History:</strong> ${state.history.length} sessions, ${state.history.reduce((s, h) => s + (h.results || []).length, 0)} total candidates
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <button class="btn btn-sm" id="set-export">Export All Data</button>
            <button class="btn btn-sm btn-danger" id="set-clear">Clear All History</button>
          </div>
        </div>

        <div class="card">
          <div class="card-header">Skills Database</div>
          <div id="skills-info">Loading...</div>
          <div id="skills-categories" style="margin-top:12px;"></div>
        </div>

        <div class="card">
          <div class="card-header">About</div>
          <div style="font-size:0.9em;color:var(--text-secondary);">
            <strong>Resume Matcher</strong><br>
            Version 2.0<br>
            NLP engine: ${defaultMode}<br>
            <span id="skills-count-about"></span>
          </div>
        </div>
      </div>
    </div>`;

  ["tw", "sw", "ew"].forEach((key) => {
    const el = document.getElementById("set-" + key);
    if (el) el.addEventListener("input", () => { document.getElementById("set-" + key + "-val").textContent = parseFloat(el.value).toFixed(2); });
  });

  document.getElementById("set-save-weights").addEventListener("click", () => {
    state.lastSettings.text_weight = parseFloat(document.getElementById("set-tw").value);
    state.lastSettings.skill_weight = parseFloat(document.getElementById("set-sw").value);
    state.lastSettings.exp_weight = parseFloat(document.getElementById("set-ew").value);
    state.lastSettings.mode = document.getElementById("set-mode").value;
    saveState();
    toast("Defaults saved.", "success");
  });

  document.getElementById("set-toggle-theme").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    applyTheme();
    saveState();
    renderers.settings(container);
  });

  document.getElementById("set-clear").addEventListener("click", () => {
    if (confirm("Clear all history?")) {
      state.history = [];
      saveState();
      toast("History cleared.", "info");
      renderers.settings(container);
    }
  });

  document.getElementById("set-export").addEventListener("click", () => {
    const all = [];
    for (const s of state.history) {
      for (const r of (s.results || [])) {
        all.push({ session_timestamp: s.timestamp, session_id: s.id, ...r });
      }
    }
    if (all.length) downloadCSV(all, "all_history.csv");
    else toast("No data to export.", "info");
  });

  // Load skills
  API.listSkills().then((data) => {
    document.getElementById("skills-info").textContent = `${data.count || 0} skills loaded`;
    document.getElementById("skills-count-about").textContent = `${data.count || 0} skills`;
  }).catch(() => {
    document.getElementById("skills-info").textContent = "Failed to load skills";
  });
};
