"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Calendar, MessageSquare, ListTodo, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/meetings", label: "Meetings", icon: Calendar },
  { href: "/chat", label: "AI Chat", icon: MessageSquare },
  { href: "/action-items", label: "Action Items", icon: ListTodo },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border bg-surface transition-all duration-200",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="p-4 flex items-center gap-2 border-b border-border">
        {!collapsed && (
          <span className="font-semibold text-lg text-primary">MeetEdge</span>
        )}
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-primary/20 text-primary border-l-2 border-primary"
                  : "text-muted hover:bg-border/50 hover:text-white",
                collapsed && "justify-center"
              )}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-border">
        {!collapsed && (
          <div className="flex items-center gap-2 px-2 py-1 text-muted text-xs">
            <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center font-medium text-primary">
              U
            </div>
            <div className="truncate">
              <div className="font-medium text-white">User</div>
              <div>Secure Edge Pvt Ltd</div>
            </div>
          </div>
        )}
        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          className="mt-2 w-full flex items-center justify-center p-2 rounded-lg text-muted hover:bg-border hover:text-white"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
    </aside>
  );
}
