"use client";

import Link from "next/link";
import { formatDate, formatDuration, getStatusColor, getInitials, truncate } from "@/lib/utils";
import type { Meeting } from "@/types/meeting";
import { ExternalLink, Clock, Users, Zap } from "lucide-react";

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
  const more = attendees.length > 4 ? `+${attendees.length - 4}` : null;
  const isLive = meeting.status === "live";

  return (
    <article
      className={`group relative rounded-2xl glass border transition-all duration-300 p-5 flex flex-col h-full overflow-hidden ${
        isLive
          ? "border-primary/60 shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30"
          : "border-border-light/20 hover:border-primary/40"
      }`}
      onClick={onClick}
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />

      {/* Live Badge */}
      {isLive && (
        <div className="absolute -top-1 -right-1 w-20 h-20 bg-gradient-to-br from-primary/30 to-transparent rounded-full blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
      )}

      {/* Status Badge */}
      <div className="flex items-center justify-between mb-3">
        {isLive ? (
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-primary/30 to-accent/30 border border-primary/40 text-xs font-bold text-primary animate-pulse">
            <Zap className="w-3.5 h-3.5" />
            LIVE NOW
          </span>
        ) : (
          <span className={getStatusColor(
            (meeting.status as "scheduled" | "live" | "completed" | "failed") || "scheduled"
          )}>
            {meeting.status || "scheduled"}
          </span>
        )}
        {(meeting.status === "scheduled" || meeting.status === "live") && meeting.meet_url && (
          <a
            href={meeting.meet_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-lg glass border border-border-light/20 text-muted-light hover:text-primary hover:border-primary/40 transition-all group-hover:scale-110 transform"
            onClick={(e) => e.stopPropagation()}
            title="Join meeting"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>

      {/* Title */}
      <Link href={`/meetings/${meeting.id}`} className="block group/link">
        <h3 className="font-bold text-lg text-white line-clamp-2 group-hover/link:text-primary transition-colors">
          {truncate(meeting.title, 80)}
        </h3>
      </Link>

      {/* Time Info */}
      <div className="space-y-1.5 mt-3 mb-4 flex-1">
        <div className="flex items-center gap-2 text-sm text-muted-light">
          <Clock className="w-4 h-4 flex-shrink-0" />
          <span>{timeLabel}</span>
        </div>
        <p className="text-xs text-muted-light ml-6">
          {formatDuration(meeting.start_time, meeting.end_time)}
        </p>
      </div>

      {/* Attendees */}
      {attendees.length > 0 && (
        <div className="flex items-center gap-2 mb-4 pb-4 border-t border-border-light/10">
          <Users className="w-4 h-4 text-muted-light flex-shrink-0" />
          <div className="flex items-center gap-1 flex-1 min-w-0">
            <div className="flex -space-x-2">
              {displayAttendees.map((a, i) => (
                <div
                  key={a.id}
                  className="w-7 h-7 rounded-full bg-gradient-to-br from-primary/40 to-accent/40 border-2 border-surface-elevated flex items-center justify-center text-xs font-bold text-primary flex-shrink-0 hover:z-10 hover:scale-125 transition-all"
                  title={a.email}
                  style={{ zIndex: displayAttendees.length - i }}
                >
                  {getInitials(a.name || a.email)}
                </div>
              ))}
            </div>
            {more && <span className="text-xs text-muted-light">{more}</span>}
          </div>
        </div>
      )}

      {/* View Details Link */}
      <Link
        href={`/meetings/${meeting.id}`}
        className="mt-auto text-sm font-semibold text-primary hover:text-accent transition-colors group-hover:translate-x-1 transform"
      >
        View details →
      </Link>
    </article>
  );
}
