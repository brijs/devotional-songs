/* Song reader: loads songs/<id>.json and renders header, about cards, verses,
   settings drawer and word popovers. Audio and recitation hook in via DS events. */
(function (DS) {
  const $ = (sel, el = document) => el.querySelector(sel);
  const params = new URLSearchParams(location.search);
  const songId = (params.get("id") || "hanuman-chalisa").replace(/[^a-z0-9-]/gi, "");


  const TYPE_LABEL = { doha: "Dohā", chaupai: "Chaupāī", shloka: "Śloka", pada: "Pada" };

  /* ───────── Rendering ───────── */
  function verseLabel(v) {
    return (TYPE_LABEL[v.type] || v.type) + " " + v.number;
  }
  DS.verseLabel = verseLabel;

  function renderHeader(song) {
    document.title = (song.title.en || song.id) + " · Devotional Songs";
    $("#crumb").textContent = song.title.en;
    const a = song.author || {};
    const audioBtn = song.audio ? `<button class="btn" id="listenBtn">${DS.icons.headphones}<span>Listen</span></button>` : "";
    $("#songHead").innerHTML = `
      <div class="kicker">${DS.esc(song.language)} · ${DS.esc(song.composed || "")}</div>
      <h1>${DS.esc(song.title.deva)}</h1>
      <div class="sub">${DS.esc(song.title.iast || song.title.en)}</div>
      <div class="byline">${DS.esc(song.subtitle || "")}${a.name ? " · by " + DS.esc(a.name) + (a.dates ? " (" + DS.esc(a.dates) + ")" : "") : ""}</div>
      ${song.epigraph ? `<div class="epigraph"><div class="deva">${DS.esc(song.epigraph.deva)}</div><div class="en">${DS.esc(song.epigraph.en)}</div></div>` : ""}
      <div class="head-actions">
        <button class="btn primary" id="reciteBtn">${DS.icons.recite}<span>Recite</span></button>
        ${audioBtn}
        <a class="btn" href="#verses">Begin reading ↓</a>
      </div>`;
  }

  function renderAbout(song) {
    const cards = (song.about || []).map((c, i) => `
      <details class="about-card"${i === 0 ? " open" : ""}>
        <summary>${DS.esc(c.heading)} ${c.tag && c.tag !== "overview" ? `<span class="tag ${DS.esc(c.tag)}">${DS.esc(c.tag)}</span>` : ""}</summary>
        <div class="body">${c.body.map((p) => `<p>${DS.md(p)}</p>`).join("")}</div>
      </details>`).join("");
    const src = (song.sources || []).length ? `
      <details class="about-card">
        <summary>Sources &amp; credits</summary>
        <div class="body"><ul class="sources">${song.sources.map((s) => `<li><a href="${DS.esc(s.url)}" target="_blank" rel="noopener">${DS.esc(s.label)}</a></li>`).join("")}</ul>
        ${song.audio ? `<p style="margin-top:10px">Recording: <a href="${DS.esc(song.audio.sourceUrl)}" target="_blank" rel="noopener">${DS.esc(song.audio.title)}</a>, ${DS.esc(song.audio.artist)}, ${DS.esc(song.audio.recorded || "")}. Licensed <a href="${DS.esc(song.audio.licenseUrl)}" target="_blank" rel="noopener">${DS.esc(song.audio.license)}</a>.</p>` : ""}
        <p>Glosses, meanings and reflections were prepared for this site. Word roots marked √ are Sanskrit <em>dhātus</em>; Awadhi forms are traced to their Sanskrit source where one exists.</p></div>
      </details>` : "";
    $("#about").innerHTML = `<h2>About this hymn</h2>${cards}${src}`;
  }

  function wordHTML(w, vi, li, wi, scriptText, wt) {
    return `<button type="button" class="w" data-v="${vi}" data-l="${li}" data-w="${wi}" aria-expanded="false"><span class="wd">${DS.esc(scriptText)}</span><span class="wt">${DS.esc(wt)}</span><span class="wg">${DS.esc(w.gloss)}</span></button>`;
  }

  function verseHTML(v, vi) {
    const p = DS.prefs;
    const indic = p.script !== "devanagari";
    const lines = v.lines.map((ln, li) => {
      const wts = DS.wordTranslits(ln, p.translit);
      const ws = ln.words.map((w, wi) => wordHTML(w, vi, li, wi, DS.toScript(w.deva, p.script), wts[wi] || ""));
      const end = ln.deva.trim().slice(-1);
      const danda = /[।॥]/.test(end) ? `<span class="danda">${end === "॥" ? "॥" + (v.type === "chaupai" ? DS.toScript(DS.devaNum(v.number), p.script) + "॥" : "") : "।"}</span>` : "";
      // keep the last word and the danda/verse number together so they never wrap apart
      const last = ws.pop();
      return `<span class="ln">${ws.join(" ")} <span class="nowrap">${last}${danda}</span></span>`;
    }).join("");
    const tr = p.translit === "off" ? "" :
      `<div class="translit">${v.lines.map((ln) => `<span class="ln">${DS.esc(DS.lineTranslit(ln, p.translit))}</span>`).join("")}</div>`;
    const meaning = v.meaning && v.meaning.en ? `<div class="meaning"><p>${DS.md(v.meaning.en)}</p></div>` : "";
    const bhava = v.bhava && v.bhava.en ? `<div class="bhava">${DS.md(v.bhava.en)}</div>` : "";
    const notes = v.notes && v.notes.length ? `<details class="notes"><summary>Notes</summary><ul>${v.notes.map((n) => `<li>${DS.md(n)}</li>`).join("")}</ul></details>` : "";
    const playBtn = DS.song.audio ? `<button class="tool-btn" data-act="play" title="Play from this verse" aria-label="Play from this verse">${DS.icons.playFrom}</button>` : "";
    return `
      <article class="verse ${DS.esc(v.type)}" id="v-${DS.esc(v.id)}" data-vi="${vi}">
        <div class="num">${verseLabel(v)}</div>
        <div class="tools">${playBtn}
          <button class="tool-btn" data-act="copy" title="Copy verse text" aria-label="Copy verse text">${DS.icons.copy}</button>
          <button class="tool-btn" data-act="link" title="Copy link to this verse" aria-label="Copy link to this verse">${DS.icons.link}</button>
        </div>
        <div class="orig${indic ? " indic" : ""}" lang="${p.script === "devanagari" ? "awa" : ""}">${lines}</div>
        ${tr}${meaning}${bhava}${notes}
      </article>`;
  }

  function renderVerses() {
    const song = DS.song;
    DS.ensureFont(DS.prefs.script);
    let html = "";
    for (const sec of song.sections) {
      const vs = song.verses.map((v, i) => [v, i]).filter(([v]) => v.section === sec.id);
      if (!vs.length) continue;
      html += `<div class="section-head"><div class="deva">${DS.esc(sec.deva || "")}</div><div class="en">${DS.esc(sec.label)}</div></div>`;
      html += vs.map(([v, i]) => verseHTML(v, i)).join("");
    }
    $("#verses").innerHTML = html;
    applyBodyClasses();
    DS.emit("rendered");
  }
  DS.renderVerses = renderVerses;

  function applyBodyClasses() {
    const p = DS.prefs, b = document.body.classList;
    b.toggle("hide-orig", !p.showOrig);
    b.toggle("hide-translit", p.translit === "off");
    b.toggle("hide-meaning", !p.showMeaning);
    b.toggle("hide-bhava", !p.showBhava);
    b.toggle("hide-notes", !p.showNotes);
    b.remove("gloss-off", "gloss-tap", "gloss-interlinear");
    b.add("gloss-" + p.gloss);
  }

  /* ───────── Word popover ───────── */
  let pop = null, popBtn = null;
  function closePop() {
    if (pop) pop.remove();
    if (popBtn) popBtn.setAttribute("aria-expanded", "false");
    pop = popBtn = null;
  }
  function openPop(btn) {
    closePop();
    const vi = +btn.dataset.v, li = +btn.dataset.l, wi = +btn.dataset.w;
    const line = DS.song.verses[vi].lines[li];
    const w = line.words[wi];
    const p = DS.prefs;
    const showDeva = p.script !== "devanagari" ? `<div class="pt" style="font-style:normal;font-family:var(--font-deva)">${DS.esc(w.deva)}</div>` : "";
    const iast = DS.toRoman(w.deva, "iast");
    pop = document.createElement("div");
    pop.className = "pop";
    pop.setAttribute("role", "dialog");
    pop.setAttribute("aria-label", "Word meaning");
    pop.innerHTML = `
      <div class="pw${p.script !== "devanagari" ? "" : ""}">${DS.esc(DS.toScript(w.deva, p.script))}</div>
      ${showDeva}
      <div class="pt">${DS.esc(iast)}</div>
      <div class="pg">${DS.esc(w.gloss)}</div>
      ${w.root ? `<div class="pr"><b>Root &amp; origin</b>${DS.esc(w.root)}</div>` : ""}
      <div class="nav"><button data-nav="-1" ${wi === 0 && li === 0 ? "disabled" : ""}>← prev word</button><button data-nav="1">next word →</button></div>`;
    if (p.script !== "devanagari") pop.querySelector(".pw").style.fontFamily = "var(--font-indic)";
    document.body.appendChild(pop);
    const r = btn.getBoundingClientRect();
    const pw = pop.offsetWidth;
    let left = r.left + window.scrollX + r.width / 2 - pw / 2;
    left = Math.max(window.scrollX + 12, Math.min(left, window.scrollX + document.documentElement.clientWidth - pw - 12));
    pop.style.left = left + "px";
    pop.style.top = (r.bottom + window.scrollY + 8) + "px";
    btn.setAttribute("aria-expanded", "true");
    popBtn = btn;
    pop.addEventListener("click", (e) => {
      const nb = e.target.closest("[data-nav]");
      if (!nb) return;
      e.stopPropagation();
      const all = [...btn.closest(".verse").querySelectorAll(".w")];
      const idx = all.indexOf(btn) + +nb.dataset.nav;
      if (all[idx]) openPop(all[idx]);
      else {
        const nextVerse = btn.closest(".verse").nextElementSibling;
        const nv = nextVerse && (nextVerse.classList.contains("verse") ? nextVerse : nextVerse.nextElementSibling);
        const first = nv && nv.querySelector(".w");
        if (first) { first.scrollIntoView({ block: "center", behavior: "smooth" }); setTimeout(() => openPop(first), 250); }
      }
    });
  }

  /* ───────── Verse tools ───────── */
  function flash(msg) {
    let t = $("#miniToast");
    if (!t) {
      t = document.createElement("div");
      t.id = "miniToast";
      t.style.cssText = "position:fixed;left:50%;top:70px;transform:translateX(-50%);z-index:95;background:var(--ink);color:var(--bg);padding:8px 14px;border-radius:999px;font:13px var(--font-ui);opacity:0;transition:opacity .2s;pointer-events:none";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = 1;
    clearTimeout(t._h);
    t._h = setTimeout(() => (t.style.opacity = 0), 1600);
  }
  DS.flash = flash;

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; } catch (e) { return false; }
  }

  function onVersesClick(e) {
    const w = e.target.closest(".w");
    if (w) {
      if (DS.prefs.gloss !== "tap") return;
      e.stopPropagation();
      if (popBtn === w) closePop(); else openPop(w);
      return;
    }
    const tool = e.target.closest(".tool-btn");
    if (!tool) return;
    const art = tool.closest(".verse");
    const v = DS.song.verses[+art.dataset.vi];
    if (tool.dataset.act === "copy") {
      const tr = DS.prefs.translit !== "off" ? "\n" + v.lines.map((l) => DS.lineTranslit(l, DS.prefs.translit)).join("\n") : "";
      const txt = v.lines.map((l) => DS.toScript(l.deva, DS.prefs.script)).join("\n") + tr + "\n\n" + (v.meaning?.en || "");
      copyText(txt).then((ok) => flash(ok ? "Verse copied" : "Copy not available"));
    } else if (tool.dataset.act === "link") {
      const url = location.origin + location.pathname + location.search + "#v-" + v.id;
      history.replaceState(null, "", "#v-" + v.id);
      copyText(url).then((ok) => flash(ok ? "Link copied" : "Link set in address bar"));
    } else if (tool.dataset.act === "play") {
      DS.emit("play-verse", v.id);
    }
  }

  /* ───────── Settings drawer ───────── */
  function seg(name, options) {
    return `<div class="seg" role="group" data-pref="${name}">${options.map(([val, label]) =>
      `<button type="button" data-val="${val}" aria-pressed="${String(DS.prefs[name]) === String(val)}">${label}</button>`).join("")}</div>`;
  }
  function sw(name, label) {
    return `<div class="row"><label for="pf-${name}">${label}</label><span class="switch"><input type="checkbox" id="pf-${name}" data-pref="${name}" ${DS.prefs[name] ? "checked" : ""}><span></span></span></div>`;
  }
  function renderDrawer() {
    const p = DS.prefs;
    const trHint = (DS.TRANSLITS.find((t) => t.id === p.translit) || {}).hint || "";
    $("#drawer").innerHTML = `
      <div class="dh"><h2>Reading options</h2><button class="btn icon" id="closeDrawer" aria-label="Close settings">${DS.icons.close}</button></div>
      <h3>Layers</h3>
      ${sw("showOrig", "Original text")}
      ${sw("showMeaning", "English meaning")}
      ${sw("showBhava", "Reflection (bhāva)")}
      ${sw("showNotes", "Notes &amp; references")}
      ${DS.song && DS.song.art ? sw("showArt", "Verse illustrations") : ""}
      <h3>Word-by-word</h3>
      ${seg("gloss", [["off", "Off"], ["tap", "Tap a word"], ["interlinear", "Interlinear"]])}
      <p class="hint">Tap a word to see its meaning and Sanskrit root, or show a gloss under every word.</p>
      <h3>Script of the original</h3>
      <select data-pref="script" aria-label="Script">${DS.SCRIPTS.map((s) => `<option value="${s.id}" ${s.id === p.script ? "selected" : ""}>${s.label}</option>`).join("")}</select>
      <h3>Transliteration</h3>
      <select data-pref="translit" aria-label="Transliteration">${DS.TRANSLITS.map((s) => `<option value="${s.id}" ${s.id === p.translit ? "selected" : ""}>${s.label}</option>`).join("")}</select>
      <p class="hint">${DS.esc(trHint)}</p>
      <h3>Theme</h3>
      ${seg("theme", [["auto", "Auto"], ["light", "Light"], ["diya", "Diyā"], ["dark", "Dark"]])}
      <h3>Text size</h3>
      <div class="row"><label for="pf-scale">Overall</label></div>
      <input type="range" id="pf-scale" data-pref="scale" min="0.85" max="1.5" step="0.05" value="${p.scale}">
      <div class="row"><label for="pf-origScale">Original text</label></div>
      <input type="range" id="pf-origScale" data-pref="origScale" min="0.8" max="1.8" step="0.05" value="${p.origScale}">
      <h3></h3>
      <button class="btn" id="resetPrefs">${DS.icons.reset}<span>Reset to defaults</span></button>`;
  }
  function setPref(name, val) {
    DS.prefs[name] = val;
    DS.savePrefs();
    DS.applyTheme();
    if (["script", "translit", "gloss"].includes(name)) { closePop(); renderVerses(); }
    else applyBodyClasses();
    if (name === "translit" || name === "theme" || name === "gloss") renderDrawer();
    DS.emit("prefs", { name, val });
  }
  function openDrawer() { renderDrawer(); $("#drawer").classList.add("open"); $("#scrim").classList.add("open"); $("#closeDrawer").focus(); }
  function closeDrawer() { $("#drawer").classList.remove("open"); $("#scrim").classList.remove("open"); }
  DS.openDrawer = openDrawer;

  function bindDrawer() {
    const d = $("#drawer");
    d.addEventListener("click", (e) => {
      if (e.target.closest("#closeDrawer")) return closeDrawer();
      if (e.target.closest("#resetPrefs")) { Object.assign(DS.prefs, DS.defaults); DS.savePrefs(); DS.applyTheme(); renderVerses(); renderDrawer(); return; }
      const b = e.target.closest(".seg button");
      if (b) setPref(b.parentElement.dataset.pref, b.dataset.val);
    });
    d.addEventListener("change", (e) => {
      const el = e.target;
      if (!el.dataset.pref) return;
      if (el.type === "checkbox") setPref(el.dataset.pref, el.checked);
      else if (el.tagName === "SELECT") setPref(el.dataset.pref, el.value);
    });
    d.addEventListener("input", (e) => {
      const el = e.target;
      if (el.type === "range") setPref(el.dataset.pref, +el.value);
    });
    $("#scrim").addEventListener("click", closeDrawer);
  }

  /* ───────── Boot ───────── */
  async function boot() {
    $("#settingsBtn").innerHTML = DS.icons.settings + '<span class="lbl">Options</span>';
    try {
      const res = await fetch("songs/" + songId + ".json");
      if (!res.ok) throw new Error(res.status);
      DS.song = await res.json();
    } catch (e) {
      $("#songHead").innerHTML = `<h1 style="font-family:var(--font-body);color:var(--ink)">Song not found</h1>
        <p>Could not load <code>songs/${DS.esc(songId)}.json</code>. If you opened this file directly, serve the folder instead:<br><code>python3 -m http.server</code></p>`;
      return;
    }
    renderHeader(DS.song);
    renderAbout(DS.song);
    renderVerses();
    bindDrawer();

    $("#settingsBtn").addEventListener("click", openDrawer);
    $("#verses").addEventListener("click", onVersesClick);
    document.addEventListener("click", (e) => { if (pop && !pop.contains(e.target)) closePop(); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { closePop(); closeDrawer(); }
    });
    window.addEventListener("resize", closePop);

    $("#reciteBtn").addEventListener("click", () => DS.emit("recite-open"));
    const lb = $("#listenBtn");
    if (lb) lb.addEventListener("click", () => DS.emit("audio-toggle"));

    DS.emit("ready", DS.song);

    if (location.hash) {
      const el = document.getElementById(location.hash.slice(1));
      if (el) setTimeout(() => el.scrollIntoView({ block: "start" }), 50);
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})(window.DS);
