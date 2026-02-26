import Link from "next/link";
import type { Meeting } from "@/types";

interface Props {
  meeting: Meeting;
}

export default function MeetingCard({ meeting }: Props) {
  const start = new Date(meeting.start_time).toLocaleString();
  const end = new Date(meeting.end_time).toLocaleTimeString();

  return (
    <article
      style={{
        padding: "1.25rem",
        border: "1px solid var(--border)",
        borderRadius: 12,
        background: "var(--surface)",
      }}
    >
      <Link href={`/meetings/${meeting.id}`}>
        <h2 style={{ marginBottom: "0.5rem", fontSize: "1.125rem" }}>{meeting.title}</h2>
      </Link>
      <p style={{ fontSize: "0.875rem", color: "var(--muted)" }}>
        {start} – {end}
      </p>
      {meeting.attendees.length > 0 && (
        <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginTop: "0.5rem" }}>
          {meeting.attendees.map((a) => a.email).join(", ")}
        </p>
      )}
      {meeting.action_items.length > 0 && (
        <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
          {meeting.action_items.length} action item(s)
        </p>
      )}
    </article>
  );
}
