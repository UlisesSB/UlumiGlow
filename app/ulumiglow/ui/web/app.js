/* =====================================================================
   UlumiGlow - comportamiento de la interfaz
   Habla con Python a través de window.pywebview.api (ver ui/window.py).
   ===================================================================== */

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];
const api = () => window.pywebview.api;

let cfg = null;        // config actual (espejo de config.json)
let monitors = [];

// ---------- Guardado con espera (los sliders mandan muchos cambios) ----------
let pending = {}, saveTimer = null;
function save(patch) {
  Object.assign(cfg, patch);
  Object.assign(pending, patch);
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { api().set_config(pending); pending = {}; }, 120);
}

// ---------- Utilidades de color ----------
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const toHex = (r, g, b) => "#" + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");

function hsvToHex(h, s, v = 1) {
  const f = (n) => { const k = (n + h / 60) % 6; return v - v * s * Math.max(0, Math.min(k, 4 - k, 1)); };
  return toHex(f(5) * 255, f(3) * 255, f(1) * 255);
}
function hexToHsv(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const max = Math.max(r, g, b), d = max - Math.min(r, g, b);
  let h = 0;
  if (d) h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return { h: (h * 60 + 360) % 360, s: max ? d / max : 0 };
}
function setRangeFill(input) {
  const p = ((input.value - input.min) / (input.max - input.min)) * 100;
  input.style.setProperty("--p", p + "%");
}

// ---------- Encendido y modos ----------
function renderPower() {
  $("#power").setAttribute("aria-pressed", cfg.enabled);
  $("#power-label").textContent = cfg.enabled ? "Encendido" : "Apagado";
}
function renderMode() {
  $$(".mode").forEach((b) => b.classList.toggle("active", b.dataset.mode === cfg.mode));
  $$(".view").forEach((v) => v.classList.toggle("active", v.dataset.view === cfg.mode));
  if (cfg.mode === "ambilight") loadShot();
}
$("#power").onclick = () => { save({ enabled: !cfg.enabled }); renderPower(); };
$$(".mode").forEach((b) => (b.onclick = () => {
  save({ mode: b.dataset.mode, enabled: true });
  renderPower(); renderMode();
}));

// ---------- Ambilight: zona de captura ----------
const PRESET_NAMES = { top: "Arriba", bottom: "Abajo", left: "Izquierda", right: "Derecha", full: "Toda la pantalla", custom: "Personalizada" };

function presetRect(preset, d) {
  switch (preset) {
    case "top": return { x: 0, y: 0, w: 1, h: d };
    case "bottom": return { x: 0, y: 1 - d, w: 1, h: d };
    case "left": return { x: 0, y: 0, w: d, h: 1 };
    case "right": return { x: 1 - d, y: 0, w: d, h: 1 };
    case "full": return { x: 0, y: 0, w: 1, h: 1 };
  }
  return null;
}
function setZone(preset, rect) {
  const z = { ...cfg.zone, preset, ...(rect || presetRect(preset, cfg.zone.depth)) };
  save({ zone: z });
  renderZone();
}
function renderZone() {
  const z = cfg.zone, el = $("#zone");
  Object.assign(el.style, { left: z.x * 100 + "%", top: z.y * 100 + "%", width: z.w * 100 + "%", height: z.h * 100 + "%" });
  $("#zone-label").textContent = PRESET_NAMES[z.preset] || "";
  $$("#presets .chip").forEach((c) => c.classList.toggle("active", c.dataset.preset === z.preset));
  const edge = ["top", "bottom", "left", "right"].includes(z.preset);
  $("#depth-field").setAttribute("aria-disabled", !edge);
  $("#depth").value = Math.round(z.depth * 100);
  $("#depth-out").textContent = Math.round(z.depth * 100) + " %";
  setRangeFill($("#depth"));
  $("#custom-hint").style.visibility = z.preset === "custom" ? "visible" : "hidden";
}
$$("#presets .chip").forEach((c) => (c.onclick = () =>
  setZone(c.dataset.preset, c.dataset.preset === "custom" ? { ...cfg.zone } : null)));
$("#depth").oninput = (e) => {
  cfg.zone.depth = e.target.value / 100;
  setZone(cfg.zone.preset);
};

// Arrastrar sobre la captura dibuja una zona personalizada
(function dragZone() {
  const map = $("#map");
  let start = null;
  const point = (e) => {
    const r = map.getBoundingClientRect();
    return { x: clamp((e.clientX - r.left) / r.width, 0, 1), y: clamp((e.clientY - r.top) / r.height, 0, 1) };
  };
  const rectFrom = (a, b) => ({
    x: Math.min(a.x, b.x), y: Math.min(a.y, b.y),
    w: Math.max(Math.abs(a.x - b.x), 0.02), h: Math.max(Math.abs(a.y - b.y), 0.02),
  });
  map.addEventListener("mousedown", (e) => { start = point(e); map.classList.add("dragging"); });
  window.addEventListener("mousemove", (e) => {
    if (!start) return;
    Object.assign(cfg.zone, rectFrom(start, point(e)), { preset: "custom" });
    renderZone();
  });
  window.addEventListener("mouseup", (e) => {
    if (!start) return;
    const rect = rectFrom(start, point(e));
    start = null;
    map.classList.remove("dragging");
    rect.x = Math.min(rect.x, 1 - rect.w);
    rect.y = Math.min(rect.y, 1 - rect.h);
    setZone("custom", rect);
  });
})();

