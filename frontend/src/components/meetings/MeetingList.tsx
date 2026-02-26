"use client";

import type { Meeting } from "@/types/meeting";
import MeetingCard from "./MeetingCard";
import { CalendarX } from "lucide-react";

interface Props {
  meetings: Meeting[];
  isLoading: boolean;
}

export default function MeetingList({ meetings, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-48 rounded-xl bg-surface border border-border animate-pulse" />
        ))}
      </div>
    );
  }

  if (meetings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted">
        <CalendarX className="w-12 h-12 mb-4 opacity-50" />
        <p className="text-lg font-medium">No meetings found</p>
        <p className="text-sm">Sync your calendar or create a meeting to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {meetings.map((m) => (
        <MeetingCard key={m.id} meeting={m} />
      ))}
    </div>
  );
}
