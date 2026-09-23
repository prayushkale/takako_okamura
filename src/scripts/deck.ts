export function initDeck() {
  const root = document.querySelector<HTMLElement>("[data-deck]");
  if (!root) return;
  const frames = Array.from(root.querySelectorAll<HTMLElement>("[data-frame]"));
  const counter = root.querySelector<HTMLElement>("[data-counter]");
  const prev = root.querySelector<HTMLButtonElement>("[data-prev]");
  const next = root.querySelector<HTMLButtonElement>("[data-next]");
  const index = root.querySelector<HTMLSelectElement>("[data-index]");
  const autoplayBtn = root.querySelector<HTMLButtonElement>("[data-autoplay]");
  const chorusBtn = root.querySelector<HTMLButtonElement>("[data-chorus-toggle]");
  const chorusState = root.querySelector<HTMLElement>("[data-chorus-state]");
  const openLink = root.querySelector<HTMLAnchorElement>("[data-open-current]");
  const presentBtn = root.querySelector<HTMLButtonElement>("[data-present]");
  const progress = root.querySelector<HTMLElement>("[data-progress]");
  if (!frames.length || !counter || !prev || !next || !index) return;

  let current = 0;
  let timer: number | null = null;
  const AUTOPLAY_MS = 8000;
  const CHORUS_KEY = "deck:fromChorus";
  let fromChorus = false;
  try {
    fromChorus = window.localStorage.getItem(CHORUS_KEY) === "1";
  } catch {
    fromChorus = false;
  }
  const clamp = (n: number) => Math.min(frames.length - 1, Math.max(0, n));

  function stopAutoplay() {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
    if (autoplayBtn) {
      autoplayBtn.setAttribute("aria-pressed", "false");
      autoplayBtn.querySelector("[data-autoplay-label]")!.textContent = "Auto 8s: off";
    }
  }

  function stopVideos() {
    root.querySelectorAll("[data-cover-wrap]").forEach((wrap) => {
      wrap.querySelectorAll(".player,.stop-btn").forEach((el) => el.remove());
      const cover = wrap.querySelector<HTMLElement>(".cover");
      if (cover) cover.style.display = "";
    });
  }

  function playVideo(frame: HTMLElement, youtubeId: string, title: string, chorus: number) {
    const wrap = frame.querySelector<HTMLElement>("[data-cover-wrap]");
    if (!wrap) return;
    stopVideos();
    const cover = wrap.querySelector<HTMLElement>(".cover");
    if (cover) cover.style.display = "none";
    const player = document.createElement("div");
    player.className = "player";
    const iframe = document.createElement("iframe");
    const seek = fromChorus && chorus > 0 ? `&start=${chorus}` : "";
    iframe.src = `https://www.youtube.com/embed/${youtubeId}?autoplay=1&rel=0${seek}`;
    iframe.title = `${title} — YouTube sample`;
    iframe.allow =
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    iframe.allowFullscreen = true;
    player.appendChild(iframe);
    const stop = document.createElement("button");
    stop.type = "button";
    stop.className = "stop-btn";
    stop.textContent = "✕ Cover";
    stop.setAttribute("aria-label", "Stop video and show cover again");
    stop.addEventListener("click", () => stopVideos());
    wrap.appendChild(player);
    wrap.appendChild(stop);
  }

  function chorusSeconds(frame: HTMLElement | undefined): number {
    const start = Number(frame?.dataset.chorus ?? "");
    return Number.isFinite(start) && start > 0 ? start : 0;
  }

  function watchHref(frame: HTMLElement | undefined): string {
    const url = frame?.dataset.watch ?? "#";
    const start = chorusSeconds(frame);
    if (!fromChorus || !start || !url.includes("watch?v=")) return url;
    return `${url}&t=${start}`;
  }

  function applyChorusMode() {
    if (chorusBtn) chorusBtn.setAttribute("aria-pressed", fromChorus ? "true" : "false");
    if (chorusState) chorusState.textContent = `From chorus: ${fromChorus ? "on" : "off"}`;
    frames.forEach((frame) => {
      const note = frame.querySelector<HTMLElement>("[data-play-note]");
      if (!note) return;
      note.dataset.base ??= (note.textContent ?? "").trim();
      const label = fromChorus ? frame.dataset.chorusLabel : "";
      if (label) {
        note.textContent = `${note.dataset.base} · starting at the chorus (${label})`;
      } else if (fromChorus && frame.dataset.youtube) {
        note.textContent = `${note.dataset.base} · no chorus time for this song yet`;
      } else {
        note.textContent = note.dataset.base;
      }
    });
    if (openLink) openLink.href = watchHref(frames[current]);
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
    if (openLink && active) openLink.href = watchHref(active);
    if (opts.push !== false) history.replaceState(null, "", `#slide-${current + 1}`);
    prev!.disabled = current === 0;
    next!.disabled = current === frames.length - 1;
    root!.dataset.currentTitle = active?.dataset.title ?? "";
  }

  prev.addEventListener("click", () => {
    stopAutoplay();
    show(current - 1);
  });
  next.addEventListener("click", () => {
    stopAutoplay();
    show(current + 1);
  });
  index.addEventListener("change", () => {
    stopAutoplay();
    show(Number(index.value));
  });

  root.querySelectorAll<HTMLButtonElement>("[data-play]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const frame = btn.closest<HTMLElement>("[data-frame]");
      const youtubeId = btn.dataset.play;
      if (!frame || !youtubeId) return;
      stopAutoplay();
      const start = Number(btn.dataset.start ?? "");
      playVideo(
        frame,
        youtubeId,
        btn.dataset.title ?? frame.dataset.title ?? "sample",
        Number.isFinite(start) ? start : 0,
      );
    });
  });

  if (chorusBtn) {
    chorusBtn.addEventListener("click", () => setFromChorus(!fromChorus));
  }

  if (autoplayBtn) {
    autoplayBtn.addEventListener("click", () => {
      if (timer !== null) {
        stopAutoplay();
        return;
      }
      autoplayBtn.setAttribute("aria-pressed", "true");
      autoplayBtn.querySelector("[data-autoplay-label]")!.textContent = "Auto 8s: on";
      timer = window.setInterval(() => {
        if (current >= frames.length - 1) {
          stopAutoplay();
          return;
        }
        show(current + 1);
      }, AUTOPLAY_MS);
    });
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
      stopAutoplay();
      show(current + 1);
    } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
      e.preventDefault();
      stopAutoplay();
      show(current - 1);
    } else if (e.key === "Home") {
      e.preventDefault();
      stopAutoplay();
      show(0);
    } else if (e.key === "End") {
      e.preventDefault();
      stopAutoplay();
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
}