function renderMonitors() {
  const sel = $("#monitor");
  sel.innerHTML = monitors.map((m) =>
    `<option value="${m.index}">Pantalla ${m.index} · ${m.width}×${m.height}</option>`).join("");
  sel.value = cfg.monitor;
  const m = monitors.find((m) => m.index === cfg.monitor) || monitors[0];
  if (m) $("#map").style.aspectRatio = `${m.width} / ${m.height}`;
}
$("#monitor").onchange = (e) => { save({ monitor: +e.target.value }); renderMonitors(); loadShot(); };

async function loadShot() {
  try { $("#shot").src = await api().get_screenshot(cfg.monitor); } catch (e) { /* sin captura */ }
}
$("#refresh-shot").onclick = loadShot;

// ---------- Color fijo ----------
const SWATCHES = ["#2f7bff", "#22c3ee", "#2ee26a", "#b6ff3b", "#ffd400",
                  "#ff7a1a", "#ff2a3d", "#ff3fa4", "#8a4dff", "#ffffff"];
$("#swatches").innerHTML = SWATCHES.map((c) =>
  `<button class="swatch" data-color="${c}" style="--c:${c}" title="${c}"></button>`).join("");
$$(".swatch").forEach((s) => (s.onclick = () => setFixed(s.dataset.color)));

function setFixed(hex) {
  save({ fixed_color: hex.toLowerCase() });
  renderFixed();
}
function renderFixed() {
  const hex = cfg.fixed_color, { h, s } = hexToHsv(hex);
  $("#fixed-orb").style.setProperty("--c", hex);
  $("#hue").value = Math.round(h);
  $("#sat").value = Math.round(s * 100);
  $("#sat").style.setProperty("--sat-end", hsvToHex(h, 1));
  if (document.activeElement !== $("#hex")) $("#hex").value = hex.toUpperCase();
  $$(".swatch").forEach((b) => b.classList.toggle("active", b.dataset.color === hex));
}
$("#hue").oninput = $("#sat").oninput = () =>
  setFixed(hsvToHex(+$("#hue").value, $("#sat").value / 100));
$("#hex").oninput = (e) => {
  let v = e.target.value.trim();
  if (!v.startsWith("#")) v = "#" + v;
  if (/^#[0-9a-f]{6}$/i.test(v)) setFixed(v);
};

// ---------- Ajustes generales ----------
$("#brightness").oninput = (e) => {
  save({ brightness: +e.target.value });
  renderGeneral();
};
$$("#curve button").forEach((b) => (b.onclick = () => { save({ curve: b.dataset.curve }); renderGeneral(); }));

function renderPorts(ports) {
  const sel = $("#port");
  const list = [...new Set([...ports, cfg.port].filter(Boolean))];
  sel.innerHTML = `<option value="">Automático</option>` + list.map((p) => `<option>${p}</option>`).join("");
  sel.value = cfg.port;
}
$("#port").onfocus = async () => renderPorts(await api().get_ports());
$("#port").onchange = (e) => save({ port: e.target.value });

function renderGeneral() {
  $("#brightness").value = cfg.brightness;
  $("#bright-out").textContent = cfg.brightness + " %";
  setRangeFill($("#brightness"));
  $$("#curve button").forEach((b) => b.classList.toggle("active", b.dataset.curve === cfg.curve));
}

// ---------- Ventana ----------
$("#btn-hide").onclick = () => api().hide();
$("#btn-min").onclick = () => api().minimize();

// ---------- Estado en vivo (color que se está enviando) ----------
async function poll() {
  try {
    const st = await api().get_status();
    const [r, g, b] = st.rgb;
    // Para que se vea, el fondo usa el color con brillo normalizado
    const m = Math.max(r, g, b, 1), k = st.enabled ? 255 / m : 0;
    const shown = st.enabled && m > 1 ? toHex(r * k, g * k, b * k) : "#2f7bff";
    document.documentElement.style.setProperty("--live", shown);
    // brillo real (aprox. como lo ve el ojo) para el orbe del modo audio
    const raw = st.enabled ? toHex(...[r, g, b].map((c) => 255 * (c / 255) ** (1 / 2.2))) : "#000000";
    document.documentElement.style.setProperty("--live-raw", raw);
    $("#live-rgb").textContent = `${r}, ${g}, ${b}`;
    $("#device-status").textContent = st.status;
    $("#device-pill").classList.toggle("ok", st.connected);
    if (st.enabled !== cfg.enabled || st.mode !== cfg.mode) {   // cambió desde la bandeja
      cfg.enabled = st.enabled; cfg.mode = st.mode;
      renderPower(); renderMode();
    }
  } catch (e) { /* la ventana se está cerrando */ }
}

// ---------- Intro ----------
function startIntro() {
  const intro = $("#intro");
  intro.hidden = false;
  const close = () => { intro.classList.add("out"); setTimeout(() => intro.remove(), 700); };
  $("#intro-skip").onclick = () => intro.classList.add("done");
  $("#intro-config").onclick = close;
  $("#intro-tray").onclick = () => { api().hide(); intro.remove(); };
}

// ---------- Arranque ----------
async function init() {
  const state = await api().get_state();
  cfg = state.config;
  monitors = state.monitors;
  $("#version").textContent = "v" + state.version;
  renderMonitors(); renderPower(); renderMode(); renderZone(); renderFixed(); renderGeneral();
  renderPorts(state.ports);
  if (state.intro) startIntro(); else $("#intro").remove();
  poll();
  setInterval(poll, 200);
}

if (window.pywebview && window.pywebview.api) init();
else window.addEventListener("pywebviewready", init, { once: true });
