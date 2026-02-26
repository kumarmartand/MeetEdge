"use client";

import { useState, useMemo } from "react";

interface Props {
  meetingId: string;
  transcript: string | null;
}

export default function TranscriptViewer({ meetingId, transcript }: Props) {
  const [search, setSearch] = useState("");
  const [copied, setCopied] = useState(false);

  const segments = useMemo(() => {
    if (!transcript?.trim()) return [];
    return transcript.split(/\n+/).filter(Boolean);
  }, [transcript]);

  const highlighted = useMemo(() => {
    if (!search.trim()) return segments;
    const re = new RegExp(`(${search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    return segments.map((s) => s.replace(re, (m) => `\u0000${m}\u0000`));
  }, [segments, search]);

  const copyFull = () => {
    if (!transcript) return;
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!transcript?.trim()) {
    return (
      <div className="rounded-lg border border-border bg-surface p-6 text-center text-muted">
        Transcript not yet available for this meeting.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <input
          type="text"
          placeholder="Search in transcript..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 rounded-lg bg-background border border-border text-white placeholder-muted w-64"
        />
        <button
          type="button"
          onClick={copyFull}
          className="px-3 py-2 rounded-lg bg-surface border border-border hover:bg-border text-sm"
        >
          {copied ? "Copied!" : "Copy full transcript"}
        </button>
      </div>
      <div className="rounded-lg border border-border bg-surface overflow-hidden">
        <div className="max-h-[60vh] overflow-y-auto p-4 space-y-3">
          {highlighted.map((seg, i) => (
            <div key={i} className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-primary/20 shrink-0 flex items-center justify-center text-xs font-medium text-primary">
                {(i % 3) + 1}
              </div>
              <p className="text-sm leading-relaxed break-words">
                {seg.split("\u0000").map((part, j) =>
                  j % 2 === 1 ? (
                    <mark key={j} className="bg-yellow-500/30 text-yellow-200">
                      {part}
                    </mark>
                  ) : (
                    part
                  )
                )}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
