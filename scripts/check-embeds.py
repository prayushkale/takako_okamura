#!/usr/bin/env python3
"""Find deck samples that YouTube refuses to embed, so no slide shows a dead player.

An uploader can switch off "playback on other websites". Such a video still plays
on youtube.com, but every third-party embed — this deck included — receives
"Playback on other websites has been disabled by the video owner" in place of the
song. Nothing on the embedding page can override that, so the only real fix is to
find the blocked ids and swap in an upload that does allow embedding. The deck
itself also detects the refusal at runtime and offers a direct YouTube link, so a
blocked id degrades instead of breaking.

This checks every youtubeId in src/data/discography.json by asking yt-dlp to
simulate playback as the web-embedded client: that client is refused exactly when
embedding is refused.

One check can fail for unrelated reasons (bot check, transient network), so each id
is retried and only reported once every attempt has failed.

Usage:
    .venv/bin/python scripts/check-embeds.py              # every sample
    .venv/bin/python scripts/check-embeds.py --jobs 1     # gentler on rate limits
    .venv/bin/python scripts/check-embeds.py --only ID1,ID2
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISCOGRAPHY = ROOT / "src" / "data" / "discography.json"

YTDLP = "yt-dlp"
PLAYER_CLIENT = "youtube:player_client=web_embedded"
ATTEMPTS = 3


def collect_uses() -> dict[str, list[str]]:
    """Map every youtube id to the releases that reference it."""
    data = json.loads(DISCOGRAPHY.read_text(encoding="utf-8"))
    uses: dict[str, list[str]] = {}

    def add(video_id: str | None, label: str) -> None:
        if video_id:
            uses.setdefault(video_id, []).append(label)

    for year in data.get("years", []):
        for single in year.get("singles", []):
            add(single.get("youtubeId"), f'{single.get("date")} · single · {single.get("title")}')
        for album in year.get("albums", []):
            for track in album.get("tracks", []):
                add(
                    track.get("youtubeId"),
                    f'{album.get("date")} · {album.get("title")} · track {track.get("t")}',
                )
    return uses


def embedded_playback_allowed(video_id: str) -> bool:
    command = [
        YTDLP,
        "--simulate",
        "--no-warnings",
        "--no-progress",
        "--extractor-args",
        PLAYER_CLIENT,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    for _ in range(ATTEMPTS):
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except OSError as exc:
            print(f"could not run {YTDLP}: {exc}", file=sys.stderr)
            return True
        if result.returncode == 0:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobs", type=int, default=4, help="parallel checks (default 4)")
    parser.add_argument("--only", default="", help="comma-separated video ids to check")
    args = parser.parse_args()

    uses = collect_uses()
    ids = sorted(uses)
    if args.only:
        wanted = {part.strip() for part in args.only.split(",") if part.strip()}
        ids = [video_id for video_id in ids if video_id in wanted]

    if not ids:
        print("No video ids to check.")
        return 0

    print(f"Checking {len(ids)} sample(s) with the embedded player client …", flush=True)
    blocked: list[str] = []
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(embedded_playback_allowed, video_id): video_id for video_id in ids}
        for future in as_completed(futures):
            video_id = futures[future]
            done += 1
            if future.result():
                if done % 25 == 0 or done == len(ids):
                    print(f"  [{done}/{len(ids)}] checked …", flush=True)
                continue
            blocked.append(video_id)
            print(f"  [{done}/{len(ids)}] BLOCKED {video_id}", flush=True)

    print()
    if not blocked:
        print(f"All {len(ids)} samples allow embedding.")
        return 0

    print(f"{len(blocked)} of {len(ids)} sample(s) refuse embedding — replace them:")
    for video_id in sorted(blocked):
        print(f"\n  {video_id}   https://www.youtube.com/watch?v={video_id}")
        for label in uses[video_id]:
            print(f"    · {label}")
    print(
        "\nSearch YouTube for the song, then confirm a replacement allows embedding with:\n"
        "  python3 scripts/check-embeds.py --only <videoId>"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
