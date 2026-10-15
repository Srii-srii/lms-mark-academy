// Admin portal UI. Talks to the FastAPI backend in admin/app.py.
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const rupees = (n) => "₹" + Number(n).toLocaleString("en-IN");

let courses = [];
let meta = { levels: [] };
let editingId = null;

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json", "X-Requested-With": "admin-ui" },
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: "same-origin",
  });
  if (res.status === 401 && path !== "/api/login") { showLogin(); throw new Error("Please sign in"); }
  const data = res.headers.get("content-type")?.includes("json") ? await res.json() : null;
  if (!res.ok) {
    const d = data?.detail;
    throw new Error(Array.isArray(d) ? d.map((x) => (typeof x === "string" ? x : x.msg)).join("\n") : d || res.statusText);
  }
  return data;
}

function notify(msg, kind = "ok") {
  const n = $("#notice");
  n.textContent = msg;
  n.className = `notice ${kind === "ok" ? "" : kind}`;
  n.hidden = false;
  clearTimeout(notify.t);
  notify.t = setTimeout(() => (n.hidden = true), kind === "ok" ? 4000 : 9000);
}

// ---------------------------------------------------------------- auth

function showLogin() { $("#app-view").hidden = true; $("#login-view").hidden = false; }

$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  $("#login-error").textContent = "";
  try {
    await api("/api/login", { method: "POST", body: { username: f.get("username"), password: f.get("password") } });
    e.target.reset();
    await start();
  } catch (err) { $("#login-error").textContent = err.message; }
});

$("#logout").addEventListener("click", async () => { await api("/api/logout", { method: "POST" }); showLogin(); });

// ---------------------------------------------------------------- tabs

$$(".tab").forEach((b) => b.addEventListener("click", () => openTab(b.dataset.tab)));
function openTab(name) {
  $$(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  $$("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== name));
  if (name === "academy") loadAcademy();
  if (name === "publish") loadGitStatus();
  if (name === "activity") loadAudit();
}

// ---------------------------------------------------------------- courses

async function loadCourses() {
  courses = await api("/api/courses");
  const rows = courses.map((c, i) => {
    const actions = [`<button class="small" data-act="edit">Edit</button>`];
    if (c.status === "draft") actions.push(`<button class="small" data-act="published">Publish</button>`);
    if (c.status === "published") actions.push(`<button class="small" data-act="draft">Unpublish</button>`, `<button class="small danger" data-act="retired">Retire</button>`);
    if (c.status === "retired") actions.push(`<button class="small" data-act="published">Republish</button>`);
    if (c.status === "draft" && !c.published_once) actions.push(`<button class="small danger" data-act="delete">Delete</button>`);
    return `<tr data-id="${esc(c.id)}">
      <td><button class="small" data-act="up" ${i === 0 ? "disabled" : ""} aria-label="Move up">↑</button>
          <button class="small" data-act="down" ${i === courses.length - 1 ? "disabled" : ""} aria-label="Move down">↓</button></td>
      <td><b>${esc(c.title)}</b><br><span class="id">${esc(c.id)}</span></td>
      <td>${esc(c.level)}</td><td>${rupees(c.price)}</td><td>${c.lessons}</td>
      <td><span class="chip ${esc(c.status)}">${esc(c.status)}</span></td>
      <td class="actions">${actions.join("")}</td></tr>`;
  });
  $("#course-rows").innerHTML = rows.join("") || `<tr><td colspan="7" class="muted">No courses yet.</td></tr>`;
}

$("#course-rows").addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-act]");
  if (!btn) return;
  const id = btn.closest("tr").dataset.id;
  const act = btn.dataset.act;
  try {
    if (act === "edit") return openEditor(courses.find((c) => c.id === id));
    if (act === "up" || act === "down") {
      const ids = courses.map((c) => c.id);
      const i = ids.indexOf(id), j = act === "up" ? i - 1 : i + 1;
      [ids[i], ids[j]] = [ids[j], ids[i]];
      await api("/api/courses/reorder", { method: "POST", body: { ids } });
    } else if (act === "delete") {
      if (!confirm(`Delete the draft "${id}"? This can't be undone.`)) return;
      await api(`/api/courses/${encodeURIComponent(id)}`, { method: "DELETE" });
      notify(`Deleted ${id}.`);
    } else {
      if (act === "retired" && !confirm(`Retire "${id}"? It disappears from the site after Publish. Learners who bought it should get the course.retired notice.`)) return;
      const r = await api(`/api/courses/${encodeURIComponent(id)}/status`, { method: "POST", body: { status: act } });
      const extra = act === "retired" ? " Send learners the notice: GitHub → Actions → Simulate learner event → course.retired." : "";
      notify(`${id} is now ${act}. Publish to update the site.${extra}${r.warnings.length ? "\n" + r.warnings.join("\n") : ""}`, r.warnings.length ? "warn" : "ok");
    }
    await loadCourses();
  } catch (err) { notify(err.message, "bad"); }
});

