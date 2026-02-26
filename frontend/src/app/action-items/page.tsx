"use client";

import { useQuery } from "@tanstack/react-query";
import { actionItems as actionItemsApi } from "@/lib/api";
import { formatDate, getInitials } from "@/lib/utils";
import { Download } from "lucide-react";
import { useState } from "react";

const COLUMNS = [
  { id: "open", title: "Open" },
  { id: "in_progress", title: "In Progress" },
  { id: "completed", title: "Completed" },
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
      <div className="grid grid-cols-3 gap-4">
        {COLUMNS.map((col) => (
          <div key={col.id} className="rounded-lg border border-border bg-surface p-4">
            <h3 className="font-semibold mb-4">{col.title}</h3>
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 rounded bg-background animate-pulse" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 justify-between items-center">
        <div className="flex gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-surface border border-border text-white"
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
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {COLUMNS.map((col) => (
          <div key={col.id} className="rounded-lg border border-border bg-surface p-4 min-h-[400px]">
            <h3 className="font-semibold mb-4">{col.title}</h3>
            <div className="space-y-2">
              {(col.id === "open" ? open : col.id === "in_progress" ? inProgress : completed).map((ai) => (
                <ActionCard
                  key={ai.id}
                  item={ai}
                  onStatusChange={(status) => updateStatus(ai.id, status)}
                />
              ))}
            </div>
          </div>
        ))}
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
    <div className="p-3 rounded-lg bg-background border border-border">
      <p className="text-sm">{item.text}</p>
      <div className="flex items-center gap-2 mt-2">
        {item.assignee_email && (
          <span
            className="w-6 h-6 rounded-full bg-primary/30 flex items-center justify-center text-xs font-medium text-primary"
            title={item.assignee_email}
          >
            {getInitials(item.assignee_email)}
          </span>
        )}
        {item.due_date && (
          <span
            className={`text-xs px-1.5 py-0.5 rounded ${
              isOverdue ? "bg-red-500/20 text-red-400" : "bg-muted/20 text-muted"
            }`}
          >
            {formatDate(item.due_date, "MMM d")}
          </span>
        )}
        {item.priority && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-border text-muted">
            {item.priority}
          </span>
        )}
      </div>
      <select
        value={item.status}
        onChange={(e) => onStatusChange(e.target.value)}
        className="mt-2 w-full text-xs px-2 py-1 rounded bg-surface border border-border"
      >
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
      </select>
    </div>
  );
}
