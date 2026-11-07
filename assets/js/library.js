/* Collection home: renders a card per song from songs/catalog.json. */
(function (DS) {
  const $ = (s) => document.querySelector(s);

  function themeSeg() {
    const opts = [["auto", "Auto"], ["light", "Light"], ["diya", "Diyā"], ["dark", "Dark"]];
    const el = $("#themeSeg");
    el.innerHTML = opts.map(([v, l]) => `<button type="button" data-val="${v}" aria-pressed="${DS.prefs.theme === v}">${l}</button>`).join("");
    el.onclick = (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      DS.prefs.theme = b.dataset.val;
      DS.savePrefs();
      DS.applyTheme();
      themeSeg();
    };
  }

  async function boot() {
    $("#orn").innerHTML = DS.icons.lotus;
    themeSeg();
    let songs = [];
    try {
      songs = await (await fetch("songs/catalog.json")).json();
    } catch (e) {
      $("#cards").innerHTML = `<p>Could not load the song list. Serve this folder with <code>python3 -m http.server</code> and open <code>http://localhost:8000</code>.</p>`;
      return;
    }
    $("#cards").innerHTML = songs.map((s) => `
      <a class="card" href="song.html?id=${encodeURIComponent(s.id)}">
        <div class="deva">${DS.esc(s.title.deva)}</div>
        <div class="en">${DS.esc(s.title.en)}</div>
        <div class="meta">${DS.esc(s.author)} · ${DS.esc(s.language)} · ${DS.esc(s.period)} · ${s.verses} verses</div>
        <p>${DS.esc(s.summary)}</p>
      </a>`).join("") + `
      <div class="card soon" aria-hidden="true">
        <div class="deva">आगामी</div>
        <div class="en">More songs coming</div>
        <p>Stotras, bhajans and kīrtans in Sanskrit and other Indian languages.</p>
      </div>`;
  }
  document.addEventListener("DOMContentLoaded", boot);
})(window.DS);
