interface Props {
  transcript: string | null;
}

export default function TranscriptViewer({ transcript }: Props) {
  if (!transcript?.trim()) {
    return (
      <p style={{ color: "var(--muted)", fontStyle: "italic" }}>
        No transcript available for this meeting.
      </p>
    );
  }

  return (
    <div
      style={{
        padding: "1rem",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        whiteSpace: "pre-wrap",
        fontSize: "0.9375rem",
        lineHeight: 1.6,
      }}
    >
      {transcript}
    </div>
  );
}
