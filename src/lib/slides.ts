import chorusData from "../data/chorus.json";

export interface ChorusEntry {
  start: number;
  conf?: number;
  method?: "ssm" | "heuristic" | "manual";
  duration?: number;
}

const CHORUS = chorusData as Record<string, ChorusEntry | undefined>;

function chorusStartOf(youtubeId: string | null | undefined): number | null {
  if (!youtubeId) return null;
  const start = CHORUS[youtubeId]?.start;
  return typeof start === "number" && Number.isFinite(start) && start > 0
    ? Math.round(start)
    : null;
}

export function formatTime(seconds: number): string {
  const s = Math.max(0, Math.round(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export interface DiscogTrack {
  t: string;
  youtubeId: string | null;
}

export interface DiscogSingle {
  n: number | null;
  title: string;
  date: string;
  coupling?: string;
  oricon?: number | null;
  tieup?: string;
  youtubeId: string | null;
}

export interface DiscogAlbum {
  n: number | null;
  title: string;
  date: string;
  oricon?: number | null;
  tracks: DiscogTrack[];
}

export interface DiscogYear {
  year: number;
  era?: string;
  singles: DiscogSingle[];
  albums: DiscogAlbum[];
}

export interface SlideTrack {
  no: number;
  title: string;
  youtubeId: string | null;
  chorusStart: number | null;
}

export type SlideKind = "single" | "album" | "summary";

export interface Slide {
  id: string;
  index: number;
  kind: SlideKind;
  year: number;
  era?: string;
  title: string;
  subtitle: string;
  date: string;
  oricon: number | null;
  coverSeed: string;
  coverHue: number;
  youtubeId: string | null;
  youtubeEmbed: string | null;
  chorusStart: number | null;
  watchUrl: string;
  searchUrl: string;
  tieup?: string;
  coupling?: string;
  num?: number | null;
  tracks: SlideTrack[];
  playableCount: number;
}

export interface AlbumSummaryRow {
  n: number | null;
  title: string;
  year: number;
  date: string;
  oricon: number | null;
  trackCount: number;
  hue: number;
}

export interface DeckSummary {
  albumCount: number;
  singleCount: number;
  trackCount: number;
  firstYear: number;
  lastYear: number;
  spanYears: number;
  albums: AlbumSummaryRow[];
  bestAlbum: AlbumSummaryRow | null;
}

export interface SlidesPayload {
  count: number;
  slides: Slide[];
  summary: DeckSummary;
}

const HUES = [348, 20, 42, 150, 200, 225, 265, 300, 320, 12];

function hueFor(seed: string, fallback: number): number {
  let h = 0;
  for (const ch of seed) h = (h * 31 + ch.codePointAt(0)!) % 360;
  return HUES[(h + fallback) % HUES.length];
}

function ytSearchUrl(title: string): string {
  return (
    "https://www.youtube.com/results?search_query=" +
    encodeURIComponent("岡村孝子 " + title)
  );
}

function watchUrl(youtubeId: string | null, title: string): string {
  return youtubeId
    ? `https://www.youtube.com/watch?v=${youtubeId}`
    : ytSearchUrl(title);
}

function embedUrl(youtubeId: string | null): string | null {
  return youtubeId ? `https://www.youtube.com/embed/${youtubeId}?rel=0` : null;
}

function slug(s: string): string {
  return (
    s
      .toLowerCase()
      .replace(/[^a-z0-9\u3040-\u30ff\u4e00-\u9faf]+/gi, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 40) || "release"
  );
}

type FlatRelease =
  | { type: "single"; date: string; order: number; single: DiscogSingle }
  | { type: "album"; date: string; order: number; album: DiscogAlbum };

export function buildSlides(years: DiscogYear[]): SlidesPayload {
  const flat: FlatRelease[] = [];
  years.forEach((y, yi) => {
    (y.singles ?? []).forEach((s, si) =>
      flat.push({ type: "single", date: s.date ?? `${y.year}`, order: yi * 100 + si, single: s }),
    );
    (y.albums ?? []).forEach((a, ai) =>
      flat.push({ type: "album", date: a.date ?? `${y.year}`, order: yi * 100 + 50 + ai, album: a }),
    );
  });
  flat.sort((a, b) =>
    a.date < b.date ? -1 : a.date > b.date ? 1 : a.order - b.order,
  );

  const eraByYear = new Map(years.map((y) => [y.year, y.era ?? ""]));

  const slides: Slide[] = flat.map((r, index) => {
    const year = Number((r.date ?? "0000").slice(0, 4));
    const era = eraByYear.get(year) ?? "";
    if (r.type === "single") {
      const s = r.single;
      const title = s.title;
      return {
        id: `${s.date}-s-${slug(title)}`,
        index,
        kind: "single",
        year,
        era,
        title,
        subtitle: s.n ? `Single #${s.n}` : "Digital single",
        date: s.date,
        oricon: s.oricon ?? null,
        coverSeed: title,
        coverHue: hueFor(title, index),
        youtubeId: s.youtubeId ?? null,
        youtubeEmbed: embedUrl(s.youtubeId ?? null),
        chorusStart: chorusStartOf(s.youtubeId),
        watchUrl: watchUrl(s.youtubeId ?? null, title),
        searchUrl: ytSearchUrl(title),
        tieup: s.tieup || undefined,
        coupling: s.coupling || undefined,
        num: s.n ?? null,
        tracks: [],
        playableCount: s.youtubeId ? 1 : 0,
      };
    }
    const a = r.album;
    const tracks: SlideTrack[] = (a.tracks ?? []).map((t, i) => ({
      no: i + 1,
      title: t.t,
      youtubeId: t.youtubeId ?? null,
      chorusStart: chorusStartOf(t.youtubeId),
    }));
    const head = tracks.find((t) => t.youtubeId)?.youtubeId ?? null;
    return {
      id: `${a.date}-a-${slug(a.title)}`,
      index,
      kind: "album",
      year,
      era,
      title: a.title,
      subtitle: a.n ? `Album #${a.n}` : "Album",
      date: a.date,
      oricon: a.oricon ?? null,
      coverSeed: a.title,
      coverHue: hueFor(a.title, index),
      youtubeId: head,
      youtubeEmbed: embedUrl(head),
      chorusStart: chorusStartOf(head),
      watchUrl: watchUrl(head, `${a.title} album`),
      searchUrl: ytSearchUrl(`${a.title}`),
      num: a.n ?? null,
      tracks,
      playableCount: tracks.filter((t) => t.youtubeId).length,
    };
  });

  const albumSlides = slides.filter((s) => s.kind === "album");
  const albumRows: AlbumSummaryRow[] = albumSlides.map((a) => ({
    n: a.num ?? null,
    title: a.title,
    year: a.year,
    date: a.date,
    oricon: a.oricon,
    trackCount: a.tracks.length,
    hue: a.coverHue,
  }));
  const firstYear = slides[0]?.year ?? 0;
  const lastYear = slides[slides.length - 1]?.year ?? 0;
  const charted = albumRows.filter((a) => a.oricon != null);
  const summary: DeckSummary = {
    albumCount: albumRows.length,
    singleCount: slides.length - albumRows.length,
    trackCount: albumRows.reduce((n, a) => n + a.trackCount, 0),
    firstYear,
    lastYear,
    spanYears: lastYear >= firstYear ? lastYear - firstYear + 1 : 0,
    albums: albumRows,
    bestAlbum: charted.length
      ? charted.reduce((best, a) => ((a.oricon as number) < (best.oricon as number) ? a : best))
      : null,
  };

  slides.push({
    id: "summary",
    index: slides.length,
    kind: "summary",
    year: lastYear,
    title: "総括",
    subtitle: "Complete Discography",
    date: `${firstYear}–${lastYear}`,
    oricon: null,
    coverSeed: "summary",
    coverHue: 225,
    youtubeId: null,
    youtubeEmbed: null,
    chorusStart: null,
    watchUrl: "",
    searchUrl: "",
    tracks: [],
    playableCount: 0,
  });

  return { count: slides.length, slides, summary };
}

export function initialsOf(title: string): string {
  const chars = [...title.replace(/[\s〜～・「」『』（）()!！?？\-–—]+/g, "")];
  if (chars.length === 0) return "孝";
  if (chars.length === 1) return chars[0];
  return chars[0] + chars[chars.length - 1];
}
