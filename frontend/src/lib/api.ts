/**
 * Full API client for MeetEdge backend.
 * Base URL uses Next.js rewrites: /api/v1/* -> localhost:8000/api/v1/*
 */

const BASE = "/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail ?? "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const health = {
  get: () => request<{ status: string }>("/health"),
  ready: () => request<{ ready: boolean }>("/health/ready"),
};

export const meetings = {
  list: (params?: { status?: string; search?: string; limit?: number; offset?: number }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.search) sp.set("search", params.search);
    if (params?.limit != null) sp.set("limit", String(params.limit));
    if (params?.offset != null) sp.set("offset", String(params.offset));
    const q = sp.toString() ? `?${sp}` : "";
    return request<import("@/types/meeting").Meeting[]>(`/meetings${q}`);
  },
  get: (id: number) => request<import("@/types/meeting").Meeting>(`/meetings/${id}`),
  create: (body: import("@/types/meeting").MeetingCreate) =>
    request<import("@/types/meeting").Meeting>("/meetings", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  update: (id: number, body: import("@/types/meeting").MeetingUpdate) =>
    request<import("@/types/meeting").Meeting>(`/meetings/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  delete: (id: number) => request<void>(`/meetings/${id}`, { method: "DELETE" }),
};

export const calendar = {
  sync: () => request<{ synced: number; skipped?: number }>("/calendar/sync", { method: "POST" }),
  upcoming: () => request<{ events: unknown[] }>("/calendar/upcoming"),
  authStatus: () => request<{ authenticated: boolean }>("/calendar/auth/status"),
  events: () => request<{ events: import("@/types/api").CalendarEvent[] }>("/calendar/events"),
};

export const actionItems = {
  list: (params?: { status?: string; meeting_id?: number; assigned_to?: string; priority?: string }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.meeting_id != null) sp.set("meeting_id", String(params.meeting_id));
    if (params?.assigned_to) sp.set("assigned_to", params.assigned_to);
    if (params?.priority) sp.set("priority", params.priority);
    const q = sp.toString() ? `?${sp}` : "";
    return request<import("@/types/meeting").ActionItem[]>(`/action-items${q}`);
  },
  get: (id: number) => request<import("@/types/meeting").ActionItem>(`/action-items/${id}`),
  update: (id: number, body: import("@/types/api").ActionItemUpdate) =>
    request<import("@/types/meeting").ActionItem>(`/action-items/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  delete: (id: number) => request<void>(`/action-items/${id}`, { method: "DELETE" }),
  exportCsv: () => fetch(`${BASE}/action-items/export/csv`),
};

export const chat = {
  query: (body: import("@/types/api").ChatQueryRequest) =>
    request<import("@/types/api").ChatQueryResponse>("/chat/query", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

export default { health, meetings, calendar, actionItems, chat };
