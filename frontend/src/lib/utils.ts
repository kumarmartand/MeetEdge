import { clsx, type ClassValue } from "clsx";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...classes: ClassValue[]): string {
  return clsx(classes);
}

export function formatDate(date: string | Date, formatStr: string = "PPp"): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return format(d, formatStr);
}

export function formatDuration(startTime: string, endTime: string): string {
  const start = new Date(startTime).getTime();
  const end = new Date(endTime).getTime();
  const mins = Math.round((end - start) / 60000);
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export type MeetingStatus = "scheduled" | "live" | "completed" | "failed";

export function getStatusColor(status: MeetingStatus): string {
  switch (status) {
    case "scheduled":
      return "bg-primary/20 text-primary border-primary/30";
    case "live":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "completed":
      return "bg-muted/20 text-muted border-muted/30";
    case "failed":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-muted/20 text-muted border-muted/30";
  }
}

export function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .map((s) => s[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "…";
}

export function debounce<A extends unknown[]>(fn: (...args: A) => void, delay: number): (...args: A) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  return (...args: A) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}
