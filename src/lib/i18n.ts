import translations from "../data/translations.json";

const MAP = translations as Record<string, string>;

export function en(text: string | null | undefined): string {
  if (!text) return "";
  const translated = MAP[text];
  return translated ? `${text} [${translated}]` : text;
}
