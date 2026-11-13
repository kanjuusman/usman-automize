/* Usman Automize PC Tool v2 - frontend (koi framework nahi) */
let STATE = null;

function showTab(name) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tabs button").forEach(b => b.classList.remove("active"));
  document.getElementById("tab-" + name).classList.add("active");
  document.querySelector(`.tabs button[data-tab="${name}"]`).classList.add("active");
  if (name === "timeline") renderTimeline();
  if (name === "upload") renderUpload();
}

async function api(path, body) {
  const r = await fetch(path, body ? {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  } : undefined);
  return r.json();
}

async function refresh() {
  const d = await api("/api/state");
  if (!d.ok) return;
  STATE = d.state;
  const p = STATE.project;
  document.getElementById("topic").value = p.topic || "";
  document.getElementById("title").value = p.title || "";
  document.getElementById("script").value = p.script || "";
  document.getElementById("targetWords").value = p.target_words || 500;
  // agents
  const list = document.getElementById("agentList");
  list.innerHTML = STATE.agents.map((a, i) => `
    <div class="agent">
      <div class="num">${i + 1}</div>
      <div class="body">
        <span class="name">${a.name}</span>
        <span class="badge ${a.status}" style="float:right">${a.status}</span>
        <div class="note">${a.job}</div>
        ${a.note ? `<div class="note">${a.note}</div>` : ""}
        ${a.checker_note ? `<div class="checker">✓ ${a.checker_note}</div>` : ""}
      </div>
      <button class="btn ghost" onclick="runAgent('${a.key}')">Chalao</button>
    </div>`).join("");
  const fq = STATE.final_qa || {};
  const badge = document.getElementById("qaBadge");
  badge.textContent = "Final QA: " + (fq.status || "pending");
  badge.className = "badge " + (fq.status || "pending");
  // issues
  const il = document.getElementById("issueList");
  il.innerHTML = STATE.issues.length ? STATE.issues.map(x => `
    <div class="issue"><b>${x.agent}: ${x.problem}</b><br>Hal: ${x.solution}</div>`).join("")
    : "<p class='small'>Koi masla nahi hai.</p>";
  // api keys
  document.getElementById("apiList").innerHTML = STATE.api_keys.length ? STATE.api_keys.map(k => `
    <div class="kv"><span><b>${k.provider}</b> (${k.tier}) — ${k.label || ""} ${k.note ? "• " + k.note : ""}</span>
    <span>${k.masked} <button class="btn ghost" onclick="delApi('${k.provider}')">Hatao</button></span></div>`).join("")
    : "<p class='small'>Abhi koi API nahi lagi. Neeche se pehla slot banao.</p>";
  const prov = document.getElementById("apiProvider");
  if (!prov.options.length) {
    prov.innerHTML = STATE.providers.map(p => `<option>${p}</option>`).join("");
  }
  // media
  const folders = {};
  STATE.media.forEach(m => { (folders[m.folder] = folders[m.folder] || []).push(m); });
  document.getElementById("mediaList").innerHTML = Object.entries(folders).map(([f, items]) => `
    <h3>${f}</h3>${items.map(m => `<div class="kv"><span>${m.has_file ? "📎" : "📝"} ${m.name}</span><span class="small">${m.note || ""}</span></div>`).join("")}`).join("");
  // status chips
  const chips = [];
  if (STATE.video_file) chips.push("🎥 Video tayyar: " + STATE.video_file);
  if (STATE.total_sec) chips.push("⏱ Timeline: " + STATE.total_sec.toFixed(0) + " sec");
  if (STATE.title_score) chips.push("🏆 Title score: " + STATE.title_score + "/100");
  document.getElementById("statusChips").innerHTML = chips.map(c => `<span class="chip">${c}</span>`).join("");
  // log
  if (STATE.job && STATE.job.log.length) {
    document.getElementById("logBox").textContent = STATE.job.log.join("\n");
  }
  renderTimeline();
  renderUpload();
}

