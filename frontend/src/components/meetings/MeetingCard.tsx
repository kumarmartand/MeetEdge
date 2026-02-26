"use client";

import Link from "next/link";
import { formatDate, formatDuration, getStatusColor, getInitials, truncate } from "@/lib/utils";
import type { Meeting } from "@/types/meeting";
import { ExternalLink } from "lucide-react";

interface Props {
  meeting: Meeting;
  onClick?: () => void;
}

export default function MeetingCard({ meeting, onClick }: Props) {
  const start = new Date(meeting.start_time);
  const isToday = start.toDateString() === new Date().toDateString();
  const timeLabel = isToday
    ? `Today at ${formatDate(meeting.start_time, "h:mm a")}`
    : formatDate(meeting.start_time, "EEE, MMM d 'at' h:mm a");
  const attendees = meeting.attendees ?? [];
  const displayAttendees = attendees.slice(0, 4);
  const more = attendees.length > 4 ? `+${attendees.length - 4} more` : null;

  return (
    <article
      className="rounded-xl bg-surface border border-border p-4 flex flex-col h-full"
      onClick={onClick}
    >
      <Link href={`/meetings/${meeting.id}`} className="block">
        <h3 className="font-semibold text-white line-clamp-2">{truncate(meeting.title, 80)}</h3>
      </Link>
      <p className="text-sm text-muted mt-1">{timeLabel}</p>
      <p className="text-xs text-muted">{formatDuration(meeting.start_time, meeting.end_time)}</p>
      {attendees.length > 0 && (
        <div className="flex items-center gap-1 mt-2">
          <div className="flex -space-x-2">
            {displayAttendees.map((a, i) => (
              <div
                key={a.id}
                className="w-7 h-7 rounded-full bg-primary/30 border-2 border-surface flex items-center justify-center text-xs font-medium text-primary"
                title={a.email}
                style={{ zIndex: displayAttendees.length - i }}
              >
                {getInitials(a.name || a.email)}
              </div>
            ))}
          </div>
          {more && <span className="text-xs text-muted ml-1">{more}</span>}
        </div>
      )}
      <div className="mt-3 flex items-center justify-between gap-2">
        <span
          className={`inline-block px-2 py-0.5 rounded text-xs border ${getStatusColor(
            (meeting.status as "scheduled" | "live" | "completed" | "failed") || "scheduled"
          )}`}
        >
          {meeting.status === "live" && <span className="inline-block w-1.5 h-1.5 rounded-full bg-current mr-1 animate-pulse" />}
          {meeting.status || "scheduled"}
        </span>
        {(meeting.status === "scheduled" || meeting.status === "live") && meeting.meet_url && (
          <a
            href={meeting.meet_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            Join <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
      <Link
        href={`/meetings/${meeting.id}`}
        className="mt-2 text-sm text-primary hover:underline"
      >
        View details
      </Link>
    </article>
  );
}
