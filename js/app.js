(async function () {
  const slide = document.getElementById("slide");
  const timeline = document.getElementById("timeline");
  const yearSelect = document.getElementById("yearSelect");
  const progress = document.getElementById("progress");
  const prevBtn = document.getElementById("prevYear");
  const nextBtn = document.getElementById("nextYear");

  let years = [];
  let current = 0;
  let currentQueue = [];
  let ignoreHash = false;

  const esc = (s) =>
    String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  const ytSearch = (t) =>
    "https://www.youtube.com/results?search_query=" +
    encodeURIComponent("岡村孝子 " + t);
  const rankBadge = (o) =>
    o ? '<span class="rank">Oricon ' + o + "位</span>" : "";
  const numBadge = (label, n) =>
    n ? '<span class="num">' + label + " #" + n + "</span>" : "";

  function playableQueue(y) {
    const q = [];
    y.singles.forEach((s) => {
      if (s.youtubeId)
        q.push({ year: y.year, from: "Single · " + s.title, title: s.title, youtubeId: s.youtubeId });
    });
    y.albums.forEach((a) => {
      a.tracks.forEach((t) => {
        if (t.youtubeId)
          q.push({ year: y.year, from: "Album · " + a.title, title: t.t, youtubeId: t.youtubeId });
      });
    });
    return q;
  }

  function singleCard(s, qi) {
    const btn = s.youtubeId
      ? '<button class="play" type="button" data-q="' + qi + '" aria-label="Play ' + esc(s.title) + '">▶</button>'
      : '<button class="play off" type="button" disabled title="No video linked yet">–</button>';
    const bits = [s.date, s.coupling ? "c/w " + esc(s.coupling) : "", rankBadge(s.oricon)]
      .filter(Boolean)
      .join(" · ");
    return (
      "<article class=\"single\">" + btn + "<div><div class=\"song-title\">" +
      esc(s.title) + numBadge("Single", s.n) + "</div>" +
      (bits ? "<div class=\"meta\">" + bits + "</div>" : "") +
      "<div class=\"tags\">" +
      (s.tieup ? "<span class=\"tieup\">" + esc(s.tieup) + "</span>" : "") +
      "<a class=\"yt-link\" href=\"" + ytSearch(s.title) + "\" target=\"_blank\" rel=\"noopener\">Search on YouTube ↗</a>" +
      "</div></div></article>"
    );
  }

  function albumCard(a, nextQi) {
    let qi = nextQi.value;
    const tracks = a.tracks
      .map((t, i) => {
        const idx = t.youtubeId ? qi++ : -1;
        const btn = t.youtubeId
          ? '<button class="mini-play" type="button" data-q="' + idx + '" aria-label="Play ' + esc(t.t) + '">▶</button>'
          : '<button class="mini-play off" type="button" disabled title="No video linked yet">–</button>';
        return (
          "<li>" + btn + "<span class=\"track-no\">" + (i + 1) + "</span><span>" + esc(t.t) + "</span>" +
          "<a class=\"yt-link\" href=\"" + ytSearch(t.t) + "\" target=\"_blank\" rel=\"noopener\">↗</a></li>"
        );
      })
      .join("");
    nextQi.value = qi;
    const bits = [a.date, rankBadge(a.oricon), a.tracks.length + " tracks"]
      .filter(Boolean)
      .join(" · ");
    return (
      "<article class=\"album\"><div class=\"album-head\"><span class=\"album-no\">Album" +
      (a.n ? " #" + a.n : "") + "</span><h3>" + esc(a.title) + "</h3>" +
      "<div class=\"meta\">" + bits + "</div></div>" +
      '<ol class="tracks">' + tracks + "</ol></article>"
    );
  }

  function render(y) {
    currentQueue = playableQueue(y);
    const qi = { value: 0 };
    const singlesHtml = y.singles.length
      ? y.singles.map((s) => singleCard(s, s.youtubeId ? qi.value++ : -1)).join("")
      : '<div class="quiet">No singles this year.</div>';
    const albumsHtml = y.albums.length
      ? y.albums.map((a) => albumCard(a, qi)).join("")
      : '<div class="quiet">No studio album this year.</div>';
    const playable = currentQueue.length;
    slide.innerHTML =
      '<div class="slide-head"><p class="year-big">' + y.year + "</p>" +
      '<p class="era">' + esc(y.era || "") + "</p>" +
      '<div class="slide-actions"><button class="play-all" type="button" data-play-all' +
      (playable ? "" : " disabled") + ">▶ Play this year</button>" +
      '<span class="playable-count">' + playable + " playable track" + (playable === 1 ? "" : "s") + "</span></div></div>" +
      '<h2 class="section-title">Singles</h2>' + singlesHtml +
      '<h2 class="section-title">Albums</h2>' + albumsHtml;
  }

  function showYear(year) {
    const i = years.findIndex((y) => y.year === year);
    if (i < 0) return;
    current = i;
    render(years[i]);
    Array.prototype.forEach.call(timeline.children, (el, k) =>
      el.classList.toggle("active", k === i)
    );
    yearSelect.value = String(year);
    progress.textContent = "Year " + (i + 1) + " of " + years.length + " · " + year + " · ← → keys work too";
    prevBtn.disabled = i === 0;
    nextBtn.disabled = i === years.length - 1;
    const h = "#year=" + year;
    if (location.hash !== h) {
      ignoreHash = true;
      location.hash = h;
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
    const active = timeline.children[i];
    if (active) active.scrollIntoView({ block: "nearest", inline: "center" });
  }

  function step(d) {
    const n = current + d;
    if (n >= 0 && n < years.length) showYear(years[n].year);
  }

  try {
    const res = await fetch("data/discography.json");
    const data = await res.json();
    years = data.years;
  } catch (err) {
    slide.innerHTML = '<p class="error">Could not load discography data. Please serve this folder over HTTP (e.g. `npx serve .`) instead of opening index.html directly.</p>';
    return;
  }

  years.forEach((y) => {
    const b = document.createElement("button");
    b.className = "pill";
    b.type = "button";
    b.textContent = y.year;
    b.setAttribute("role", "tab");
    b.addEventListener("click", () => showYear(y.year));
    timeline.appendChild(b);
    const o = document.createElement("option");
    o.value = y.year;
    o.textContent = y.year;
    yearSelect.appendChild(o);
  });

  prevBtn.addEventListener("click", () => step(-1));
  nextBtn.addEventListener("click", () => step(1));
  yearSelect.addEventListener("change", () => showYear(Number(yearSelect.value)));

  slide.addEventListener("click", (e) => {
    if (e.target.closest("[data-play-all]")) {
      if (currentQueue.length) Player.playQueue(currentQueue, 0);
      return;
    }
    const btn = e.target.closest("[data-q]");
    if (btn) Player.playQueue(currentQueue, Number(btn.getAttribute("data-q")));
  });

  document.addEventListener("keydown", (e) => {
    if (e.target && (e.target.tagName === "SELECT" || e.target.tagName === "INPUT")) return;
    if (e.key === "ArrowRight") step(1);
    else if (e.key === "ArrowLeft") step(-1);
  });

  window.addEventListener("hashchange", () => {
    if (ignoreHash) {
      ignoreHash = false;
      return;
    }
    const m = location.hash.match(/year=(\d{4})/);
    if (m) showYear(Number(m[1]));
  });

  const start = location.hash.match(/year=(\d{4})/);
  showYear(start ? Number(start[1]) : years[0].year);
})();
