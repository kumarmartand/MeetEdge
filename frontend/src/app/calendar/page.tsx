"use client";

import { useEffect, useState } from "react";
import { calendar as api } from "@/lib/api";
import type { CalendarEvent } from "@/types";

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .events()
      .then((r) => setEvents(r.events))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const onSync = () => {
    setSyncing(true);
    api
      .sync()
      .then(() => load())
      .finally(() => setSyncing(false));
  };

  return (
    <main style={{ padding: "2rem", maxWidth: 960, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>Calendar</h1>
        <button
          type="button"
          onClick={onSync}
          disabled={syncing}
          style={{
            padding: "0.5rem 1rem",
            background: "var(--accent)",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: syncing ? "not-allowed" : "pointer",
          }}
        >
          {syncing ? "Syncing…" : "Sync from Google"}
        </button>
      </div>
      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading events…</p>
      ) : events.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>No events. Sync to pull from Google Calendar.</p>
      ) : (
        <ul style={{ listStyle: "none" }}>
          {events.map((e) => (
            <li
              key={e.id}
              style={{
                padding: "0.75rem",
                border: "1px solid var(--border)",
                borderRadius: 8,
                marginBottom: "0.5rem",
              }}
            >
              <strong>{e.title}</strong>
              <div style={{ fontSize: "0.875rem", color: "var(--muted)" }}>
                {e.start} – {e.end}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
