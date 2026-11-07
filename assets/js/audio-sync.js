/* Audio player with verse highlighting, plus a tap-to-time helper for
   creating verse timings for any recording.

   Timings live in song.audio.timings as { verseId: startSeconds }.
   Timings made with the helper are saved in this browser (localStorage) and
   take effect immediately; copy the JSON into the song file to make them permanent. */
(function (DS) {
  const $ = (s, el = document) => el.querySelector(s);
  let song, audio, bar, timings = {}, order = [], current = null, timingMode = false, markIdx = 0;
  const key = () => "ds:timings:" + song.id;

  function loadTimings() {
    const local = DS.store.get(key(), null);
    timings = Object.assign({}, song.audio.timings || {}, local || {});
  }
  const hasTimings = () => Object.keys(timings).length > 0;

  function verseAt(t) {
    let found = null;
    for (const id of order) {
      if (timings[id] != null && timings[id] <= t + 0.05) found = id;
    }
    return found;
  }

  function setCurrent(id) {
    if (id === current) return;
    if (current) { const el = document.getElementById("v-" + current); if (el) el.classList.remove("playing"); }
    current = id;
    if (!id) return;
    const el = document.getElementById("v-" + id);
    if (el) {
      el.classList.add("playing");
      if (DS.prefs.follow && !$(".recite.open")) el.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    DS.emit("audio-verse", id);
  }

  function render() {
    const a = song.audio;
    bar.innerHTML = `
      <div class="prow">
        <button class="play" id="pPlay" aria-label="Play">${DS.icons.play}</button>
        <div class="pmeta">
          <div class="ptitle">${DS.esc(a.title)}</div>
          <div class="pcredit">${DS.esc(a.artist)} · <a href="${DS.esc(a.sourceUrl)}" target="_blank" rel="noopener">source</a> · <a href="${DS.esc(a.licenseUrl)}" target="_blank" rel="noopener">${DS.esc(a.license)}</a></div>
        </div>
        <button class="pbtn" id="pFollow" title="Auto-scroll to the current verse" aria-pressed="${DS.prefs.follow}">${DS.icons.follow}</button>
        <button class="pbtn" id="pTime" title="Time verses for this recording" aria-label="Time verses">${DS.icons.timer}</button>
        <button class="pbtn" id="pClose" title="Close player" aria-label="Close player">${DS.icons.close}</button>
      </div>
      <div class="seek"><input type="range" id="pSeek" min="0" max="1000" value="0" aria-label="Seek"><span class="time" id="pTimeLbl">0:00 / 0:00</span></div>
      <div id="pExtra"></div>`;
    $("#pFollow", bar).style.color = DS.prefs.follow ? "var(--accent)" : "";
    renderExtra();
  }

  function renderExtra() {
    const ex = $("#pExtra", bar);
    if (timingMode) {
      const v = song.verses[markIdx];
      ex.innerHTML = `
        <div class="timing-panel">
          <div class="trow">
            <div class="cur">${v ? `Press <b>T</b> or <b>Mark</b> when <b>${DS.esc(DS.verseLabel(v))}</b> begins:<br><span style="font-family:var(--font-deva)">${DS.esc(v.lines[0].deva)}</span>` : "<b>All verses marked.</b> Timings are saved in this browser."}</div>
            <button class="btn primary" id="tMark" ${v ? "" : "disabled"}>Mark</button>
            <button class="btn" id="tUndo" ${markIdx ? "" : "disabled"}>Undo</button>
            <button class="btn" id="tClear">Clear</button>
            <button class="btn" id="tDone">Done</button>
          </div>
          <textarea readonly id="tOut" aria-label="Timings JSON"></textarea>
          <div class="trow" style="margin-top:6px"><button class="btn" id="tCopy">Copy JSON</button><span class="hint">Paste into <code>audio.timings</code> in the song file to share these timings with everyone.</span></div>
        </div>`;
      $("#tOut", bar).value = JSON.stringify(roundTimings(), null, 0).replace(/,/g, ", ");
    } else if (!hasTimings()) {
      ex.innerHTML = `<div class="sync-note">Verse highlighting isn't set up for this recording yet. <button class="btn" id="startTiming">${DS.icons.timer} Time it as you listen</button></div>`;
    } else {
      ex.innerHTML = "";
    }
  }

  const roundTimings = () => Object.fromEntries(order.filter((id) => timings[id] != null).map((id) => [id, Math.round(timings[id] * 10) / 10]));

  function saveLocal() { DS.store.set(key(), roundTimings()); }

  function mark() {
    const v = song.verses[markIdx];
    if (!v) return;
    timings[v.id] = audio.currentTime;
    markIdx++;
    saveLocal();
    setCurrent(v.id);
    renderExtra();
  }

  function startTiming() {
    timingMode = true;
    timings = {};
    markIdx = 0;
    renderExtra();
    if (audio.paused) audio.play().catch(() => {});
    DS.flash("Timing mode: press T at the start of each verse");
  }

  function show() {
    bar.classList.add("show");
    document.body.classList.add("has-player");
  }

  function togglePlay() {
    show();
    if (audio.paused) audio.play().catch(() => DS.flash("Could not start audio"));
    else audio.pause();
  }

  function init(s) {
    song = s;
    if (!song.audio || !song.audio.src) return;
    order = song.verses.map((v) => v.id);
    loadTimings();
    audio = new Audio();
    audio.preload = "none";
    audio.src = song.audio.src;
    bar = $("#player");
    render();

    const playBtn = () => $("#pPlay", bar);
    audio.addEventListener("play", () => { playBtn().innerHTML = DS.icons.pause; playBtn().setAttribute("aria-label", "Pause"); });
    audio.addEventListener("pause", () => { playBtn().innerHTML = DS.icons.play; playBtn().setAttribute("aria-label", "Play"); });
    audio.addEventListener("timeupdate", () => {
      const d = audio.duration || 0;
      $("#pSeek", bar).value = d ? Math.round((audio.currentTime / d) * 1000) : 0;
      $("#pTimeLbl", bar).textContent = DS.fmtTime(audio.currentTime) + " / " + DS.fmtTime(d);
      if (!timingMode && hasTimings()) setCurrent(verseAt(audio.currentTime));
    });
    audio.addEventListener("waiting", () => ($("#pTimeLbl", bar).textContent = "loading…"));

    bar.addEventListener("click", (e) => {
      const t = e.target.closest("button");
      if (!t) return;
      switch (t.id) {
        case "pPlay": togglePlay(); break;
        case "pClose": audio.pause(); bar.classList.remove("show"); document.body.classList.remove("has-player"); setCurrent(null); break;
        case "pFollow":
          DS.prefs.follow = !DS.prefs.follow; DS.savePrefs();
          t.setAttribute("aria-pressed", DS.prefs.follow); t.style.color = DS.prefs.follow ? "var(--accent)" : "";
          DS.flash(DS.prefs.follow ? "Auto-scroll on" : "Auto-scroll off"); break;
        case "pTime": case "startTiming": timingMode ? (timingMode = false, loadTimings(), renderExtra()) : startTiming(); break;
        case "tMark": mark(); break;
        case "tUndo":
          markIdx = Math.max(0, markIdx - 1); delete timings[song.verses[markIdx].id]; saveLocal(); renderExtra(); break;
        case "tClear": timings = {}; markIdx = 0; DS.store.remove(key()); renderExtra(); break;
        case "tDone": timingMode = false; loadTimings(); renderExtra(); break;
        case "tCopy":
          navigator.clipboard?.writeText(JSON.stringify(roundTimings())).then(() => DS.flash("Timings copied"), () => DS.flash("Select the text and copy"));
          break;
      }
    });
    $("#pSeek", bar).addEventListener("input", (e) => {
      if (audio.duration) audio.currentTime = (e.target.value / 1000) * audio.duration;
    });
    document.addEventListener("keydown", (e) => {
      if (!timingMode || e.target.matches("input, textarea, select")) return;
      if (e.key === "t" || e.key === "T") { e.preventDefault(); mark(); }
    });

    DS.on("rendered", () => { if (current) { const el = document.getElementById("v-" + current); if (el) el.classList.add("playing"); } });
    DS.on("audio-toggle", togglePlay);
    DS.on("play-verse", (id) => {
      show();
      if (timings[id] != null) { audio.currentTime = timings[id]; audio.play().catch(() => {}); }
      else if (hasTimings()) DS.flash("This verse isn't timed yet");
      else { audio.play().catch(() => {}); DS.flash("Recording not timed yet; playing from the start"); }
    });

    if (new URLSearchParams(location.search).get("timing") === "1") { show(); startTiming(); }
  }

  DS.audio = { get el() { return audio; }, hasTimings: () => hasTimings() };
  DS.on("ready", init);
})(window.DS);
