"use client";

import { useQuery } from "@tanstack/react-query";
import { meetings as meetingsApi, actionItems as actionItemsApi } from "@/lib/api";
import { formatDate, formatDuration, getStatusColor } from "@/lib/utils";
import { Calendar, Radio, ListTodo, CalendarDays, ExternalLink, Zap, CheckCircle2, AlertCircle, TrendingUp } from "lucide-react";
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
    <div className="space-y-8 animate-float-up">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Meetings Today"
          value={meetingsLoading ? "—" : String(meetingsToday.length)}
          icon={Calendar}
          index={0}
        />
        <StatCard
          title="Live Now"
          value={meetingsLoading ? "—" : String(liveNow.length)}
          icon={Radio}
          index={1}
          highlight={liveNow.length > 0}
        />
        <StatCard
          title="Action Items Open"
          value={itemsLoading ? "—" : String(openActionItems.length)}
          icon={ListTodo}
          index={2}
        />
        <StatCard
          title="Meetings This Week"
          value={meetingsLoading ? "—" : String(meetingsThisWeek.length)}
          icon={CalendarDays}
          index={3}
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Upcoming Meetings */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold">Upcoming Meetings</h2>
            <span className="px-2.5 py-1 rounded-lg glass border border-border-light/20 text-xs font-semibold text-primary">
              {upcoming.length}
            </span>
          </div>
          {meetingsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="h-20 rounded-xl glass border border-border-light/20 animate-shimmer"
                  style={{
                    backgroundImage: "linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent)",
                    backgroundSize: "200% 100%",
                  }}
                />
              ))}
            </div>
          ) : upcoming.length === 0 ? (
            <div className="p-8 rounded-xl glass border border-border-light/20 text-center">
              <Calendar className="w-12 h-12 text-muted-light mx-auto mb-3 opacity-50" />
              <p className="text-muted-light">No upcoming meetings</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {upcoming.map((m, idx) => (
                <li
                  key={m.id}
                  style={{
                    animation: `float-up 0.6s ease-out ${idx * 50}ms both`,
                  }}
                  className="flex items-center justify-between p-4 rounded-xl glass border border-border-light/20 hover:border-primary/40 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {m.status === "live" && (
                        <span className="flex items-center gap-1 px-2 py-1 rounded-lg bg-gradient-to-r from-primary/30 to-accent/30 border border-primary/40 text-xs font-bold text-primary animate-pulse">
                          <Radio className="w-3 h-3" />
                          LIVE
                        </span>
                      )}
                      {m.status === "scheduled" && (
                        <span className="px-2 py-1 rounded-lg glass border border-border-light/20 text-xs font-semibold text-muted-light">
                          Scheduled
                        </span>
                      )}
                    </div>
                    <p className="font-bold text-white group-hover:text-primary transition-colors">{m.title}</p>
                    <p className="text-sm text-muted-light mt-1">
                      {formatDate(m.start_time, "EEE, MMM d 'at' h:mm a")} · {formatDuration(m.start_time, m.end_time)}
                    </p>
                  </div>
                  {m.meet_url && (
                    <a
                      href={m.meet_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 ml-3 px-4 py-2 rounded-lg bg-gradient-to-r from-primary to-accent text-white text-sm font-bold hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 flex items-center gap-2 group-hover:scale-105 transform"
                    >
                      <Zap className="w-4 h-4" />
                      Join
                    </a>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Action Items */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold">Action Items</h2>
            <span className="px-2.5 py-1 rounded-lg glass border border-border-light/20 text-xs font-semibold text-accent">
              {recentItems.length}
            </span>
          </div>
          {itemsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="h-16 rounded-xl glass border border-border-light/20 animate-shimmer"
                  style={{
                    backgroundImage: "linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent)",
                    backgroundSize: "200% 100%",
                  }}
                />
              ))}
            </div>
          ) : recentItems.length === 0 ? (
            <div className="p-6 rounded-xl glass border border-border-light/20 text-center">
              <CheckCircle2 className="w-10 h-10 text-success mx-auto mb-2 opacity-50" />
              <p className="text-muted-light text-sm">All caught up!</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {recentItems.map((ai, idx) => (
                <li
                  key={ai.id}
                  style={{
                    animation: `float-up 0.6s ease-out ${idx * 50}ms both`,
                  }}
                  className="p-4 rounded-xl glass border border-border-light/20 hover:border-accent/40 transition-all duration-300 hover:shadow-lg hover:shadow-accent/10 group cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-lg border-2 border-muted-light group-hover:border-accent group-hover:bg-accent/20 transition-all mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-white group-hover:text-accent transition-colors line-clamp-2">
                        {ai.text}
                      </p>
                      <p className="text-xs text-muted-light mt-1.5">
                        {ai.assignee_email && (
                          <span>{ai.assignee_email}</span>
                        )}
                        {ai.assignee_email && ai.due_date && <span> · </span>}
                        {ai.due_date && (
                          <span>Due {formatDate(ai.due_date, "MMM d")}</span>
                        )}
                      </p>
                    </div>
                  </div>
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
  index = 0,
  highlight = false,
}: {
  title: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  index?: number;
  highlight?: boolean;
}) {
  return (
    <div
      style={{
        animation: `float-up 0.6s ease-out ${index * 100}ms both`,
      }}
      className={`group relative p-5 rounded-xl border transition-all duration-300 overflow-hidden ${
        highlight
          ? "glass border-primary/40 hover:border-primary/60 shadow-lg shadow-primary/20"
          : "glass border-border-light/20 hover:border-primary/30"
      }`}
    >
      {/* Background gradient on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
      
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-light">{title}</span>
        <div className={`p-2 rounded-lg transition-all duration-300 ${
          highlight
            ? "bg-gradient-to-br from-primary/30 to-accent/30 text-primary"
            : "bg-surface-elevated text-muted-light group-hover:text-primary group-hover:bg-primary/10"
        }`}>
          <Icon className={`w-5 h-5 ${highlight ? "animate-pulse" : "group-hover:scale-110 transition-transform"}`} />
        </div>
      </div>
      <p className="text-3xl font-bold mt-3 bg-gradient-to-r from-white to-muted-light bg-clip-text text-transparent">
        {value}
      </p>
    </div>
  );
}
