"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Calendar, MessageSquare, ListTodo, ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
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
        "flex flex-col glass border-r transition-all duration-300 ease-out",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Logo Section */}
      <div className="p-6 flex items-center gap-3 border-b border-border-light/30">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary via-accent to-primary flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col gap-0.5">
            <span className="font-bold text-lg bg-gradient-to-r from-primary to-accent-light bg-clip-text text-transparent">
              MeetEdge
            </span>
            <span className="text-xs text-muted-light">AI Intelligence</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-2">
        {nav.map(({ href, label, icon: Icon }, index) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              style={{
                animation: `slide-in-left 0.5s ease-out ${index * 50}ms both`,
              }}
              className={cn(
                "relative flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all duration-300 group",
                active
                  ? "bg-gradient-to-r from-primary/30 to-accent/20 text-primary shadow-lg shadow-primary/10 border border-primary/40"
                  : "text-muted-light hover:text-white hover:bg-surface-elevated border border-transparent",
                collapsed && "justify-center"
              )}
            >
              {active && (
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/5 rounded-xl blur-xl -z-10 opacity-0 group-hover:opacity-100 transition-opacity" />
              )}
              <Icon className={cn(
                "w-5 h-5 shrink-0 transition-transform duration-300",
                active && "group-hover:scale-110"
              )} />
              {!collapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-border-light/30 space-y-3">
        {!collapsed && (
          <div className="glass rounded-lg p-3 border border-border-light/20">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center font-bold text-white text-sm flex-shrink-0 shadow-lg shadow-primary/20">
                U
              </div>
              <div className="truncate min-w-0">
                <div className="font-medium text-white text-sm truncate">User</div>
                <div className="text-xs text-muted-light truncate">Secure Edge Pvt Ltd</div>
              </div>
            </div>
          </div>
        )}
        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "w-full flex items-center justify-center p-2.5 rounded-lg text-muted-light hover:text-white transition-all duration-300 hover:bg-surface-elevated border border-border-light/20",
            collapsed && "justify-center"
          )}
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
    </aside>
  );
}
