/* Shared helpers: preferences, theme, icons, small formatting utilities. */
window.DS = window.DS || {};

(function (DS) {
  const PREF_KEY = "ds:prefs:v1";

  DS.defaults = {
    theme: "auto",          // auto | light | dark | diya
    scale: 1,               // body text scale
    origScale: 1,           // original-text scale
    script: "devanagari",   // original-text script
    translit: "simple",     // off | simple | iast | iast-hindi | itrans | hk
    showOrig: true,
    showMeaning: true,
    showBhava: true,
    showNotes: true,
    gloss: "tap",           // off | tap | interlinear
    follow: true            // auto-scroll with audio
  };

  DS.store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw == null ? fallback : JSON.parse(raw);
      } catch (e) { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage unavailable */ }
    },
    remove(key) {
      try { localStorage.removeItem(key); } catch (e) { /* ignore */ }
    }
  };

  DS.prefs = Object.assign({}, DS.defaults, DS.store.get(PREF_KEY, {}));
  DS.savePrefs = () => DS.store.set(PREF_KEY, DS.prefs);

  DS.applyTheme = function () {
    const root = document.documentElement;
    if (DS.prefs.theme === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", DS.prefs.theme);
    root.style.setProperty("--scale", DS.prefs.scale);
    root.style.setProperty("--orig-scale", DS.prefs.origScale);
  };

  DS.esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* Tiny inline markup: *em*, **strong**. Input is escaped first. */
  DS.md = (s) => DS.esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>");

  const DEVA_DIGITS = "०१२३४५६७८९";
  DS.devaNum = (n) => String(n).replace(/\d/g, (d) => DEVA_DIGITS[d]);

  DS.fmtTime = (t) => {
    if (!isFinite(t)) return "0:00";
    const m = Math.floor(t / 60), s = Math.floor(t % 60);
    return m + ":" + String(s).padStart(2, "0");
  };

  const I = (p) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${p}</svg>`;
  DS.icons = {
    settings: I('<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>'),
    recite: I('<path d="M12 3c-3 3-5 5.5-5 8.5a5 5 0 0 0 10 0C17 8.5 15 6 12 3z"/><path d="M12 14v7M8 21h8"/>'),
    play: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6.5" y="5" width="4" height="14" rx="1"/><rect x="13.5" y="5" width="4" height="14" rx="1"/></svg>',
    headphones: I('<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="7" rx="1.5"/><rect x="17" y="14" width="4" height="7" rx="1.5"/>'),
    close: I('<path d="M6 6l12 12M18 6L6 18"/>'),
    prev: I('<path d="M15 5l-7 7 7 7"/>'),
    next: I('<path d="M9 5l7 7-7 7"/>'),
    link: I('<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>'),
    copy: I('<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>'),
    playFrom: I('<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l5.5-3.5z" fill="currentColor"/>'),
    follow: I('<path d="M12 5v14M6 13l6 6 6-6"/>'),
    timer: I('<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9 2h6"/>'),
    reset: I('<path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.5"/><path d="M4 4v4.5h4.5"/>'),
    lotus: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M16 6c-2.5 3-3.5 6-3.5 9s1.2 6 3.5 8c2.3-2 3.5-5 3.5-8s-1-6-3.5-9z"/><path d="M16 23c-3-.2-6.5-1.8-8.5-5 1.5-1.3 3.5-1.8 5-1.5"/><path d="M16 23c3-.2 6.5-1.8 8.5-5-1.5-1.3-3.5-1.8-5-1.5"/><path d="M16 23c-4 .8-8.5 0-11.5-2.5M16 23c4 .8 8.5 0 11.5-2.5"/><circle cx="16" cy="27" r=".8" fill="currentColor"/></svg>'
  };

  DS.on = (name, fn) => document.addEventListener("ds:" + name, (e) => fn(e.detail));
  DS.emit = (name, detail) => document.dispatchEvent(new CustomEvent("ds:" + name, { detail }));

  DS.applyTheme();
})(window.DS);
