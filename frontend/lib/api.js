const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MARKER = "\n[[SOURCES]]";

export class ChatError extends Error {}

// Hide the sources trailer (or a partial prefix of it) while text is still streaming.
function visibleText(raw) {
  const idx = raw.indexOf(MARKER);
  if (idx !== -1) return raw.slice(0, idx);
  for (let n = Math.min(MARKER.length - 1, raw.length); n > 0; n--) {
    if (raw.endsWith(MARKER.slice(0, n))) return raw.slice(0, raw.length - n);
  }
  return raw;
}

export async function streamChat(message, history, onText) {
  let res;
  try {
    res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });
  } catch {
    throw new ChatError("Can't reach the IT Support service. Please check that the backend is running.");
  }

  if (!res.ok) {
    if (res.status === 422) throw new ChatError("Please enter a message of up to 2000 characters.");
    let detail = "Something went wrong. Please try again.";
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {}
    throw new ChatError(detail);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let raw = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      raw += decoder.decode(value, { stream: true });
      onText(visibleText(raw));
    }
  } catch {
    // Network drop mid-stream: fall through and report as interrupted below.
  }

  const idx = raw.indexOf(MARKER);
  if (idx === -1) return { text: visibleText(raw), sources: [], interrupted: true };
  let sources = [];
  try {
    sources = JSON.parse(raw.slice(idx + MARKER.length)).sources ?? [];
  } catch {}
  return { text: raw.slice(0, idx), sources, interrupted: false };
}