// ---------------------------------------------------------------- editor

const form = $("#course-form");
const dialog = $("#editor");

function altRow(alt = { id: "", reason: "" }) {
  const options = courses.filter((c) => c.id !== editingId && c.status !== "retired")
    .map((c) => `<option value="${esc(c.id)}" ${c.id === alt.id ? "selected" : ""}>${esc(c.title)}</option>`).join("");
  const row = document.createElement("div");
  row.className = "alt-row";
  row.innerHTML = `<label>Course<select class="alt-id"><option value="">Choose…</option>${options}</select></label>
    <label>When to suggest it<input class="alt-reason" maxlength="200" placeholder="You want hands-on emergency skills" value="${esc(alt.reason)}"></label>
    <button type="button" class="small danger" aria-label="Remove">✕</button>`;
  row.querySelector("button").onclick = () => row.remove();
  $("#alts").append(row);
}

function openEditor(course) {
  editingId = course?.id ?? null;
  form.reset();
  $("#form-error").textContent = "";
  $("#editor-title").textContent = course ? `Edit ${course.title}` : "Add course";
  form.level.innerHTML = meta.levels.map((l) => `<option>${esc(l)}</option>`).join("");
  form.id.readOnly = !!course;
  form.status.closest("label").hidden = !!course;  // status changes use the table buttons
  $("#alts").innerHTML = "";
  if (course) {
    for (const k of ["id", "title", "level", "goal", "duration", "lessons", "price", "summary", "audience"]) form[k].value = course[k];
    form.outcomes.value = course.outcomes.join("\n");
    course.tryInstead.forEach(altRow);
  }
  dialog.showModal();
}

$("#new-course").addEventListener("click", () => openEditor(null));
$("#add-alt").addEventListener("click", () => ($$(".alt-row").length < 3 ? altRow() : notify("Up to 3 alternatives.", "warn")));
$("#cancel-edit").addEventListener("click", () => dialog.close());

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(form);
  const body = {
    id: f.get("id"), title: f.get("title"), level: f.get("level"), goal: f.get("goal"),
    duration: f.get("duration"), lessons: f.get("lessons"), price: f.get("price"),
    summary: f.get("summary"), audience: f.get("audience"), status: f.get("status") || "draft",
    outcomes: f.get("outcomes").split("\n").map((s) => s.trim()).filter(Boolean),
    tryInstead: $$(".alt-row").map((r) => ({ id: r.querySelector(".alt-id").value, reason: r.querySelector(".alt-reason").value }))
      .filter((a) => a.id),
  };
  try {
    if (editingId) {
      body.status = courses.find((c) => c.id === editingId).status;
      await api(`/api/courses/${encodeURIComponent(editingId)}`, { method: "PUT", body });
    } else {
      await api("/api/courses", { method: "POST", body });
    }
    dialog.close();
    notify(`Saved ${body.title}. Publish to update the site.`);
    await loadCourses();
  } catch (err) { $("#form-error").textContent = err.message; }
});

// ---------------------------------------------------------------- academy info