function renderTimeline() {
  const box = document.getElementById("timelineBox");
  if (!STATE || !STATE.timeline || !STATE.timeline.length) {
    box.innerHTML = "<p class='small'>Abhi timeline khaali hai — Run All Agents dabao.</p>";
    return;
  }
  const cues = STATE.timeline;
  const total = STATE.total_sec || cues[cues.length - 1].end;
  const pct = s => Math.max(2, (s / total) * 100);
  box.innerHTML = `
    <p class="small">${cues.length} scenes • ${total.toFixed(0)} second • Video / Caption / Audio / SFX tracks</p>
    <div class="timeline">
      <div class="track"><span class="tlabel">🎬 Video</span>${cues.map(c => `<span class="clip" style="width:${pct(c.end - c.start)}%">Scene ${c.n}</span>`).join("")}</div>
      <div class="track"><span class="tlabel">💬 Caption</span>${cues.map(c => `<span class="clip caption" style="width:${pct(c.end - c.start)}%">${c.text.slice(0, 18)}…</span>`).join("")}</div>
      <div class="track"><span class="tlabel">🔊 Voice</span><span class="clip audio" style="width:100%">Voiceover — Kokoro / Edge TTS (British male)</span></div>
      <div class="track"><span class="tlabel">🎵 SFX</span><span class="clip sfx" style="width:100%">Whoosh har cut par • Ding number par • Music voice se halki</span></div>
    </div>`;
}

function renderUpload() {
  const box = document.getElementById("uploadBox");
  if (!STATE || !STATE.upload_package || !STATE.upload_package.description) {
    box.innerHTML = "<p class='small'>Abhi package nahi bana — Run All Agents dabao.</p>";
    return;
  }
  const u = STATE.upload_package;
  box.innerHTML = `
    <label>Thumbnail text</label><input value="${u.thumbnail_text || ""}" readonly>
    <label>Description</label><textarea readonly>${u.description || ""}</textarea>
    <label>Keywords</label><textarea readonly>${u.keywords || ""}</textarea>
    <label>Thumbnail image prompt</label><textarea readonly>${u.thumbnail_prompt || ""}</textarea>`;
}

async function saveProject() {
  await api("/api/project", {
    topic: document.getElementById("topic").value,
    title: document.getElementById("title").value,
    script: document.getElementById("script").value,
    target_words: parseInt(document.getElementById("targetWords").value || "500", 10)
  });
  alert("Project save ho gaya.");
  refresh();
}

async function runAll() {
  const d = await api("/api/run-all", {});
  alert(d.msg || "Agents chal rahe hain.");
  pollLog();
}

async function runAgent(key) {
  await api("/api/run-agent", {agent: key});
  refresh();
}

async function renderVideo() {
  const d = await api("/api/render", {});
  alert(d.msg || "Render shuru ho gaya. Kaali window mein sirf 'Scene 5/47...' jaisi lines aayengi.");
  pollLog();
}

async function saveApi() {
  const d = await api("/api/api-key", {
    provider: document.getElementById("apiProvider").value,
    tier: document.getElementById("apiTier").value,
    label: document.getElementById("apiLabel").value,
    key: document.getElementById("apiKey").value,
    note: document.getElementById("apiNote").value
  });
  alert(d.msg || (d.ok ? "API save ho gayi." : "Masla hai."));
  document.getElementById("apiKey").value = "";
  refresh();
}

async function delApi(provider) {
  await api("/api/api-key-delete", {provider});
  refresh();
}

async function uploadMedia() {
  const f = document.getElementById("upFile").files[0];
  if (!f) { alert("Pehle file chuno."); return; }
  const fd = new FormData();
  fd.append("file", f);
  fd.append("folder", document.getElementById("upFolder").value);
  fd.append("name", f.name);
  const r = await fetch("/api/upload-media", {method: "POST", body: fd});
  const d = await r.json();
  alert(d.msg || (d.ok ? "Upload ho gayi." : "Masla hai."));
  refresh();
}

async function pollLog() {
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 3000));
    await refresh();
    if (STATE && STATE.job && !STATE.job.running) break;
  }
  refresh();
}

refresh();
setInterval(() => { if (STATE && STATE.job && STATE.job.running) refresh(); }, 5000);
