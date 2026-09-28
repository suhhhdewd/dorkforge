"use strict";

const $ = (id) => document.getElementById(id);

function currentMode() {
  const checked = document.querySelector('input[name="mode"]:checked');
  return checked ? checked.value : "targeted";
}

function syncModeUI() {
  const broad = currentMode() === "broad";
  $("targeted-values").hidden = broad;
  $("broad-values").hidden = !broad;
  $("auth-row").hidden = broad;
}

function collectValues() {
  const values = {};
  const map = { domain: "v-domain", company: "v-company", ip: "v-ip", asn: "v-asn", name: "v-name" };
  for (const [token, elId] of Object.entries(map)) {
    const v = $(elId).value.trim();
    if (v) values[token] = v;
  }
  return values;
}

function buildBody() {
  const broad = currentMode() === "broad";
  const body = {
    mode: broad ? "broad" : "targeted",
    category: $("f-category").value.trim() || null,
    risk: $("f-risk").value || null,
    surface: $("f-surface").value || null,
    text: $("f-text").value.trim() || null,
    values: broad ? {} : collectValues(),
    tld: broad ? $("b-tld").value.trim() || null : null,
    country: broad ? $("b-country").value.trim() || null : null,
    authorized: broad ? false : $("authorized").checked,
  };
  return body;
}

function riskClass(risk) {
  return "risk-" + String(risk).replace(/[^A-Za-z]/g, "");
}

function renderRows(rows) {
  const tbody = $("results").querySelector("tbody");
  tbody.innerHTML = "";
  for (const r of rows) {
    const tr = document.createElement("tr");

    const cells = [
      ["id", r.id],
      ["category", r.category],
      ["risk", r.risk],
      ["surface", r.surface],
    ];
    for (const [cls, val] of cells) {
      const td = document.createElement("td");
      td.textContent = val;
      if (cls === "risk") td.className = riskClass(val);
      tr.appendChild(td);
    }

    const modeTd = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "badge badge-" + r.mode;
    badge.textContent = r.mode;
    badge.title = r.advisory;
    modeTd.appendChild(badge);
    tr.appendChild(modeTd);

    const q = document.createElement("td");
    q.className = "query";
    q.textContent = r.query;
    tr.appendChild(q);

    const purpose = document.createElement("td");
    purpose.textContent = r.purpose;
    tr.appendChild(purpose);

    const urlTd = document.createElement("td");
    const a = document.createElement("a");
    a.href = r.url;
    a.textContent = "open";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    urlTd.appendChild(a);
    tr.appendChild(urlTd);

    const copyTd = document.createElement("td");
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "copy";
    btn.addEventListener("click", () => {
      navigator.clipboard.writeText(r.query).then(() => {
        btn.textContent = "copied";
        setTimeout(() => (btn.textContent = "copy"), 1200);
      });
    });
    copyTd.appendChild(btn);
    tr.appendChild(copyTd);

    tbody.appendChild(tr);
  }
  $("results").hidden = rows.length === 0;
}

async function build() {
  $("status").textContent = "Building…";
  $("notice").hidden = true;
  try {
    const resp = await fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildBody()),
    });
    const data = await resp.json();
    if (!resp.ok) {
      $("status").textContent = data.detail || "Request failed.";
      $("results").hidden = true;
      return;
    }
    if (data.notice) {
      $("notice").textContent = data.notice;
      $("notice").hidden = false;
    }
    renderRows(data.rows);
    let msg = `${data.rows.length} queries built.`;
    if (data.skipped) msg += ` ${data.skipped} skipped.`;
    $("status").textContent = msg;
  } catch (err) {
    $("status").textContent = "Error: " + err;
  }
}

async function doExport(format) {
  const body = Object.assign(buildBody(), { format });
  const resp = await fetch("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    $("status").textContent = data.detail || "Export failed.";
    return;
  }
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "dorkforge." + (format === "markdown" ? "md" : format);
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

document.querySelectorAll('input[name="mode"]').forEach((el) =>
  el.addEventListener("change", syncModeUI)
);
$("build-btn").addEventListener("click", build);
document.querySelectorAll(".export-btn").forEach((btn) =>
  btn.addEventListener("click", () => doExport(btn.dataset.format))
);

syncModeUI();
