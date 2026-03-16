"use client";

import { useState, useMemo } from "react";
import { useMeetings, useSyncCalendar } from "@/hooks/useMeetings";
import MeetingList from "@/components/meetings/MeetingList";
import { debounce } from "@/lib/utils";
import { Search, Calendar, Zap, ChevronLeft, ChevronRight } from "lucide-react";

const TABS = [
  { value: "", label: "All", color: "from-primary" },
  { value: "scheduled", label: "Scheduled", color: "from-blue-500" },
  { value: "live", label: "Live", color: "from-red-500" },
  { value: "completed", label: "Completed", color: "from-green-500" },
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
    <div className="space-y-6 animate-float-up">
      {/* Header Section */}
      <div className="space-y-4">
        <div className="flex flex-col gap-4">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-xl blur-lg opacity-0 group-focus-within:opacity-100 transition-opacity" />
            <div className="relative flex items-center gap-2 px-4 py-3 rounded-xl glass border border-border-light/30 focus-within:border-primary/40 transition-all">
              <Search className="w-5 h-5 text-muted-light" />
              <input
                type="text"
                placeholder="Search meetings by title, participants..."
                value={search}
                onChange={handleSearchChange}
                className="flex-1 bg-transparent outline-none text-white placeholder-muted-light"
              />
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-start sm:items-center">
            <div className="flex gap-2 flex-wrap">
              {TABS.map((tab, idx) => (
                <button
                  key={tab.value}
                  type="button"
                  onClick={() => {
                    setOffset(0);
                    setStatus(tab.value);
                  }}
                  style={{
                    animation: `float-up 0.5s ease-out ${idx * 50}ms both`,
                  }}
                  className={`relative px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 border group overflow-hidden ${
                    status === tab.value
                      ? `glass border-primary/40 bg-gradient-to-r ${tab.color}/20 to-transparent text-primary shadow-lg shadow-primary/20`
                      : "glass border-border-light/20 text-muted-light hover:text-white hover:border-primary/30"
                  }`}
                >
                  {status === tab.value && (
                    <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                  )}
                  <span className="relative">{tab.label}</span>
                </button>
              ))}
            </div>
            
            <button
              type="button"
              onClick={() => sync()}
              disabled={isSyncing}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-300 bg-gradient-to-r from-primary to-accent text-white hover:shadow-lg hover:shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed ${
                isSyncing ? "animate-pulse" : ""
              }`}
            >
              <Zap className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} />
              {isSyncing ? "Syncing…" : "Sync Now"}
            </button>
          </div>
        </div>
      </div>

      {/* Meetings List */}
      <MeetingList meetings={meetings} isLoading={isLoading} />

      {/* Pagination */}
      <div className="flex justify-between items-center pt-6 px-2">
        <button
          type="button"
          onClick={() => setOffset((o) => Math.max(0, o - limit))}
          disabled={offset === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass border border-border-light/20 text-muted-light hover:text-white hover:border-primary/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
        >
          <ChevronLeft className="w-4 h-4 group-hover:scale-110 transition-transform" />
          <span className="hidden sm:inline">Previous</span>
        </button>
        
        <span className="text-sm text-muted-light font-medium">
          {offset + 1} – {Math.min(offset + limit, offset + meetings.length)}
        </span>
        
        <button
          type="button"
          onClick={() => setOffset((o) => o + limit)}
          disabled={meetings.length < limit}
          className="flex items-center gap-2 px-4 py-2 rounded-lg glass border border-border-light/20 text-muted-light hover:text-white hover:border-primary/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight className="w-4 h-4 group-hover:scale-110 transition-transform" />
        </button>
      </div>
    </div>
  );
}
