"use client";

import { useParams } from "next/navigation";
import { useMeeting } from "@/hooks/useMeetings";
import { formatDate, formatDuration, getStatusColor, getInitials } from "@/lib/utils";
import SummaryPanel from "@/components/meetings/SummaryPanel";
import TranscriptViewer from "@/components/meetings/TranscriptViewer";
import { useState } from "react";
import { ExternalLink } from "lucide-react";
import { actionItems as actionItemsApi } from "@/lib/api";

const TABS = ["Summary", "Transcript", "Action Items", "Attendees"];

export default function MeetingDetailPage() {
  const params = useParams();
  const id = String(params.id);
  const { meeting, isLoading } = useMeeting(id);
  const [activeTab, setActiveTab] = useState(0);

  if (isLoading || !meeting) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="text-center py-16 text-muted">
        Meeting not found.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{meeting.title}</h1>
          <p className="text-muted mt-1">
            {formatDate(meeting.start_time, "EEEE, MMMM d, yyyy 'at' h:mm a")} · {formatDuration(meeting.start_time, meeting.end_time)}
          </p>
          <span
            className={`inline-block mt-2 px-2 py-0.5 rounded text-xs border ${getStatusColor(
              (meeting.status as "scheduled" | "live" | "completed" | "failed") || "scheduled"
            )}`}
          >
            {meeting.status}
          </span>
        </div>
        {meeting.meet_url && (
          <a
            href={meeting.meet_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white font-medium hover:opacity-90"
          >
            Join Meeting <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>

      <div className="border-b border-border">
        <nav className="flex gap-1">
          {TABS.map((label, i) => (
            <button
              key={label}
              type="button"
              onClick={() => setActiveTab(i)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
                activeTab === i ? "bg-surface border border-border border-b-0 -mb-px text-primary" : "text-muted hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 0 && <SummaryPanel meeting={meeting} />}
      {activeTab === 1 && (
        <TranscriptViewer meetingId={id} transcript={meeting.transcript} />
      )}
      {activeTab === 2 && (
        <ActionItemsTab meetingId={meeting.id} items={meeting.action_items} />
      )}
      {activeTab === 3 && (
        <div className="rounded-lg border border-border bg-surface overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border text-left text-sm text-muted">
                <th className="p-3">Attendee</th>
                <th className="p-3">Email</th>
                <th className="p-3">Response</th>
              </tr>
            </thead>
            <tbody>
              {(meeting.attendees ?? []).map((a) => (
                <tr key={a.id} className="border-b border-border last:border-0">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-xs font-medium text-primary">
                        {getInitials(a.name || a.email)}
                      </div>
                      {a.name || a.email}
                    </div>
                  </td>
                  <td className="p-3 text-muted">{a.email}</td>
                  <td className="p-3 text-muted">{a.response_status ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function ActionItemsTab({
  meetingId,
  items,
}: {
  meetingId: number;
  items: Array<{ id: number; text: string; assignee_email: string | null; due_date: string | null; status: string }>;
}) {
  const [statuses, setStatuses] = useState<Record<number, string>>(
    Object.fromEntries((items ?? []).map((i) => [i.id, i.status]))
  );

  const handleStatusChange = async (itemId: number, status: string) => {
    setStatuses((prev) => ({ ...prev, [itemId]: status }));
    await actionItemsApi.update(itemId, {
      status,
      completed: status === "completed",
    });
  };

  if (!items?.length) {
    return <p className="text-muted">No action items for this meeting.</p>;
  }

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-left text-sm text-muted">
            <th className="p-3">Description</th>
            <th className="p-3">Assignee</th>
            <th className="p-3">Due</th>
            <th className="p-3">Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((ai) => (
            <tr key={ai.id} className="border-b border-border last:border-0">
              <td className="p-3">{ai.text}</td>
              <td className="p-3 text-muted">{ai.assignee_email ?? "—"}</td>
              <td className="p-3 text-muted">
                {ai.due_date ? formatDate(ai.due_date, "MMM d") : "—"}
              </td>
              <td className="p-3">
                <select
                  value={statuses[ai.id] ?? ai.status}
                  onChange={(e) => handleStatusChange(ai.id, e.target.value)}
                  className="px-2 py-1 rounded bg-background border border-border text-sm"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
