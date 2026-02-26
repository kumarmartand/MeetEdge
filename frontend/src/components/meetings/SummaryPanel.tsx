"use client";

import { useState } from "react";
import type { Meeting } from "@/types/meeting";
import { Check, ListChecks, Copy } from "lucide-react";

interface Props {
  meeting: Meeting;
}

export default function SummaryPanel({ meeting }: Props) {
  const [copied, setCopied] = useState(false);
  const summary = meeting.summary;
  const keyPoints = (meeting.summary_key_points as Record<string, unknown>) ?? {};
  const keyPointsList = (keyPoints.key_points as string[]) ?? [];
  const decisions = (keyPoints.decisions as string[]) ?? [];
  const actionItemsSummary = (keyPoints.action_items_summary as unknown[]) ?? [];
  const followUps = (keyPoints.follow_ups as string[]) ?? [];

  const copySummary = () => {
    const parts = [
      summary,
      keyPointsList.length ? "Key points:\n" + keyPointsList.map((p, i) => `${i + 1}. ${p}`).join("\n") : "",
      decisions.length ? "Decisions:\n" + decisions.map((d) => `• ${d}`).join("\n") : "",
      followUps.length ? "Follow-ups:\n" + followUps.map((f) => `• ${f}`).join("\n") : "",
    ].filter(Boolean);
    navigator.clipboard.writeText(parts.join("\n\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!summary && keyPointsList.length === 0 && decisions.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-surface p-6 text-center">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3" />
        <p className="text-muted">Summary being generated...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <button
          type="button"
          onClick={copySummary}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface border border-border hover:bg-border text-sm"
        >
          <Copy className="w-4 h-4" />
          {copied ? "Copied!" : "Copy Summary"}
        </button>
      </div>
      {summary && (
        <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
          <h3 className="font-semibold text-primary mb-2">Executive Summary</h3>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{summary}</p>
        </div>
      )}
      {keyPointsList.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <ListChecks className="w-4 h-4" />
            Key Discussion Points
          </h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-muted">
            {keyPointsList.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ol>
        </div>
      )}
      {decisions.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <Check className="w-4 h-4" />
            Decisions Made
          </h3>
          <ul className="space-y-1 text-sm">
            {decisions.map((d, i) => (
              <li key={i} className="flex items-start gap-2">
                <Check className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                {d}
              </li>
            ))}
          </ul>
        </div>
      )}
      {meeting.action_items && meeting.action_items.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Action Items</h3>
          <ul className="space-y-2">
            {meeting.action_items.map((ai) => (
              <li key={ai.id} className="flex justify-between items-start text-sm p-2 rounded bg-surface border border-border">
                <span>{ai.text}</span>
                <span className="text-muted text-xs">
                  {ai.assignee_email && `${ai.assignee_email} · `}
                  {ai.due_date && new Date(ai.due_date).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {followUps.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Follow-ups</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted">
            {followUps.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
