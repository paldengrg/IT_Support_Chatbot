"use client";

import { useEffect, useRef, useState } from "react";
import ChatInput from "./ChatInput";
import Message from "./Message";
import { streamChat } from "../lib/api";

const WELCOME = {
  role: "assistant",
  content:
    "Hi! I'm the IT Support Assistant. Ask me about troubleshooting, software installation, networking, accounts, or software licenses.",
  welcome: true,
};

export default function ChatWindow() {
  const [messages, setMessages] = useState([WELCOME]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const updateLast = (patch) =>
    setMessages((prev) => {
      const next = [...prev];
      next[next.length - 1] = { ...next[next.length - 1], ...patch };
      return next;
    });

  async function send(text) {
    const history = messages
      .filter((m) => !m.welcome && !m.interrupted && m.content)
      .slice(-10)
      .map(({ role, content }) => ({ role, content }));

    setError(null);
    setBusy(true);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "", pending: true },
    ]);

    try {
      const result = await streamChat(text, history, (partial) =>
        updateLast({ content: partial, pending: partial.length === 0 }),
      );
      updateLast({
        content: result.text,
        sources: result.sources,
        interrupted: result.interrupted,
        pending: false,
      });
    } catch (err) {
      setMessages((prev) => prev.slice(0, -1));
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function clear() {
    setMessages([WELCOME]);
    setError(null);
  }

  return (
    <div className="chat">
      <header className="chat-header">
        <div>
          <h1>IT Support Assistant</h1>
          <p>Troubleshooting · Software · Networking · Licensing</p>
        </div>
        <button className="clear" onClick={clear} disabled={busy}>
          Clear chat
        </button>
      </header>

      <main className="chat-messages">
        {messages.map((m, i) => (
          <Message key={i} message={m} />
        ))}
        <div ref={endRef} />
      </main>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <ChatInput onSend={send} disabled={busy} />
    </div>
  );
}
