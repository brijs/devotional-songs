# Devotional Songs

A small, static website for reading devotional songs slowly: original text, transliteration,
word-by-word meaning with Sanskrit roots (dhātu), verse meanings, short reflections, and the
history and legends behind each song.

The first song is the **Shri Hanuman Chalisa** (Goswami Tulsidas, Awadhi).

## Run it

The pages load song data with `fetch`, so open them through a local server (not `file://`):

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

It is plain HTML/CSS/JS with no build step, so it can be hosted as-is on GitHub Pages or any static host.

## Features

- **Layers you can toggle:** original text, transliteration, English meaning, reflection (bhāva), and notes.
- **Word-by-word:** tap a word for its meaning and root, or switch to *interlinear* mode to show a gloss under every word.
- **Script of the original:** Devanagari, Kannada, Telugu, Tamil, Malayalam, Gujarati, Bengali, Gurmukhi or Odia.
  These are generated from the Devanagari with [Sanscript](https://github.com/indic-transliteration/sanscript.js).
- **Transliteration:** Simple (as sung), IAST, IAST with Hindi pronunciation (the silent "a" dropped), ITRANS or Harvard-Kyoto.
- **Themes:** Auto, Light, Diyā (warm parchment) and Dark. Separate size controls for the body text and the original text.
- **Recite mode:** one verse at a time in large type, navigated with the keyboard, swipes or taps. A mala-bead counter tracks
  complete recitations toward a target (1, 3, 7, 11, 21, 100 or 108), and the screen stays awake.
- **Audio with verse highlighting:** a sticky player. Once a recording is timed, the current verse is highlighted and
  scrolled into view, and each verse has a "play from here" button.

All preferences are stored in your browser's `localStorage`.

## Audio and timing a recording

The Hanuman Chalisa page streams a live kirtan recording from the Internet Archive:

> *Shri Hanuman Chalisa*, Sri Raman Bihari Das Babaji and devotees, Stroud, UK, 2 Aug 2014.
> [archive.org](https://archive.org/details/SriRamanBihariDasBabaji02-08-2014KirtanStroudUk) ·
> [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)

The licence allows non-commercial sharing of the unmodified recording with attribution. The file is streamed directly
from archive.org and is not stored or altered here. If this site ever becomes commercial, replace the recording.

**The verse timings are not filled in yet.** To create them:

1. Open the song, press **Listen**, then the ⏱ button (or open `song.html?id=hanuman-chalisa&timing=1`).
2. Press **T** (or tap **Mark**) as each verse begins.
3. The timings take effect in your browser immediately. To share them with everyone, click **Copy JSON** and paste the
   result into `"audio": { "timings": { ... } }` in `songs/hanuman-chalisa.json`.

## Adding a song

1. Create `songs/<id>.json` (copy `hanuman-chalisa.json` as a template).
2. Add an entry to `songs/catalog.json`.
3. Run `python3 tools/validate.py`.

### Song schema (summary)

```jsonc
{
  "id": "hanuman-chalisa",
  "title": { "deva": "…", "en": "…", "iast": "…" },
  "language": "Awadhi", "script": "devanagari",
  "author": { "name": "…", "dates": "…" },
  "composed": "…",
  "epigraph": { "deva": "…", "en": "…" },               // optional
  "about": [ { "heading": "…", "tag": "history|legend|tradition|overview|trivia", "body": ["paragraph", "…"] } ],
  "sources": [ { "label": "…", "url": "…" } ],
  "audio": null | { "src", "title", "artist", "recorded", "license", "licenseUrl", "sourceUrl", "timings": { "<verseId>": seconds } },
  "sections": [ { "id": "opening", "label": "Opening Dohas", "deva": "दोहा" } ],
  "verses": [ {
    "id": "c1", "section": "chaupais", "type": "doha|chaupai|shloka|pada", "number": 1,
    "lines": [ {
      "deva": "जय हनुमान ज्ञान गुन सागर ।",          // source of truth for every script and transliteration
      "roman": "Jai Hanuman gyan gun sagar",        // hand-written "as sung" form, one token per word
      "words": [ { "deva": "जय", "gloss": "victory", "root": "Skt. jaya ← √ji, to conquer" } ]
    } ],
    "meaning": { "en": "…" },                        // keyed by language: add "hi", "kn", … later
    "bhava":   { "en": "…" },                        // optional reflection
    "notes":   ["…"]                                 // optional
  } ]
}
```

Rules checked by `tools/validate.py`:
- The words of each line, joined with spaces, must equal the line's `deva` text (ignoring punctuation).
- `roman` must have one token per word. Join compounds with a hyphen (`Pavan-kumar`).

Text in `about`, `meaning`, `bhava` and `notes` supports `*italic*` and `**bold**`.

## Layout

```
index.html              collection home
song.html               reader (song.html?id=<id>)
assets/css/styles.css   theme tokens, typography and layout
assets/js/common.js     preferences, theme, icons and helpers
assets/js/translit.js   script conversion and transliteration (Sanscript + Hindi schwa deletion)
assets/js/reader.js     verses, word popovers and settings drawer
assets/js/audio-sync.js player, verse highlighting and the timing helper
assets/js/recite.js     recitation mode and mala counter
assets/vendor/          Sanscript 1.3.3 (MIT)
songs/                  catalog.json and one JSON file per song
tools/validate.py       data checks
```
