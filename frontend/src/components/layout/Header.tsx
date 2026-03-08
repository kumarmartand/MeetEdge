"use client";

import { usePathname } from "next/navigation";
import { Bell, User, Calendar, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const titles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/meetings": "Meetings",
  "/chat": "AI Chat",
  "/action-items": "Action Items",
  "/login": "Sign in",
};

function getTitle(pathname: string): string {
  if (pathname.startsWith("/meetings/") && pathname !== "/meetings") return "Meeting details";
  return titles[pathname] ?? "MeetEdge";
}

export default function Header() {
  const pathname = usePathname();
  const title = getTitle(pathname);

  return (
    <header className="h-16 glass border-b border-border-light/30 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-muted-light bg-clip-text text-transparent">
          {title}
        </h1>
      </div>
      
      <div className="flex items-center gap-2">
        {/* Status Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg glass border border-border-light/20">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="text-xs font-medium text-muted-light">Live Sync</span>
        </div>

        {/* Notifications */}
        <button
          type="button"
          className="relative p-2.5 rounded-lg transition-all duration-300 text-muted-light hover:text-primary hover:bg-surface-elevated border border-border-light/20 group"
        >
          <Bell className="w-5 h-5 transition-transform group-hover:scale-110" />
          <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-gradient-to-br from-primary to-accent rounded-full animate-pulse shadow-lg shadow-primary/50" />
        </button>

        {/* User Profile */}
        <button
          type="button"
          className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-all duration-300 text-muted-light hover:text-white hover:bg-surface-elevated border border-border-light/20 group"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary via-accent to-primary flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20 group-hover:shadow-primary/40 transition-shadow">
            <User className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-medium max-w-[100px] truncate hidden sm:block group-hover:text-primary transition-colors">
            Profile
          </span>
        </button>
      </div>
    </header>
  );
}