const ACADEMY_FIELDS = [
  ["name", "Academy name"], ["site_url", "Website URL"], ["tagline", "Tagline", true],
  ["course_format", "Course format", true], ["how_to_enrol", "How to enrol", true],
  ["how_to_get_help", "How to get help", true], ["refund_policy", "Refund and cancellation policy (leave empty if none)", true],
  ["discounts", "Discounts and coupons (leave empty if none)", true], ["privacy_url", "Privacy notice URL"], ["currency", "Currency"],
];

async function loadAcademy() {
  const a = await api("/api/academy");
  $("#academy-form").innerHTML = ACADEMY_FIELDS.map(([k, label, wide]) => wide
    ? `<label class="wide">${esc(label)}<textarea name="${k}" rows="2">${esc(a[k])}</textarea></label>`
    : `<label>${esc(label)}<input name="${k}" value="${esc(a[k])}"></label>`).join("")
    + `<div class="wide row-end"><button class="primary">Save academy info</button></div>`;
}

$("#academy-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/academy", { method: "PUT", body: Object.fromEntries(new FormData(e.target)) });
    notify("Academy info saved. Publish to update the guide and knowledge base.");
  } catch (err) { notify(err.message, "bad"); }
});

// ---------------------------------------------------------------- publish & git

$("#publish-btn").addEventListener("click", async () => {
  const btn = $("#publish-btn");
  btn.disabled = true;
  try {
    const r = await api("/api/publish", { method: "POST" });
    $("#publish-result").innerHTML = Object.entries(r.files)
      .map(([f, changed]) => `<li class="${changed ? "changed" : ""}">${esc(f)}: ${changed ? "updated" : "no change"}</li>`).join("");
    const anyChanged = Object.values(r.files).some(Boolean);
    notify(!anyChanged ? "Nothing changed: the site already matches the saved courses."
      : meta.storage === "github" ? "Published to GitHub. The site updates in about a minute."
      : "Generated files are up to date. Push to GitHub to update the site.");
    await Promise.all([loadCourses(), loadGitStatus()]);
  } catch (err) { notify(err.message, "bad"); }
  btn.disabled = false;
});

async function loadGitStatus() {
  try {
    const s = await api("/api/git/status");
    $("#push-controls").hidden = s.mode === "github";
    if (s.mode === "github") {
      $("#git-status").textContent = `Hosted mode: every save and every Publish is committed straight to GitHub (${s.repo}, ${s.branch}). The public site redeploys about a minute after Publish.`;
      return;
    }
    $("#git-status").textContent = s.changed.length
      ? `Not yet on GitHub: ${s.changed.join(", ")}`
      : "Everything published is already committed.";
    $("#push-btn").disabled = !s.allow_push || !s.changed.length;
    if (!s.allow_push) $("#git-status").textContent += " (Push is off: start the server with ALLOW_GIT_PUSH=1, or commit and push from a terminal.)";
  } catch (err) { $("#git-status").textContent = err.message; }
}

$("#push-btn").addEventListener("click", async () => {
  if (!confirm("Commit and push to GitHub? The public site redeploys in about a minute.")) return;
  try {
    const r = await api("/api/git/push", { method: "POST", body: { message: $("#commit-msg").value } });
    notify(r.pushed ? "Pushed. The site will update in about a minute." : `Nothing pushed: ${r.reason}`);
    loadGitStatus();
  } catch (err) { notify(err.message, "bad"); }
});

// ---------------------------------------------------------------- activity

async function loadAudit() {
  const rows = await api("/api/audit");
  $("#audit-rows").innerHTML = rows.map((r) => {
    const { at, user, action, ...rest } = r;
    return `<tr><td>${esc(new Date(at).toLocaleString())}</td><td>${esc(user)}</td><td>${esc(action)}</td><td>${esc(JSON.stringify(rest))}</td></tr>`;
  }).join("") || `<tr><td colspan="4" class="muted">No activity yet.</td></tr>`;
}

// ---------------------------------------------------------------- start

async function start() {
  try {
    meta = await api("/api/me");
  } catch { return; }
  $("#who").textContent = meta.user;
  $("#login-view").hidden = true;
  $("#app-view").hidden = false;
  await loadCourses();
}
start();
