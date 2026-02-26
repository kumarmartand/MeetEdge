"use client";

import { usePathname } from "next/navigation";
import { Bell, User, Calendar } from "lucide-react";
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
    <header className="h-14 border-b border-border bg-surface/80 flex items-center justify-between px-6 shrink-0">
      <h1 className="text-lg font-semibold">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1.5 text-muted text-sm">
          <Calendar className="w-4 h-4" />
          Synced
        </span>
        <button type="button" className="relative p-2 rounded-lg hover:bg-border text-muted hover:text-white">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
        </button>
        <button type="button" className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-border">
          <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
          <span className="text-sm max-w-[100px] truncate hidden sm:block">Profile</span>
        </button>
      </div>
    </header>
  );
}
