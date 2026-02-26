"use client";

import { useState } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface Props {
  meetingId?: number;
  onSend?: (message: string) => Promise<string>;
}

export default function ChatInterface({ meetingId, onSend }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    try {
      const reply = onSend ? await onSend(text) : "Chat integration not configured.";
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: "Sorry, something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: 12,
        overflow: "hidden",
        background: "var(--surface)",
      }}
    >
      <div
        style={{
          padding: "0.75rem 1rem",
          borderBottom: "1px solid var(--border)",
          fontSize: "0.875rem",
          color: "var(--muted)",
        }}
      >
        Chat {meetingId != null ? `· Meeting #${meetingId}` : ""}
      </div>
      <div
        style={{
          minHeight: 200,
          maxHeight: 400,
          overflowY: "auto",
          padding: "1rem",
        }}
      >
        {messages.length === 0 ? (
          <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
            Ask a question about this meeting…
          </p>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              style={{
                marginBottom: "0.75rem",
                padding: "0.5rem 0",
                borderBottom: "1px solid var(--border)",
              }}
            >
              <span
                style={{
                  fontSize: "0.75rem",
                  color: "var(--muted)",
                  textTransform: "uppercase",
                }}
              >
                {m.role}
              </span>
              <p style={{ marginTop: "0.25rem" }}>{m.content}</p>
            </div>
          ))
        )}
      </div>
      <form onSubmit={handleSubmit} style={{ padding: "0.75rem", borderTop: "1px solid var(--border)" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message…"
          disabled={sending}
          style={{
            width: "100%",
            padding: "0.5rem 0.75rem",
            background: "var(--bg)",
            border: "1px solid var(--border)",
            borderRadius: 6,
            color: "var(--text)",
          }}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          style={{
            marginTop: "0.5rem",
            padding: "0.5rem 1rem",
            background: "var(--accent)",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: sending ? "not-allowed" : "pointer",
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
