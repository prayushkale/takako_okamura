const Player = (() => {
  let yt = null;
  let apiReady = false;
  let waiting = null;
  let queue = [];
  let index = -1;

  if (typeof YT !== "undefined" && YT.Player) apiReady = true;

  window.onYouTubeIframeAPIReady = function () {
    apiReady = true;
    if (waiting) {
      const w = waiting;
      waiting = null;
      open(w.queue, w.index);
    }
  };

  function open(q, i) {
    if (!q || !q.length) return;
    if (typeof YT === "undefined" || !apiReady) {
      waiting = { queue: q, index: i };
      return;
    }
    if (!yt) {
      queue = q;
      index = i;
      yt = new YT.Player("yt-slot", {
        width: "320",
        height: "180",
        playerVars: { rel: 0 },
        events: {
          onReady: () => playAt(index),
          onStateChange: (e) => {
            if (e.data === YT.PlayerState.ENDED) step(1);
          }
        }
      });
      document.getElementById("player").hidden = false;
      document.body.classList.add("playing");
      renderNow();
      return;
    }
    playAt(i, q);
  }

  function playAt(i, q) {
    if (q) queue = q;
    if (!queue.length) return;
    index = (i + queue.length) % queue.length;
    const item = queue[index];
    document.getElementById("player").hidden = false;
    document.body.classList.add("playing");
    if (yt && yt.loadVideoById) yt.loadVideoById(item.youtubeId);
    renderNow();
  }

  function renderNow() {
    if (!queue.length || index < 0) return;
    const item = queue[index];
    document.getElementById("np-title").textContent = item.title;
    document.getElementById("np-sub").textContent = item.year + " · " + item.from;
    document.getElementById("np-count").textContent = (index + 1) + " / " + queue.length;
    const list = document.getElementById("np-queue");
    list.innerHTML = "";
    queue.forEach((q, k) => {
      const li = document.createElement("li");
      li.textContent = q.title;
      if (k === index) li.className = "now";
      li.addEventListener("click", () => playAt(k));
      list.appendChild(li);
    });
    const now = list.children[index];
    if (now) now.scrollIntoView({ block: "nearest", inline: "center" });
  }

  function step(d) {
    if (queue.length) playAt(index + d);
  }

  function close() {
    if (yt && yt.stopVideo) yt.stopVideo();
    document.getElementById("player").hidden = true;
    document.body.classList.remove("playing");
    queue = [];
    index = -1;
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("np-prev").addEventListener("click", () => step(-1));
    document.getElementById("np-next").addEventListener("click", () => step(1));
    document.getElementById("np-close").addEventListener("click", close);
  });

  return { playQueue: open, next: () => step(1), prev: () => step(-1), close };
})();
