"use client";

import { useQuery } from "@tanstack/react-query";
import { actionItems as actionItemsApi } from "@/lib/api";
import { formatDate, getInitials } from "@/lib/utils";
import { Download, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { useState } from "react";

const COLUMNS = [
  { id: "open", title: "Open", icon: AlertCircle, color: "from-red-500" },
  { id: "in_progress", title: "In Progress", icon: Clock, color: "from-yellow-500" },
  { id: "completed", title: "Completed", icon: CheckCircle2, color: "from-green-500" },
];

export default function ActionItemsPage() {
  const { data: items = [], isLoading } = useQuery({
    queryKey: ["action-items"],
    queryFn: () => actionItemsApi.list(),
  });
  const [statusFilter, setStatusFilter] = useState<string>("");

  const filtered = statusFilter ? items.filter((i) => i.status === statusFilter) : items;
  const open = filtered.filter((i) => i.status === "open");
  const inProgress = filtered.filter((i) => i.status === "in_progress");
  const completed = filtered.filter((i) => i.status === "completed" || i.completed);

  const handleExport = () => {
    window.open("/api/v1/action-items/export/csv", "_blank");
  };

  const updateStatus = async (id: number, status: string) => {
    await actionItemsApi.update(id, { status, completed: status === "completed" });
    window.location.reload();
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {COLUMNS.map((col) => (
          <div key={col.id} className="rounded-2xl glass border border-border-light/20 p-6">
            <h3 className="font-bold text-lg mb-4 text-white">{col.title}</h3>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 rounded-xl glass border border-border-light/20 animate-shimmer" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-float-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="flex gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2.5 rounded-lg glass border border-border-light/20 text-white font-medium hover:border-primary/40 transition-all focus:outline-none"
          >
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <button
          type="button"
          onClick={handleExport}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-bold hover:shadow-lg hover:shadow-primary/30 transition-all"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {COLUMNS.map((col, colIdx) => {
          const Icon = col.icon;
          const items = col.id === "open" ? open : col.id === "in_progress" ? inProgress : completed;
          
          return (
            <div
              key={col.id}
              style={{
                animation: `float-up 0.6s ease-out ${colIdx * 100}ms both`,
              }}
              className="rounded-2xl glass border border-border-light/20 p-6 min-h-[500px] flex flex-col"
            >
              {/* Column Header */}
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-border-light/10">
                <div className={`p-2.5 rounded-lg bg-gradient-to-br ${col.color}/20 to-transparent`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-white">{col.title}</h3>
                  <span className="text-xs text-muted-light">{items.length} items</span>
                </div>
              </div>

              {/* Cards */}
              <div className="space-y-3 flex-1 overflow-y-auto">
                {items.length === 0 ? (
                  <div className="flex items-center justify-center h-32 text-muted-light">
                    <p className="text-sm">No items</p>
                  </div>
                ) : (
                  items.map((ai, idx) => (
                    <div
                      key={ai.id}
                      style={{
                        animation: `float-up 0.5s ease-out ${idx * 30}ms both`,
                      }}
                    >
                      <ActionCard
                        item={ai}
                        onStatusChange={(status) => updateStatus(ai.id, status)}
                      />
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ActionCard({
  item,
  onStatusChange,
}: {
  item: { id: number; text: string; assignee_email: string | null; due_date: string | null; status: string; priority?: string | null };
  onStatusChange: (status: string) => void;
}) {
  const isOverdue = item.due_date && new Date(item.due_date) < new Date();

  return (
    <div className="group p-4 rounded-xl glass border border-border-light/20 hover:border-primary/40 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 cursor-grab active:cursor-grabbing">
      {/* Checkbox & Text */}
      <div className="flex items-start gap-3 mb-3">
        <input
          type="checkbox"
          checked={item.status === "completed"}
          onChange={(e) => onStatusChange(e.target.checked ? "completed" : "open")}
          className="mt-1 w-5 h-5 rounded-lg border-2 border-muted-light accent-primary cursor-pointer"
        />
        <p className="text-sm font-medium text-white flex-1 group-hover:text-primary transition-colors line-clamp-3">
          {item.text}
        </p>
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-2 flex-wrap mt-3 pt-3 border-t border-border-light/10">
        {item.assignee_email && (
          <span
            className="w-6 h-6 rounded-lg bg-gradient-to-br from-primary/40 to-accent/40 flex items-center justify-center text-xs font-bold text-white flex-shrink-0 hover:scale-110 transition-transform"
            title={item.assignee_email}
          >
            {getInitials(item.assignee_email)}
          </span>
        )}
        {item.due_date && (
          <span
            className={`text-xs font-semibold px-2 py-1 rounded-lg ${
              isOverdue 
                ? "glass border border-error/40 bg-error/10 text-error" 
                : "glass border border-muted-light/30 bg-muted-light/5 text-muted-light"
            }`}
          >
            {formatDate(item.due_date, "MMM d")}
          </span>
        )}
        {item.priority && (
          <span className="text-xs font-semibold px-2 py-1 rounded-lg glass border border-warning/40 bg-warning/10 text-warning">
            {item.priority}
          </span>
        )}
      </div>

      {/* Status Selector */}
      <select
        value={item.status}
        onChange={(e) => onStatusChange(e.target.value)}
        className="mt-3 w-full text-xs px-2 py-1.5 rounded-lg glass border border-border-light/20 text-white font-medium focus:outline-none hover:border-primary/40 transition-all"
      >
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
      </select>
    </div>
  );
}
