"use client";

import type { Meeting } from "@/types/meeting";
import MeetingCard from "./MeetingCard";
import { CalendarX, Search } from "lucide-react";

interface Props {
  meetings: Meeting[];
  isLoading: boolean;
}

export default function MeetingList({ meetings, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-48 rounded-xl glass border border-border-light/20 animate-shimmer"
            style={{
              backgroundImage: "linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent)",
              backgroundSize: "200% 100%",
            }}
          />
        ))}
      </div>
    );
  }

  if (meetings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 px-6 rounded-2xl glass border border-border-light/20 backdrop-blur-md">
        <div className="mb-4 p-4 rounded-full bg-muted-light/10">
          <CalendarX className="w-8 h-8 text-muted-light opacity-70" />
        </div>
        <p className="text-lg font-bold text-white mb-1">No meetings found</p>
        <p className="text-sm text-muted-light">Sync your calendar or create a meeting to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {meetings.map((m, idx) => (
        <div
          key={m.id}
          style={{
            animation: `float-up 0.6s ease-out ${idx * 50}ms both`,
          }}
        >
          <MeetingCard meeting={m} />
        </div>
      ))}
    </div>
  );
}
