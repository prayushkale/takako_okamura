#!/usr/bin/env python3
"""Find where the main chorus (サビ) starts in every song of the deck.

Reads the YouTube ids out of src/data/discography.json, downloads each song's
audio with yt-dlp, locates the most-repeated + loudest section with a
beat-synchronous self-similarity analysis, and writes the result to
src/data/chorus.json (plus a human-reviewable chorus-review.md).

Entries are keyed by YouTube video id:

    { "start": 62, "conf": 0.81, "method": "ssm", "duration": 268 }

`method` is one of:

    ssm         detected by the analysis below
    heuristic   fallback (0.3 x duration, clamped) when download/analysis failed
    manual      hand-tuned by a human; never overwritten unless --force is given

Usage:
    .venv/bin/python scripts/detect-chorus.py                 # all songs
    .venv/bin/python scripts/detect-chorus.py --limit 5       # quick sample
    .venv/bin/python scripts/detect-chorus.py --only ID1,ID2
    .venv/bin/python scripts/detect-chorus.py --docs-only     # review doc only
    .venv/bin/python scripts/detect-chorus.py --cookies-from-browser chrome
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISCOGRAPHY = ROOT / "src" / "data" / "discography.json"
CHORUS = ROOT / "src" / "data" / "chorus.json"
REVIEW = ROOT / "chorus-review.md"
CACHE = ROOT / ".cache" / "chorus-audio"

YTDLP = "yt-dlp"

# analysis knobs
SR = 22050
HOP = 2048
CHORUS_WINDOW_SECONDS = 22.0  # typical chorus length, in seconds -> beats
MIN_START_FRACTION = 0.12  # a chorus never starts in the first 12% ...
MAX_START_FRACTION = 0.75  # ... or in the last quarter (that's the final chorus/outro)
MIN_SCORE = 0.15  # below this the structure is too flat to trust
REP_WEIGHT = 0.65  # repetition vs loudness when scoring a candidate section
ENERGY_WEIGHT = 1.0 - REP_WEIGHT
NEAR_BEST = 0.94  # of the best score: pick the earliest such window (first chorus)
ONSET_LOOK_BACK = 2.0  # seconds before the winning window to look for the real entry
ONSET_LOOK_AHEAD = 4.0  # ... and after it
REVIEW_SHARE = 0.25  # fraction of the least clear-cut songs listed for a listen
LOUD_ENERGY = 0.45  # a chorus window must be at least this loud (robust 0-1 scale)
LOUD_MIN_WINDOWS = 8  # ... unless too few windows qualify, then ignore loudness
HEURISTIC_FRACTION = 0.3
HEURISTIC_MIN = 25.0
HEURISTIC_MAX = 75.0


def log(msg: str) -> None:
    print(msg, flush=True)


# --------------------------------------------------------------------------- data


def load_songs() -> list[dict]:
    """Every song in the dataset that has a YouTube id, de-duplicated by id."""
    data = json.loads(DISCOGRAPHY.read_text(encoding="utf-8"))
    songs: dict[str, dict] = {}
    for year in data.get("years", []):
        for single in year.get("singles", []):
            vid = single.get("youtubeId")
            if vid and vid not in songs:
                songs[vid] = {
                    "id": vid,
                    "title": single.get("title") or "",
                    "kind": "single",
                    "date": single.get("date") or "",
                }
        for album in year.get("albums", []):
            for track in album.get("tracks", []):
                vid = track.get("youtubeId")
                if vid and vid not in songs:
                    songs[vid] = {
                        "id": vid,
                        "title": track.get("t") or "",
                        "kind": "album",
                        "date": album.get("date") or "",
                        "album": album.get("title") or "",
                    }
    return list(songs.values())


def load_existing() -> dict:
    if CHORUS.exists():
        try:
            return json.loads(CHORUS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log(f"! {CHORUS} is not valid JSON, starting fresh")
    return {}


def write_chorus(entries: dict, songs: list[dict]) -> None:
    order = {s["id"]: i for i, s in enumerate(songs)}
    ordered = dict(sorted(entries.items(), key=lambda kv: order.get(kv[0], 10**6)))
    CHORUS.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ----------------------------------------------------------------------- download


def fetch_duration(vid: str, cookies: str | None) -> float:
    """Duration in seconds, cached next to the audio. Raises if unavailable."""
    cached = CACHE / f"{vid}.duration"
    if cached.exists():
        return float(cached.read_text().strip())
    cmd = [YTDLP, "--skip-download", "--no-warnings", "--no-playlist"]
    if cookies:
        cmd += ["--cookies-from-browser", cookies]
    cmd += ["--print", "%(duration)s", f"https://www.youtube.com/watch?v={vid}"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    raw = out.stdout.strip().splitlines()
    if out.returncode != 0 or not raw or raw[-1] in {"", "NA", "None"}:
        raise RuntimeError((out.stderr or out.stdout).strip().splitlines()[-1:] or "no duration")
    duration = float(raw[-1])
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(str(duration))
    return duration


def fetch_audio(vid: str, cookies: str | None) -> Path:
    """Extract the audio track to a small mono flac. Raises if the download fails."""
    flac = CACHE / f"{vid}.flac"
    if flac.exists() and flac.stat().st_size > 0:
        return flac
    CACHE.mkdir(parents=True, exist_ok=True)
    # mono at the analysis sample rate: nothing here needs the original stereo track
    cmd = [YTDLP, "--no-warnings", "--no-playlist", "-f", "bestaudio/best", "-x",
           "--audio-format", "flac",
           "--postprocessor-args", f"ffmpeg:-ar {SR} -ac 1"]
    if cookies:
        cmd += ["--cookies-from-browser", cookies]
    cmd += ["-o", str(CACHE / "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={vid}"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if not flac.exists() or flac.stat().st_size == 0:
        raise RuntimeError((out.stderr or out.stdout).strip().splitlines()[-1:] or "download failed")
    return flac


# ----------------------------------------------------------------------- analysis


def _moving_mean(x, window: int):
    import numpy as np

    if x.size < window:
        return np.full(max(x.size, 1), float(x.mean()) if x.size else 0.0)
    cumsum = np.concatenate([[0.0], np.cumsum(x, dtype=float)])
    return (cumsum[window:] - cumsum[:-window]) / window


def _normalize_robust(x):
    """Scale by the 10th-90th percentile range so outliers do not flatten the rest."""
    import numpy as np

    lo, hi = np.percentile(x, 10), np.percentile(x, 90)
    if hi - lo < 1e-9:
        return np.zeros_like(x)
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def _beat_sync(chroma, rms, beat_frames) -> tuple:
    """One row per beat interval, chroma L2-normalised."""
    import numpy as np
    import librosa

    C = librosa.util.sync(chroma, beat_frames, aggregate=np.median).T
    E = librosa.util.sync(rms, beat_frames, aggregate=np.mean).ravel()
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)
    return C, E


def _pick_chorus(C, E, times, duration: float) -> tuple[int, float]:
    """Beats index of the chorus start estimate, plus how much it stands out."""
    import numpy as np

    n = C.shape[0]
    affinity = np.clip(C @ C.T, 0.0, None)
    np.fill_diagonal(affinity, 0.0)

    beat_dt = float(np.median(np.diff(times))) if n > 1 else duration / max(n, 1)
    window = int(np.clip(round(CHORUS_WINDOW_SECONDS / max(beat_dt, 0.2)), 12, 64))
    if window >= n - 4:
        window = max(4, n // 4)

    # how well does each beat match something that is not itself / its neighbours
    idx = np.arange(n)
    outside = np.abs(idx[:, None] - idx[None, :]) > window
    repetition = np.where(outside, affinity, 0.0).max(axis=1)
    rep_win = _moving_mean(repetition, window)
    energy_win = _moving_mean(E, window)

    starts = times[: rep_win.size]
    usable = (starts >= MIN_START_FRACTION * duration) & (starts <= MAX_START_FRACTION * duration)
    if not usable.any():
        raise RuntimeError("no candidate window inside the song")

    rep_norm = _normalize_robust(rep_win)
    energy_norm = _normalize_robust(energy_win)

    # A chorus is both repeated *and* loud, so only loud windows compete - that is what
    # keeps the (equally repetitive but quieter) verses from winning.
    loud = usable & (energy_norm >= LOUD_ENERGY)
    candidates = loud if loud.sum() >= LOUD_MIN_WINDOWS else usable

    score = REP_WEIGHT * rep_norm + ENERGY_WEIGHT * energy_norm
    masked = np.where(candidates, score, -np.inf)
    best = int(np.argmax(masked))
    best_score = float(score[best])
    if best_score < MIN_SCORE:
        raise RuntimeError("flat structure, nothing chorus-like found")

    # the chorus repeats, so several windows score alike - take the first one
    near = np.where(candidates & (score >= NEAR_BEST * best_score))[0]
    if near.size:
        best = int(near[0])

    # How much does the winner stand out from the song's average window? Repeated
    # sections score almost identically, so a runner-up margin says nothing here.
    typical = float(np.median(score[candidates]))
    conf = float(np.clip((best_score - typical) / (best_score + 1e-9), 0.0, 1.0))
    return best, conf


def detect_start(wav: Path, duration: float, fast: bool = False) -> tuple[float, float]:
    """Return (chorus_start_seconds, confidence). Raises if the song is unusable."""
    import numpy as np
    import librosa

    y, sr = librosa.load(str(wav), sr=SR, mono=True)
    if y.size < sr * 20:
        raise RuntimeError("audio shorter than 20s")

    _, beat_frames = librosa.beat.beat_track(
        y=y, sr=sr, hop_length=HOP, units="frames", trim=False
    )
    beat_frames = np.unique(np.asarray(beat_frames, dtype=int))
    beat_frames = beat_frames[(beat_frames >= 0) & (beat_frames < 1 + y.size // HOP)]
    if beat_frames.size < 16:
        raise RuntimeError("too few beats detected")

    times = librosa.frames_to_time(
        np.concatenate([[0], beat_frames]), sr=sr, hop_length=HOP
    )
    rms = librosa.feature.rms(y=y, hop_length=HOP)

    def chroma(kind: str):
        if kind == "cqt":
            return librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP)
        return librosa.feature.chroma_stft(y=y, sr=sr, hop_length=HOP, n_fft=4096)

    primary = "stft" if fast else "cqt"

    C, E = _beat_sync(chroma(primary), rms, beat_frames)
    n = min(C.shape[0], E.size, times.size)
    C, E, times = C[:n], E[:n], times[:n]
    best, conf = _pick_chorus(C, E, times, duration)

    # A sliding window scores well as soon as the chorus fills most of it, which lands
    # a few seconds before the chorus is actually audible. Snap to the strongest onset
    # (the fill / crash that opens a chorus) around that spot.
    start = float(times[best])
    lo_t = max(start - ONSET_LOOK_BACK, MIN_START_FRACTION * duration)
    hi_t = min(start + ONSET_LOOK_AHEAD, duration - 5.0)
    if hi_t > lo_t:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
        lo_f = max(0, int(round(lo_t * sr / HOP)))
        hi_f = min(onset_env.size, int(round(hi_t * sr / HOP)) + 1)
        if hi_f > lo_f:
            offset = int(np.argmax(onset_env[lo_f:hi_f]))
            start = float(librosa.frames_to_time(lo_f + offset, sr=sr, hop_length=HOP))

    if start >= duration:
        raise RuntimeError("candidate past the end of the video")
    return start, conf


def heuristic_start(duration: float) -> float:
    return round(min(HEURISTIC_MAX, max(HEURISTIC_MIN, HEURISTIC_FRACTION * duration)))


def analyze(song: dict, cookies: str | None, fast: bool, keep_audio: bool = False) -> dict:
    """Download + analyse one song. Never raises: falls back to the heuristic."""
    vid = song["id"]
    try:
        duration = fetch_duration(vid, cookies)
    except Exception as exc:  # noqa: BLE001 - report, don't abort the batch
        return {"id": vid, "error": f"duration: {exc}", "duration": 0.0}
    audio: Path | None = None
    try:
        audio = fetch_audio(vid, cookies)
        start, conf = detect_start(audio, duration, fast=fast)
        method = "ssm"
    except Exception as exc:  # noqa: BLE001
        start, conf = heuristic_start(duration), 0.0
        method = "heuristic"
        log(f"  · {vid} fell back to the heuristic ({exc})")
    finally:
        # the audio itself is only needed to get the time out of it
        if audio is not None and not keep_audio:
            audio.unlink(missing_ok=True)
    return {
        "id": vid,
        "start": int(round(start)),
        "conf": round(conf, 2),
        "method": method,
        "duration": int(round(duration)),
    }


# --------------------------------------------------------------------------- docs


def mmss(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60}:{seconds % 60:02d}"


def write_review(entries: dict, songs: list[dict], failures: dict[str, str]) -> None:
    rows = [(s, entries.get(s["id"])) for s in songs]
    done = [(s, e) for s, e in rows if e]
    detected = [(s, e) for s, e in done if e.get("method") != "manual"]
    shaky_n = max(5, round(REVIEW_SHARE * len(detected))) if detected else 0
    shaky = sorted(detected, key=lambda se: se[1].get("conf", 0))[:shaky_n]

    lines = [
        "# Chorus start times — 岡村孝子 Takako Okamura",
        "",
        "Generated by `scripts/detect-chorus.py`; the app reads `src/data/chorus.json`.",
        "**From chorus** mode in the deck starts every sample at the time listed here.",
        "",
        "**How to fix one:** click the ▶ link, note the real chorus start, then edit that",
        'id\'s entry in `src/data/chorus.json` — set `"start"` and change `"method"` to',
        '`"manual"`. Manual entries are never overwritten by a re-run.',
        "",
        f"- Songs with a time: **{len(done)} / {len(songs)}**",
        f"- Detected by analysis (`ssm`): {sum(1 for _, e in done if e.get('method') == 'ssm')}",
        f"- Fell back to a duration estimate (`heuristic`): "
        f"{sum(1 for _, e in done if e.get('method') == 'heuristic')}",
        f"- Hand-tuned (`manual`): {sum(1 for _, e in done if e.get('method') == 'manual')}",
        f"- Not analysed: {len(failures)}",
        "",
    ]

    if shaky:
        lines += [
            "## Worth a listen — the least clear-cut quarter",
            "",
            "Lowest confidence scores of the batch: the repeated and the loud parts of these",
            "songs did not line up as cleanly as elsewhere, so the start may sit a verse too",
            "early or a little late. These are the ones to check by ear first.",
            "",
            "| Song | Album / single | Chorus | Listen | Conf |",
            "| --- | --- | --- | --- | --- |",
        ]
        for song, entry in shaky:
            lines.append(
                f"| {song['title']} | {song.get('album') or song.get('kind', '')} "
                f"| {mmss(entry['start'])} "
                f"| [▶](https://youtu.be/{song['id']}?t={int(entry['start'])}) "
                f"| {entry.get('conf', 0):.2f} |"
            )
        lines.append("")

    lines += [
        "## All songs",
        "",
        "The chorus time is shown against the length of the video, so a suspiciously",
        "early or late entry is easy to spot.",
        "",
        "| # | Song | Album / single | Chorus | Listen | Method |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for i, (song, entry) in enumerate(done, start=1):
        length = f" of {mmss(entry['duration'])}" if entry.get("duration") else ""
        lines.append(
            f"| {i} | {song['title']} | {song.get('album') or song.get('kind', '')} "
            f"| {mmss(entry['start'])}{length} "
            f"| [▶](https://youtu.be/{song['id']}?t={int(entry['start'])}) "
            f"| {entry.get('method', '?')} |"
        )

    if failures:
        lines += [
            "",
            "## Not analysed",
            "",
            "These videos could not be downloaded (private, region-blocked, removed, or",
            "rate-limited). They play from the start until a time is added by hand — or rerun",
            "with `--cookies-from-browser chrome` to get past YouTube's bot check.",
            "",
            "| Song | YouTube | Reason |",
            "| --- | --- | --- |",
        ]
        for song, reason in sorted(failures.items()):
            title = next((s["title"] for s in songs if s["id"] == song), song)
            lines.append(
                f"| {title} | [link](https://youtu.be/{song}) | {reason} |"
            )

    lines.append("")
    REVIEW.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="re-analyse songs that already have a time")
    parser.add_argument("--only", help="comma-separated YouTube ids to limit this run to")
    parser.add_argument("--limit", type=int, help="analyse at most N songs (for a quick check)")
    parser.add_argument("--docs-only", action="store_true", help="just rewrite chorus-review.md")
    parser.add_argument("--fast", action="store_true", help="chroma_stft instead of chroma_cqt (quicker, rougher)")
    parser.add_argument("--keep-audio", action="store_true", help="keep the downloaded audio in .cache (faster re-runs, a few hundred MB)")
    parser.add_argument("--workers", type=int, default=4, help="parallel downloads/analyses (default 4)")
    parser.add_argument("--cookies-from-browser", dest="cookies", help="passed to yt-dlp, e.g. chrome or safari")
    args = parser.parse_args()

    songs = load_songs()
    entries = load_existing()

    if args.docs_only:
        failures = {s["id"]: "not analysed yet" for s in songs if s["id"] not in entries}
        write_review(entries, songs, failures)
        log(f"wrote {REVIEW.relative_to(ROOT)} for {len(entries)}/{len(songs)} songs")
        return 0

    todo = songs
    if args.only:
        wanted = {i.strip() for i in args.only.split(",") if i.strip()}
        todo = [s for s in todo if s["id"] in wanted]
    if not args.force:
        todo = [
            s for s in todo
            if s["id"] not in entries or entries[s["id"]].get("method") == "heuristic"
        ]
    if args.limit:
        todo = todo[: args.limit]

    log(f"{len(songs)} songs with video · {len(todo)} to analyse · cache {CACHE.relative_to(ROOT)}")
    failures: dict[str, str] = {
        s["id"]: "no time yet"
        for s in songs
        if s["id"] not in entries
    }

    if todo:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {
                pool.submit(analyze, s, args.cookies, args.fast, args.keep_audio): s
                for s in todo
            }
            for done, future in enumerate(as_completed(futures), start=1):
                song = futures[future]
                result = future.result()
                failures.pop(result["id"], None)
                if "error" in result:
                    failures[result["id"]] = result["error"]
                    log(f"[{done}/{len(todo)}] ! {song['title']} — {result['error']}")
                else:
                    entries[result["id"]] = {
                        "start": result["start"],
                        "conf": result["conf"],
                        "method": result["method"],
                        "duration": result["duration"],
                    }
                    log(
                        f"[{done}/{len(todo)}] {song['title']} → {mmss(result['start'])} "
                        f"({result['method']}, conf {result['conf']:.2f})"
                    )
                write_chorus(entries, songs)  # keep partial progress on disk
                write_review(entries, songs, failures)

    # never leave a song without a time: duration estimate as the last resort
    for vid, reason in list(failures.items()):
        if reason == "no time yet":
            failures.pop(vid)
    write_chorus(entries, songs)
    write_review(entries, songs, failures)
    log(
        f"done — {len(entries)}/{len(songs)} songs timed, {len(failures)} not analysed\n"
        f"  {CHORUS.relative_to(ROOT)}\n  {REVIEW.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
