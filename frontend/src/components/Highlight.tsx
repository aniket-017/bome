import { Fragment } from "react";

const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Marks every occurrence of any query word inside `text` (case-insensitive). */
export function Highlight({ text, query }: { text: string; query: string }) {
  const words = Array.from(new Set(query.split(/[\s,]+/).filter((w) => w.length >= 1)))
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp);
  if (!words.length) return <>{text}</>;
  const re = new RegExp(`(${words.join("|")})`, "gi");
  const parts = text.split(re);
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? <mark key={i}>{part}</mark> : <Fragment key={i}>{part}</Fragment>,
      )}
    </>
  );
}
