# 岡村孝子 Takako Okamura — Slide-by-Slide Discography Deck (Astro)

A presentation-style web app: **one slide per release, 52 slides** in chronological order
(34 singles + 18 studio albums, solo career 1985–2019). Each slide shows **cover art**,
release details, and a **playable YouTube sample**, so you can present the complete
discography song by song — and screen-record it into a presentation video.

Built with **Astro** (static output, zero-JS by default except the small deck controller).

## Run it

```sh
cd /Users/prayushkale/projects/takako_okamura
npm install
npm run dev      # http://localhost:4321/
```

Production build:

```sh
npm run build     # outputs to dist/
npm run preview
```

## How to present

- **Prev / Next / slide dropdown / ← → keys / Space / Home / End** — move slide by slide.
- **Play a sample** — every slide with a curated `youtubeId` embeds the video inline;
  slides without one show an "Open on YouTube ↗" search fallback
  (`岡村孝子 <title>`).
- **From chorus (C)** — start every sample at the song's chorus instead of the intro.
  Applies to the big `▶ Play` button and to every track `▶`, and is remembered across
  reloads. Off by default.
- **Album slides** list every track; tracks with videos link straight to that video.
- **Auto-advance (8s)** — turn on for hands-free presenting; stops at the last slide
  or the moment you navigate manually.
- **Present ⛶** — fullscreen the stage for projecting / screen-recording.
- **Deep links** — `#slide-1` … `#slide-52` jump straight to a release.

## Making the presentation video

1. `npm run dev`, open the deck, click **Present ⛶**.
2. Turn **Auto-advance** on (or step manually with →).
3. Screen-record (QuickTime / OBS), playing one sample per slide.
4. 24 of 52 slides already have curated YouTube samples
   (15 singles + 9 albums via their first playable track).

## Cover art

All 52 slides ship with real jacket art in `public/covers/<slide-id>.jpg`
(one file per release — `<date>-s-<slug>.jpg` for singles, `<date>-a-<slug>.jpg`
for albums). The base set is the artist's own label scans from the
[official discography](https://okamuratakako.com/discography/) — complete and
authoritative, but only 250px. 18 releases are upgraded to 1400px Apple Music
artwork where a perceptual match confirmed it is the same jacket.

`src/components/Cover.astro` picks up any `.jpg / .jpeg / .png / .webp` at
`public/covers/<slide-id>.*` automatically at build time — no code changes
needed. Delete a file to fall back to the generated placeholder (hue derived
from the title). Art is shown whole (`object-fit: contain`) over a blurred copy
of itself, so the non-square 8cm-CD single sleeves are not cropped.

## Adding a YouTube sample

1. Search `岡村孝子 <song title>` on YouTube
   (prefer the official channel: `UCvCKc4evIYxHjLur6xbZecw`).
2. Copy the 11-character video ID from the URL (`watch?v=XXXXXXXXXXX`).
3. Paste it as `youtubeId` for that single or album track in `src/data/discography.json`.
4. Rebuild — the slide embed + "Open on YouTube" link update automatically.

## Starting samples from the chorus

`src/data/chorus.json` holds the second each song's chorus begins, keyed by YouTube id:

```json
"UpJ_rIZOif8": { "start": 69, "conf": 0.17, "method": "ssm", "duration": 281 }
```

- `ssm` — found by `scripts/detect-chorus.py` (see below)
- `heuristic` — download or analysis failed, so it falls back to `0.3 × duration`
- `manual` — corrected by hand; **never overwritten** unless you pass `--force`

`chorus-review.md` lists every song with a `▶` link that jumps straight to the detected
moment, plus the lengths, so you can skim for wrong ones.

The times are algorithmic, not hand-checked: most land within a few seconds of the chorus,
a minority need a nudge. `conf` says how sharply the section stood out — songs near the
bottom of `chorus-review.md` are the ones worth checking first.

**Fixing a time:** open `chorus-review.md`, click ▶, and if the chorus is not starting,
note the real time, then edit that id in `src/data/chorus.json` — set `"start"` and change
`"method"` to `"manual"`. Rebuild. No re-analysis needed.

**Re-running the detector:**

```sh
python3 -m venv .venv && .venv/bin/pip install librosa soundfile numpy
npm run chorus:detect                          # every song still missing a time
npm run chorus:detect -- --limit 5             # quick sanity check
npm run chorus:detect -- --force --only ID123  # redo specific songs
npm run chorus:detect -- --keep-audio          # keep the audio in .cache for faster re-runs
npm run chorus:detect -- --docs-only           # regenerate chorus-review.md
```

How it works: each song's audio is downloaded with `yt-dlp` (a small mono flac in
`.cache/`, deleted again after analysis — pass `--keep-audio` to keep it), beat tracked,
reduced to beat-synchronous chroma, and compared against itself with a self-similarity
matrix. The chorus is the section that repeats the most *and* is loudest, restricted to
windows after the intro and before the final quarter; the start is then snapped to the
nearest strong onset. Results are written after every song, so a killed run keeps
everything it already finished. Songs YouTube blocks (bot check, region) are listed
under "Not analysed" in `chorus-review.md` — rerun those with
`--cookies-from-browser chrome`.

## Files

- `src/pages/index.astro` — the deck page (hero, controls, stage, filmstrip).
- `src/lib/slides.ts` — slide model: flattens `discography.json` into 52
  chronological release slides (singles + albums interleaved by date).
- `src/components/Cover.astro` — cover art (real jacket if present, placeholder if not).
- `src/components/SlideCard.astro` — per-slide details + YouTube sample + tracklist.
- `src/scripts/deck.ts` — slide controller (nav, dropdown, autoplay, fullscreen, hash).
- `src/layouts/Base.astro` — HTML shell + global theme.
- `src/data/discography.json` — dataset: 35 years, 34 singles, 18 albums, 168 album tracks.
- `src/data/chorus.json` — where each song's chorus starts (see above).
- `scripts/detect-chorus.py` — one-off chorus detector that writes `chorus.json`
  and `chorus-review.md`.
- `public/covers/` — drop real jacket art here (`<slide-id>.jpg`).
- Legacy plain-HTML version (`index.html`, `styles.css`, `js/`, `data/`) is superseded
  by this Astro app and can be deleted.

## Notes & caveats

- Some 80s/90s uploads may be region-blocked or have embedding disabled — the per-slide
  YouTube search/open link is always there as backup.
- Browsers block autoplay before user interaction, so samples always start from a click.
- Out of scope: Aming era (1982–83 待つわ etc.) and best-of compilations
  (After Tone, Ballade, DO MY BEST…).

## Sources

- [Takako Okamura — Wikipedia](https://en.wikipedia.org/wiki/Takako_Okamura)
- [岡村孝子 — Wikipedia (discography tables)](https://ja.wikipedia.org/wiki/%E5%B2%A1%E6%9D%91%E5%AD%9D%E5%AD%90)
- [Official discography — okamuratakako.com](https://okamuratakako.com/discography/)
- [Official YouTube channel](https://www.youtube.com/channel/UCvCKc4evIYxHjLur6xbZecw)
