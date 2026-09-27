const YT_API_SRC = "https://www.youtube.com/iframe_api";
let ytApiPromise: Promise<any> | null = null;

function loadYouTubeApi(): Promise<any> {
  if (ytApiPromise) return ytApiPromise;
  ytApiPromise = new Promise((resolve, reject) => {
    const w = window as any;
    if (w.YT && w.YT.Player) {
      resolve(w.YT);
      return;
    }
    const previous = w.onYouTubeIframeAPIReady;
    w.onYouTubeIframeAPIReady = () => {
      if (typeof previous === "function") previous();
      resolve(w.YT);
    };
    const tag = document.createElement("script");
    tag.src = YT_API_SRC;
    tag.async = true;
    tag.addEventListener("error", () => reject(new Error("YouTube IFrame API failed to load")));
    document.head.appendChild(tag);
  });
  return ytApiPromise;
}

export function initDeck() {
  const root = document.querySelector<HTMLElement>("[data-deck]");
  if (!root) return;
  const frames = Array.from(root.querySelectorAll<HTMLElement>("[data-frame]"));
  const counter = root.querySelector<HTMLElement>("[data-counter]");
  const prev = root.querySelector<HTMLButtonElement>("[data-prev]");
  const next = root.querySelector<HTMLButtonElement>("[data-next]");
  const index = root.querySelector<HTMLSelectElement>("[data-index]");
  const chorusBtn = root.querySelector<HTMLButtonElement>("[data-chorus-toggle]");
  const chorusState = root.querySelector<HTMLElement>("[data-chorus-state]");
  const presentBtn = root.querySelector<HTMLButtonElement>("[data-present]");
  const progress = root.querySelector<HTMLElement>("[data-progress]");
  if (!frames.length || !counter || !prev || !next || !index) return;

  let current = 0;
  let activePlayer: { destroy: () => void } | null = null;
  let playRequest = 0;
  const embedBlocked = new Set<string>();
  const CHORUS_KEY = "deck:fromChorus";
  let fromChorus = false;
  try {
    fromChorus = window.localStorage.getItem(CHORUS_KEY) === "1";
  } catch {
    fromChorus = false;
  }
  const clamp = (n: number) => Math.min(frames.length - 1, Math.max(0, n));

  function setPlayButton(btn: HTMLButtonElement, playing: boolean) {
    if (playing) {
      btn.dataset.state = "playing";
      btn.textContent = btn.classList.contains("play") ? "■ Stop" : "■";
      btn.setAttribute("aria-label", "Stop sample");
    } else {
      delete btn.dataset.state;
      btn.textContent = btn.classList.contains("play") ? "▶ Play" : "▶";
      btn.setAttribute("aria-label", "Play sample");
    }
  }

  function resetPlayButtons() {
    root.querySelectorAll<HTMLButtonElement>("[data-play]").forEach((btn) => setPlayButton(btn, false));
  }

  function destroyActivePlayer() {
    const player = activePlayer;
    activePlayer = null;
    if (!player) return;
    try {
      player.destroy();
    } catch {
      // the iframe is already gone
    }
  }

  function stopVideos() {
    playRequest += 1;
    destroyActivePlayer();
    root.querySelectorAll("[data-cover-wrap]").forEach((wrap) => {
      wrap.querySelectorAll(".player, .embed-fallback").forEach((el) => el.remove());
      const cover = wrap.querySelector<HTMLElement>(".cover");
      if (cover) cover.style.display = "";
    });
    resetPlayButtons();
  }

  // The owner of an embed-disabled video makes YouTube refuse to play it in an
  // iframe; there is no way around that from the embedding page. Surface the
  // reason and hand the viewer a direct YouTube link instead of a dead player.
  function showEmbedFallback(frame: HTMLElement, youtubeId: string, title: string, code: number) {
    const wrap = frame.querySelector<HTMLElement>("[data-cover-wrap]");
    if (!wrap) return;
    destroyActivePlayer();
    wrap.querySelectorAll(".player").forEach((el) => el.remove());
    const cover = wrap.querySelector<HTMLElement>(".cover");
    if (cover) cover.style.display = "";

    const disabledByOwner = code === 101 || code === 150;
    const panel = document.createElement("div");
    panel.className = "embed-fallback";
    panel.setAttribute("role", "status");

    const heading = document.createElement("p");
    heading.className = "ef-title";
    heading.textContent = disabledByOwner ? "Embedding disabled" : "Sample unavailable";

    const note = document.createElement("p");
    note.className = "ef-note";
    note.textContent = disabledByOwner
      ? `The uploader turned off playback on other websites, so “${title}” can't play inside this deck. It still plays on YouTube.`
      : `YouTube won't play “${title}” in an embedded player. The video may be private, removed or region-blocked.`;

    const link = document.createElement("a");
    link.className = "ef-link";
    link.href = `https://www.youtube.com/watch?v=${youtubeId}`;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "Watch on YouTube ↗";

    panel.append(heading, note, link);
    wrap.appendChild(panel);
    resetPlayButtons();
  }

  function playVideo(frame: HTMLElement, youtubeId: string, title: string, chorus: number) {
    const wrap = frame.querySelector<HTMLElement>("[data-cover-wrap]");
    if (!wrap) return;
    stopVideos();
    const token = playRequest;
    const cover = wrap.querySelector<HTMLElement>(".cover");
    if (cover) cover.style.display = "none";

    const player = document.createElement("div");
    player.className = "player";
    const host = document.createElement("div");
    player.appendChild(host);
    wrap.appendChild(player);

    const start = fromChorus && chorus > 0 ? chorus : 0;
    const playerVars: Record<string, string | number> = { autoplay: 1, rel: 0, playsinline: 1 };
    if (start > 0) playerVars.start = start;
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      playerVars.origin = window.location.origin;
    }

    loadYouTubeApi()
      .then((YT) => {
        if (token !== playRequest || !host.isConnected) return;
        activePlayer = new YT.Player(host, {
          videoId: youtubeId,
          playerVars,
          events: {
            onReady: (e: { target: { playVideo: () => void } }) => {
              if (token !== playRequest) return;
              e.target.playVideo();
            },
            onError: (e: { data: number }) => {
              if (token !== playRequest) return;
              const code = Number(e?.data);
              embedBlocked.add(youtubeId);
              // Let the callback return before tearing its own player down.
              window.setTimeout(() => {
                if (token !== playRequest) return;
                showEmbedFallback(frame, youtubeId, title, code);
              }, 0);
            },
          },
        });
      })
      .catch(() => {
        if (token !== playRequest) return;
        showEmbedFallback(frame, youtubeId, title, 0);
      });
  }

  function applyChorusMode() {
    if (chorusBtn) chorusBtn.setAttribute("aria-pressed", fromChorus ? "true" : "false");
    if (chorusState) chorusState.textContent = `From chorus: ${fromChorus ? "on" : "off"}`;
  }

  function setFromChorus(value: boolean) {
    fromChorus = value;
    try {
      window.localStorage.setItem(CHORUS_KEY, value ? "1" : "0");
    } catch {
      // private mode / storage disabled: the mode still works for this session
    }
    applyChorusMode();
  }

  function show(n: number, opts: { push?: boolean } = {}) {
    current = clamp(n);
    stopVideos();
    frames.forEach((f, i) => {
      f.classList.toggle("active", i === current);
      f.setAttribute("aria-hidden", i === current ? "false" : "true");
    });
    const active = frames[current];
    const hue = active?.dataset.hue;
    if (hue) document.documentElement.style.setProperty("--hue", hue);
    counter!.textContent = `${current + 1} / ${frames.length}`;
    index!.value = String(current);
    if (progress) progress.style.transform = `scaleX(${(current + 1) / frames.length})`;
    if (opts.push !== false) history.replaceState(null, "", `#slide-${current + 1}`);
    prev!.disabled = current === 0;
    next!.disabled = current === frames.length - 1;
    root!.dataset.currentTitle = active?.dataset.title ?? "";
  }

  prev.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
  index.addEventListener("change", () => show(Number(index.value)));

  root.querySelectorAll<HTMLButtonElement>("[data-play]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const frame = btn.closest<HTMLElement>("[data-frame]");
      const youtubeId = btn.dataset.play;
      if (!frame || !youtubeId) return;
      if (btn.dataset.state === "playing") {
        stopVideos();
        return;
      }
      if (embedBlocked.has(youtubeId)) {
        window.open(`https://www.youtube.com/watch?v=${youtubeId}`, "_blank", "noopener");
        return;
      }
      const start = Number(btn.dataset.start ?? "");
      playVideo(
        frame,
        youtubeId,
        btn.dataset.title ?? frame.dataset.title ?? "sample",
        Number.isFinite(start) ? start : 0,
      );
      setPlayButton(btn, true);
    });
  });

  if (chorusBtn) {
    chorusBtn.addEventListener("click", () => setFromChorus(!fromChorus));
  }

  if (presentBtn) {
    presentBtn.addEventListener("click", () => {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
        return;
      }
      root.requestFullscreen?.().catch(() => {});
    });
  }

  document.addEventListener("keydown", (e) => {
    const t = e.target as HTMLElement | null;
    if (t && (t.tagName === "SELECT" || t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
    if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") {
      e.preventDefault();
      show(current + 1);
    } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
      e.preventDefault();
      show(current - 1);
    } else if (e.key === "Home") {
      e.preventDefault();
      show(0);
    } else if (e.key === "End") {
      e.preventDefault();
      show(frames.length - 1);
    } else if (e.key === "c" || e.key === "C") {
      e.preventDefault();
      setFromChorus(!fromChorus);
    } else if (e.key === "p" || e.key === "P" || e.key === "Enter") {
      const active = frames[current];
      const firstPlay = active?.querySelector<HTMLButtonElement>("[data-play]");
      if (firstPlay && t && !t.closest("a,button")) {
        e.preventDefault();
        firstPlay.click();
      }
    }
  });

  const start = window.location.hash.match(/slide-(\d+)/);
  show(start ? Number(start[1]) - 1 : 0, { push: false });
  applyChorusMode();
  // Warm the player API so the first ▶ starts instantly instead of waiting on a script fetch.
  loadYouTubeApi().catch(() => {});
}
