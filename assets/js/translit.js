/* Script conversion and transliteration, built on the vendored Sanscript library.
   The Devanagari text in each song file is the single source of truth. */
(function (DS) {
  const S = window.Sanscript;

  // Scripts the original text can be shown in. `font` is the Google Fonts family to load on demand.
  DS.SCRIPTS = [
    { id: "devanagari", label: "Devanagari (देवनागरी)" },
    { id: "kannada", label: "Kannada (ಕನ್ನಡ)", font: "Noto Serif Kannada" },
    { id: "telugu", label: "Telugu (తెలుగు)", font: "Noto Serif Telugu" },
    { id: "tamil_superscripted", label: "Tamil (தமிழ், with superscripts)", font: "Noto Serif Tamil" },
    { id: "malayalam", label: "Malayalam (മലയാളം)", font: "Noto Serif Malayalam" },
    { id: "gujarati", label: "Gujarati (ગુજરાતી)", font: "Noto Serif Gujarati" },
    { id: "bengali", label: "Bengali (বাংলা)", font: "Noto Serif Bengali" },
    { id: "gurmukhi", label: "Gurmukhi (ਗੁਰਮੁਖੀ)", font: "Noto Serif Gurmukhi" },
    { id: "oriya", label: "Odia (ଓଡ଼ିଆ)", font: "Noto Serif Oriya" }
  ];

  // Transliteration choices shown under the original.
  DS.TRANSLITS = [
    { id: "off", label: "Off" },
    { id: "simple", label: "Simple (as sung)", hint: "Easy-to-read English spelling, as the hymn is commonly sung." },
    { id: "iast", label: "IAST (scholarly)", hint: "Letter-for-letter with diacritics; keeps every inherent 'a'." },
    { id: "iast-hindi", label: "IAST, Hindi pronunciation", hint: "IAST with the silent 'a' dropped, as in Hindi speech (an automatic approximation; compounds may differ)." },
    { id: "itrans", label: "ITRANS", hint: "ASCII-only scheme used for typing Indic text." },
    { id: "hk", label: "Harvard-Kyoto", hint: "ASCII-only scheme common in Sanskrit scholarship." }
  ];

  const loadedFonts = new Set();
  DS.ensureFont = function (scriptId) {
    const s = DS.SCRIPTS.find((x) => x.id === scriptId);
    if (!s || !s.font || loadedFonts.has(s.font)) return;
    loadedFonts.add(s.font);
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=" + encodeURIComponent(s.font) + ":wght@400;600&display=swap";
    document.head.appendChild(link);
  };

  const stripDanda = (t) => t.replace(/[।॥]/g, "").trim();

  /* ── Approximate Hindi/Awadhi schwa deletion ──
     Sanscript keeps every inherent "a" (carana). Spoken Hindi drops it at the end
     of a word (caran) and in the pattern V C_a C V (rām-candra). We mark deleted
     schwas with a virama in the Devanagari before transliterating. Compounds are
     not detected, so this is a close approximation, not a rule of grammar. */
  const AKSHARA = /((?:[क-हक़-य़]़?्)*[क-हक़-य़]़?)([ा-ौॢॣ्]?)([ँ-ः]?)|([ऄ-औ])([ँ-ः]?)|(.)/g;
  function syncopeWord(word) {
    const u = [];
    let m;
    AKSHARA.lastIndex = 0;
    while ((m = AKSHARA.exec(word))) {
      if (m[1]) u.push({ text: m[0], cons: true, cluster: m[1].includes("्"), schwa: !m[2] && !m[3], del: false, vowel: m[2] !== "्" });
      else u.push({ text: m[0], cons: false, cluster: false, schwa: false, del: false, vowel: !!m[4] });
    }
    const n = u.length;
    if (n < 2) return word;
    // A "full" vowel: a vowel sign or independent vowel (not an inherent a).
    const fullV = (x) => x && x.vowel && !x.del && !x.schwa;
    // medial: V̄ C(a) C V … → drop the a  (rāmacandra → rāmcandra, bisarāvai → bisrāvai)
    // Conservative: only after a full vowel, never before ह, never before the last syllable.
    for (let i = 1; i < n - 2; i++) {
      const x = u[i];
      if (!x.cons || !x.schwa || x.cluster) continue;
      const nx = u[i + 1];
      if (!nx.cons || !nx.vowel || nx.text.startsWith("ह")) continue;
      const pv = u[i - 1];
      // skip after a conjunct or independent vowel: usually a compound boundary (śrī-raghubīr, añjani-putra)
      if (fullV(pv) && pv.cons && !pv.cluster) x.del = true;
    }
    // final: drop the a unless the last consonant is a cluster (mitra, candra)
    const last = u[n - 1];
    if (last.cons && last.schwa && !last.cluster) last.del = true;
    return u.map((x) => (x.del ? x.text + "्" : x.text)).join("");
  }
  DS.syncope = (text) => text.split(/(\s+)/).map((w) => (/\s/.test(w) ? w : syncopeWord(w))).join("");

  const fixIAST = (s) => s.replace(/~/g, "m̐").replace(/r̤/g, "ṛ");
  // Sanscript expects precomposed nukta letters; Unicode NFC will not compose these.
  const NUKTA = { "क": "क़", "ख": "ख़", "ग": "ग़", "ज": "ज़", "ड": "ड़", "ढ": "ढ़", "फ": "फ़", "य": "य़" };
  // Sanscript 1.3.3 has no working roman mapping for ढ़; patch the passed-through letter.
  const fixRrh = (s, iast) => s.replace(/ढ़(्)?([aāiīuūeoṛ]?)/g, (m, vir, v) => (iast ? "ṛh" : "Rh") + (v || (vir ? "" : "a")));
  const composeNukta = (t) => t.replace(/([कखगजडढफय])़/g, (m, c) => NUKTA[c]);

  /** Convert Devanagari text to the chosen Indic script (or return as-is). */
  DS.toScript = function (deva, scriptId) {
    if (!scriptId || scriptId === "devanagari" || !S) return deva;
    const DEVA = /[ऀ-ॣॱ-ॿ]/;
    try {
      // Prefer precomposed nukta letters (Bengali ড়); fall back to dropping the nukta.
      let out = S.t(composeNukta(deva), "devanagari", scriptId);
      if (DEVA.test(out)) out = S.t(deva.normalize("NFD"), "devanagari", scriptId).replace(/़/g, "");
      // Gurmukhi has no ष or vocalic ṛ: use the conventional ਸ਼ and ਰਿ.
      if (scriptId === "gurmukhi") out = out.replace(/ष/g, "ਸ਼").replace(/ृ/g, "੍ਰਿ").replace(/ऋ/g, "ਰਿ");
      return out;
    } catch (e) { return deva; }
  };

  /** Roman transliteration of Devanagari text with a given scheme id (not "simple"). */
  DS.toRoman = function (deva, scheme) {
    if (!S) return "";
    const text = composeNukta(stripDanda(deva));
    try {
      if (scheme === "iast-hindi") return fixRrh(fixIAST(S.t(DS.syncope(text), "devanagari", "iast")), true);
      if (scheme === "iast") return fixRrh(fixIAST(S.t(text, "devanagari", "iast")), true);
      return fixRrh(S.t(text, "devanagari", scheme), false);
    } catch (e) { return ""; }
  };

  /** Line-level transliteration: hand-written `roman` for "simple", Sanscript otherwise. */
  DS.lineTranslit = function (line, scheme) {
    if (scheme === "off") return "";
    if (scheme === "simple") return line.roman || DS.toRoman(line.deva, "iast-hindi");
    return DS.toRoman(line.deva, scheme);
  };

  /** Per-word transliterations, aligned with line.words. */
  DS.wordTranslits = function (line, scheme) {
    if (scheme === "simple" && line.roman) {
      const toks = line.roman.replace(/[,;.!?]/g, " ").split(/\s+/).filter(Boolean);
      if (toks.length === line.words.length) return toks;
    }
    const sch = scheme === "off" || scheme === "simple" ? "iast-hindi" : scheme;
    return line.words.map((w) => DS.toRoman(w.deva, sch));
  };
})(window.DS);
