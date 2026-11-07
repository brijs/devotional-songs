/* Recitation mode: full-screen, one verse at a time, with a mala-style
   counter of complete recitations (pāṭha). */
(function (DS) {
  const $ = (s, el = document) => el.querySelector(s);
  const TARGETS = [1, 3, 7, 11, 21, 100, 108];
  let song, root, idx = 0, state, wakeLock = null;
  const key = () => "ds:recite:" + song.id;

  function loadState() {
    state = Object.assign({ count: 0, target: 11 }, DS.store.get(key(), {}));
  }
  const saveState = () => DS.store.set(key(), state);

  function malaSVG(count, target) {
    const n = Math.min(target, 108);
    const R = 40, cx = 50, cy = 50;
    const r = n <= 11 ? 4.2 : n <= 21 ? 3.2 : n <= 50 ? 2.2 : 1.45;
    let beads = "";
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + ((i + 0.5) / n) * Math.PI * 2;
      const done = i < count;
      beads += `<circle cx="${(cx + R * Math.cos(a)).toFixed(2)}" cy="${(cy + R * Math.sin(a)).toFixed(2)}" r="${r}" fill="${done ? "var(--accent)" : "none"}" stroke="${done ? "var(--accent)" : "var(--gold)"}" stroke-width=".8" opacity="${done ? 1 : 0.55}"/>`;
    }
    // the guru bead (meru) at the top
    beads += `<circle cx="${cx}" cy="${cy - R - r - 2.6}" r="${r + 1}" fill="var(--accent-2)"/>`;
    return `<svg viewBox="0 -4 100 104" aria-hidden="true">${beads}</svg>`;
  }

  function render() {
    const v = song.verses[idx];
    const p = DS.prefs;
    DS.emit("recite-verse", v.id);
    const indic = p.script !== "devanagari";
    DS.ensureFont(p.script);
    const orig = v.lines.map((l) => `<span class="ln">${DS.esc(DS.toScript(l.deva, p.script))}</span>`).join("");
    const tr = p.translit !== "off" ? `<div class="rtr">${v.lines.map((l) => `<span class="ln">${DS.esc(DS.lineTranslit(l, p.translit))}</span>`).join("")}</div>` : "";
    const meaning = p.showMeaning && v.meaning?.en ? `<div class="rmeaning">${DS.md(v.meaning.en)}</div>` : "";
    $(".rstage", root).innerHTML = `
      <div class="rlabel">${DS.esc(DS.verseLabel(v))} · ${idx + 1} / ${song.verses.length}</div>
      ${p.showOrig || p.translit === "off" ? `<div class="rorig${indic ? " indic" : ""}">${orig}</div>` : ""}
      ${tr}${meaning}`;
    $(".progress div", root).style.width = ((idx + 1) / song.verses.length) * 100 + "%";
    $(".mala", root).innerHTML = malaSVG(state.count, state.target) +
      `<div class="cnt"><div><b>${state.count}</b><small>of ${state.target}</small></div></div>`;
    $(".mala", root).setAttribute("aria-label", `${state.count} of ${state.target} recitations complete`);
  }

  function toast(deva, en) {
    const t = $("#reciteToast");
    t.innerHTML = `<div class="deva">${DS.esc(deva)}</div><div class="en">${DS.esc(en)}</div>`;
    t.classList.add("show");
    clearTimeout(t._h);
    t._h = setTimeout(() => t.classList.remove("show"), 2400);
  }

  function next() {
    if (idx < song.verses.length - 1) { idx++; render(); return; }
    state.count++;
    saveState();
    if (state.count >= state.target) {
      toast("॥ जय श्री राम ॥", `All ${state.target} recitation${state.target > 1 ? "s" : ""} complete. May Hanumān dwell in your heart.`);
    } else {
      toast(`॥ पाठ ${DS.devaNum(state.count)} सम्पूर्ण ॥`, `Recitation ${state.count} of ${state.target} complete`);
    }
    idx = 0;
    render();
  }
  function prev() { if (idx > 0) { idx--; render(); } }

  async function requestWake() {
    try { if ("wakeLock" in navigator) wakeLock = await navigator.wakeLock.request("screen"); } catch (e) { wakeLock = null; }
  }

  function open(startId) {
    loadState();
    if (startId) { const i = song.verses.findIndex((v) => v.id === startId); if (i >= 0) idx = i; }
    root.classList.add("open");
    document.body.style.overflow = "hidden";
    $("#rTarget", root).value = String(state.target);
    render();
    requestWake();
    $(".rnav.next", root).focus();
  }
  function close() {
    root.classList.remove("open");
    document.body.style.overflow = "";
    if (wakeLock) { wakeLock.release().catch(() => {}); wakeLock = null; }
  }

  function build() {
    root = $("#recite");
    root.innerHTML = `
      <div class="progress"><div></div></div>
      <div class="rtop">
        <button class="btn icon" id="rClose" aria-label="Exit recitation">${DS.icons.close}</button>
        <span>${DS.esc(song.title.deva)}</span>
        <span class="spacer"></span>
        <label for="rTarget">Target</label>
        <select id="rTarget">${TARGETS.map((t) => `<option value="${t}">${t}×</option>`).join("")}</select>
        <button class="btn icon" id="rReset" title="Reset count" aria-label="Reset count">${DS.icons.reset}</button>
        <button class="btn icon" id="rOpts" title="Reading options" aria-label="Reading options">${DS.icons.settings}</button>
      </div>
      <div class="rstage" aria-live="polite"></div>
      <div class="rbottom">
        <button class="rnav prev" aria-label="Previous verse">${DS.icons.prev}</button>
        <div class="mala" role="img"></div>
        <button class="rnav next" aria-label="Next verse">${DS.icons.next}</button>
      </div>`;
    $(".rnav.next", root).addEventListener("click", next);
    $(".rnav.prev", root).addEventListener("click", prev);
    $("#rClose", root).addEventListener("click", close);
    $("#rOpts", root).addEventListener("click", () => DS.openDrawer());
    $("#rReset", root).addEventListener("click", () => {
      if (state.count === 0 || confirm("Reset your recitation count to 0?")) { state.count = 0; idx = 0; saveState(); render(); }
    });
    $("#rTarget", root).addEventListener("change", (e) => { state.target = +e.target.value; saveState(); render(); });

    // Tap the stage: left third = back, rest = forward
    $(".rstage", root).addEventListener("click", (e) => {
      if (window.getSelection && String(window.getSelection())) return;
      const r = e.currentTarget.getBoundingClientRect();
      (e.clientX - r.left < r.width / 3 ? prev : next)();
    });
    // Swipe
    let sx = null, sy = null;
    root.addEventListener("touchstart", (e) => { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
    root.addEventListener("touchend", (e) => {
      if (sx == null) return;
      const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) { e.preventDefault(); (dx < 0 ? next : prev)(); }
      sx = sy = null;
    });
    document.addEventListener("keydown", (e) => {
      if (!root.classList.contains("open") || e.target.matches("select, input, textarea")) return;
      if ($("#drawer").classList.contains("open")) return;
      if (["ArrowRight", "PageDown", " ", "Enter"].includes(e.key)) { e.preventDefault(); next(); }
      else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); prev(); }
      else if (e.key === "Escape") close();
    });
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && root.classList.contains("open")) requestWake();
    });
  }

  DS.on("ready", (s) => { song = s; loadState(); build(); });
  DS.on("recite-open", (id) => open(id));
  DS.on("prefs", () => { if (root && root.classList.contains("open")) render(); });
  // Follow the audio when a timed recording is playing.
  DS.on("audio-verse", (id) => {
    if (!root || !root.classList.contains("open") || !id) return;
    const i = song.verses.findIndex((v) => v.id === id);
    if (i >= 0 && i !== idx) { idx = i; render(); }
  });
})(window.DS);
