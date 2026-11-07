/* Verse illustrations: follows the verse being read. On wide screens it is a panel
   beside the text; on narrower screens it becomes a soft full-screen background.
   In recitation mode it fills the background behind the verse. */
(function (DS) {
  const $ = (s, el = document) => el.querySelector(s);
  let song, art, panel, imgs, cap, rImgs, current = null, rCurrent = null, ticking = false;

  const src = (id) => art.path + id + ".svg";
  const preload = (id) => { if (id) { const i = new Image(); i.src = src(id); } };

  // Cross-fade between two stacked <img> layers.
  function show(layers, id, alt) {
    const [a, b] = layers;
    const front = a.classList.contains("on") ? a : b;
    const back = front === a ? b : a;
    back.onload = () => { back.classList.add("on"); front.classList.remove("on"); };
    back.alt = alt || "";
    back.src = src(id);
  }

  function neighbours(id) {
    const i = song.verses.findIndex((v) => v.id === id);
    preload(song.verses[i + 1]?.id);
    preload(song.verses[i - 1]?.id);
  }

  function setVerse(id) {
    if (!id || id === current) return;
    current = id;
    const v = song.verses.find((x) => x.id === id);
    const caption = art.captions[id] || "";
    show(imgs, id, caption);
    cap.innerHTML = `<span class="alabel">${DS.esc(DS.verseLabel(v))}</span>${DS.esc(caption)}`;
    neighbours(id);
  }

  // The verse crossing 40% of the viewport height is the one being read.
  function pick() {
    ticking = false;
    if (!document.body.classList.contains("has-art")) return;
    const y = window.innerHeight * 0.4;
    const els = document.querySelectorAll("#verses .verse");
    let id = null;
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (r.top <= y) id = el.id.slice(2);
      else break;
    }
    setVerse(id || song.verses[0].id);
  }
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(pick); } };

  function apply() {
    const on = !!DS.prefs.showArt;
    document.body.classList.toggle("has-art", on);
    if (on) { current = null; pick(); }
    if (rCurrent && on) { const id = rCurrent; rCurrent = null; reciteVerse(id); }
  }

  function reciteVerse(id) {
    if (!DS.prefs.showArt || !id || id === rCurrent) return;
    rCurrent = id;
    show(rImgs, id, "");
    rImgs[0].parentElement.style.setProperty("--u", `url("${new URL(src(id), location.href).href}")`);
    neighbours(id);
  }

  function build() {
    panel = document.createElement("aside");
    panel.className = "art";
    panel.setAttribute("aria-label", "Verse illustration");
    panel.innerHTML = `<img class="on" alt=""><img alt=""><div class="acap"></div>`;
    document.body.prepend(panel);
    imgs = panel.querySelectorAll("img");
    cap = $(".acap", panel);

    const r = document.createElement("div");
    r.className = "rart";
    r.setAttribute("aria-hidden", "true");
    r.innerHTML = `<img class="on" alt=""><img alt="">`;
    $("#recite").prepend(r);
    rImgs = r.querySelectorAll("img");
  }

  DS.on("ready", (s) => {
    song = s;
    art = s.art;
    if (!art) return;
    build();
    apply();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
  });
  DS.on("rendered", () => { if (art) { current = null; onScroll(); } });
  DS.on("prefs", (e) => { if (art && e && e.name === "showArt") apply(); });
  DS.on("recite-verse", (id) => { if (art) reciteVerse(id); });
})(window.DS);
