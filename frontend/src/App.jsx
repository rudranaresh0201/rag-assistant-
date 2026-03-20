import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import ChatBubble from "./components/ChatBubble";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8001").replace(/\/$/, "");
const QUERY_ENDPOINT = `${API_BASE_URL}/query`;

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const endRef = useRef(null);
  const scrollerRef = useRef(null);

  const hasMessages = messages.length > 0;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const latestConfidence = useMemo(() => {
    const assistantMessages = [...messages].reverse().filter((item) => item.role === "assistant");
    const latest = assistantMessages[0];
    if (!latest?.sources?.length) {
      return null;
    }
    const bestScore = latest.sources.reduce((max, source) => {
      const score = Number(source?.score ?? 0);
      return score > max ? score : max;
    }, 0);
    return bestScore;
  }, [messages]);

  const onSend = async (query) => {
    const text = query.trim();
    if (!text || loading) {
      return;
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery("");
    setLoading(true);

    try {
      const response = await axios.post(
        QUERY_ENDPOINT,
        { query: text },
        {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          timeout: 15000,
        }
      );

      if (!response?.data || typeof response.data !== "object") {
        throw new Error("EMPTY_RESPONSE");
      }

      const data = response.data ?? {};
      const answer = typeof data.answer === "string" ? data.answer : "";
      const nextSources = Array.isArray(data.sources) ? data.sources : [];
      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: answer || "The server returned an empty answer.",
        sources: nextSources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      let friendlyMessage = "Server not reachable";

      if (axios.isAxiosError(error)) {
        if (error.code === "ECONNABORTED") {
          friendlyMessage = "The server took too long to respond. Please try again.";
        } else if (!error.response) {
          friendlyMessage = "Server not reachable";
        } else if (error.response.status === 404) {
          friendlyMessage = "Endpoint not found: check backend route /query and port 8001.";
        } else {
          friendlyMessage = `Request failed with status ${error.response.status}.`;
        }
      } else if (error instanceof Error && error.message === "EMPTY_RESPONSE") {
        friendlyMessage = "The server returned an empty or invalid JSON response.";
      }

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: friendlyMessage,
        sources: [],
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSend(query);
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-black text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-16 top-8 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -right-12 bottom-20 h-80 w-80 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 pb-32 pt-6 md:px-6">
        <header className="mb-4 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_8px_30px_rgba(0,0,0,0.35)] backdrop-blur-xl transition duration-300">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold tracking-tight text-slate-50">BAJA RAG Assistant</h1>
              <p className="mt-1 text-sm text-slate-400">Futuristic retrieval chat for BAJA rules.</p>
            </div>
            {latestConfidence !== null && (
              <div className="rounded-full border border-emerald-300/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300 shadow-[0_0_20px_rgba(52,211,153,0.18)]">
                Confidence {(latestConfidence * 100).toFixed(0)}%
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-[0_20px_60px_rgba(0,0,0,0.45)] backdrop-blur-xl transition duration-300">
          <div ref={scrollerRef} className="chat-scrollbar h-[calc(100vh-220px)] overflow-y-auto p-4 md:p-6">
            {!hasMessages && (
              <div className="mt-28 text-center text-slate-400 animate-fade-up">
                <p className="text-lg text-slate-200">Start your conversation</p>
                <p className="mt-2 text-sm">Ask anything about BAJA rules...</p>
              </div>
            )}

            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                role={message.role}
                content={message.content}
                sources={message.sources || []}
              />
            ))}

            {loading && (
              <div className="mb-4 mr-auto w-fit max-w-[88%] animate-fade-up rounded-2xl rounded-bl-md border border-white/10 bg-slate-800/70 px-4 py-3 shadow-lg backdrop-blur">
                <div className="flex items-center gap-3 text-sm text-slate-200">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:120ms]" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300 [animation-delay:240ms]" />
                  <span className="ml-1">Thinking...</span>
                </div>
              </div>
            )}

            <div ref={endRef} />
          </div>
        </main>

        <form onSubmit={handleSubmit} className="fixed bottom-4 left-0 right-0 z-30 px-4 md:px-6">
          <div className="mx-auto w-full max-w-5xl">
            <div className="group flex items-center gap-3 rounded-full border border-white/15 bg-white/10 p-2 shadow-[0_8px_30px_rgba(0,0,0,0.5)] backdrop-blur-xl transition duration-300 focus-within:border-cyan-300/50 focus-within:shadow-[0_0_30px_rgba(34,211,238,0.2)]">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    onSend(query);
                  }
                }}
                placeholder="Ask anything about BAJA rules..."
                disabled={loading}
                className="h-11 flex-1 bg-transparent px-4 text-sm text-slate-100 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-70"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 shadow-[0_0_25px_rgba(34,211,238,0.28)] transition duration-300 hover:scale-105 hover:from-cyan-300 hover:to-blue-400 disabled:cursor-not-allowed disabled:scale-100 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-400"
                aria-label="Send"
              >
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M3 12h14" />
                  <path d="m11 4 8 8-8 8" />
                </svg>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
