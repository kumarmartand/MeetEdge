"use client";

import { useQuery } from "@tanstack/react-query";
import { meetings as meetingsApi, actionItems as actionItemsApi } from "@/lib/api";
import { formatDate, formatDuration, getStatusColor } from "@/lib/utils";
import { Calendar, Radio, ListTodo, CalendarDays, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { data: meetings = [], isLoading: meetingsLoading } = useQuery({
    queryKey: ["meetings", { limit: 20 }],
    queryFn: () => meetingsApi.list({ limit: 20 }),
  });
  const { data: items = [], isLoading: itemsLoading } = useQuery({
    queryKey: ["action-items"],
    queryFn: () => actionItemsApi.list({ status: "open" }),
  });

  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const todayEnd = new Date(todayStart.getTime() + 24 * 60 * 60 * 1000);
  const weekEnd = new Date(todayStart.getTime() + 7 * 24 * 60 * 60 * 1000);

  const meetingsToday = meetings.filter((m) => {
    const t = new Date(m.start_time).getTime();
    return t >= todayStart.getTime() && t < todayEnd.getTime();
  });
  const liveNow = meetings.filter((m) => m.status === "live");
  const openActionItems = items.filter((i) => i.status !== "completed");
  const meetingsThisWeek = meetings.filter((m) => {
    const t = new Date(m.start_time).getTime();
    return t >= todayStart.getTime() && t < weekEnd.getTime();
  });

  const upcoming = meetings
    .filter((m) => new Date(m.start_time) >= now && (m.status === "scheduled" || m.status === "live"))
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  const recentItems = openActionItems.slice(0, 10);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Meetings Today"
          value={meetingsLoading ? "—" : String(meetingsToday.length)}
          icon={Calendar}
        />
        <StatCard
          title="Live Now"
          value={meetingsLoading ? "—" : String(liveNow.length)}
          icon={Radio}
          pulse={liveNow.length > 0}
        />
        <StatCard
          title="Action Items Open"
          value={itemsLoading ? "—" : String(openActionItems.length)}
          icon={ListTodo}
        />
        <StatCard
          title="Meetings This Week"
          value={meetingsLoading ? "—" : String(meetingsThisWeek.length)}
          icon={CalendarDays}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <h2 className="text-lg font-semibold">Upcoming Meetings</h2>
          {meetingsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-20 bg-surface rounded-lg animate-pulse" />
              ))}
            </div>
          ) : upcoming.length === 0 ? (
            <p className="text-muted">No upcoming meetings</p>
          ) : (
            <ul className="space-y-2">
              {upcoming.map((m) => (
                <li
                  key={m.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-surface border border-border"
                >
                  <div>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs border ${getStatusColor(m.status as "scheduled" | "live" | "completed" | "failed")}`}>
                      {m.status}
                    </span>
                    <p className="font-medium mt-1">{m.title}</p>
                    <p className="text-sm text-muted">
                      {formatDate(m.start_time, "EEE, MMM d 'at' h:mm a")} · {formatDuration(m.start_time, m.end_time)}
                    </p>
                  </div>
                  {m.meet_url && (
                    <a
                      href={m.meet_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 ml-2 px-3 py-1.5 rounded-lg bg-primary text-white text-sm font-medium hover:opacity-90 flex items-center gap-1"
                    >
                      Join <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold">Recent Action Items</h2>
          {itemsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-14 bg-surface rounded-lg animate-pulse" />
              ))}
            </div>
          ) : recentItems.length === 0 ? (
            <p className="text-muted">No open action items</p>
          ) : (
            <ul className="space-y-2">
              {recentItems.map((ai) => (
                <li key={ai.id} className="p-3 rounded-lg bg-surface border border-border">
                  <p className="text-sm">{ai.text}</p>
                  <p className="text-xs text-muted mt-1">
                    {ai.assignee_email && `${ai.assignee_email} · `}
                    {ai.due_date && `Due ${formatDate(ai.due_date, "MMM d")}`}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  pulse = false,
}: {
  title: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  pulse?: boolean;
}) {
  return (
    <div className="p-4 rounded-lg bg-surface border border-border">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted">{title}</span>
        <Icon className={`w-5 h-5 text-primary ${pulse ? "animate-pulse" : ""}`} />
      </div>
      <p className="text-2xl font-semibold mt-2">{value}</p>
    </div>
  );
}
