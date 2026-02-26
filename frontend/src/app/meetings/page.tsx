"use client";

import { useState, useMemo } from "react";
import { useMeetings, useSyncCalendar } from "@/hooks/useMeetings";
import MeetingList from "@/components/meetings/MeetingList";
import { debounce } from "@/lib/utils";
import { Search, Calendar } from "lucide-react";

const TABS = [
  { value: "", label: "All" },
  { value: "scheduled", label: "Scheduled" },
  { value: "live", label: "Live" },
  { value: "completed", label: "Completed" },
];

export default function MeetingsPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [status, setStatus] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 12;

  const debouncedSetSearch = useMemo(
    () => debounce((v: string) => { setDebouncedSearch(v); }, 300),
    []
  );
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    debouncedSetSearch(e.target.value);
  };

  const { meetings, isLoading } = useMeetings({
    search: debouncedSearch || undefined,
    status: status || undefined,
    limit,
    offset,
  });
  const { sync, isSyncing } = useSyncCalendar();

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search meetings..."
            value={search}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-surface border border-border text-white placeholder-muted focus:ring-2 focus:ring-primary"
          />
        </div>
        <button
          type="button"
          onClick={() => sync()}
          disabled={isSyncing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90 disabled:opacity-50 shrink-0"
        >
          <Calendar className="w-4 h-4" />
          {isSyncing ? "Syncing…" : "Sync Calendar"}
        </button>
      </div>
      <div className="flex gap-2 border-b border-border pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => {
              setOffset(0);
              setStatus(tab.value);
            }}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              status === tab.value
                ? "bg-primary text-white"
                : "bg-surface border border-border text-muted hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <MeetingList meetings={meetings} isLoading={isLoading} />
      <div className="flex justify-between items-center pt-4">
        <button
          type="button"
          onClick={() => setOffset((o) => Math.max(0, o - limit))}
          disabled={offset === 0}
          className="px-4 py-2 rounded-lg border border-border hover:bg-surface disabled:opacity-50"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={() => setOffset((o) => o + limit)}
          disabled={meetings.length < limit}
          className="px-4 py-2 rounded-lg border border-border hover:bg-surface disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}
