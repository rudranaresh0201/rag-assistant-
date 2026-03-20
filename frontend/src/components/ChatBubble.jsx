import { useState } from "react";
import SourceCard from "./SourceCard";

export default function ChatBubble({ role, content, sources = [] }) {
  const [openSources, setOpenSources] = useState(false);
  const isUser = role === "user";

  return (
    <div className={`mb-5 flex animate-fade-up ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`w-fit max-w-[88%] rounded-xl px-4 py-3 shadow-lg transition duration-300 ${
          isUser
            ? "rounded-br-md bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 shadow-[0_0_24px_rgba(56,189,248,0.32)]"
            : "rounded-bl-md border border-white/10 bg-white/5 text-slate-100 backdrop-blur"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-balance">{content}</p>

        {!isUser && sources.length > 0 && (
          <div className="mt-4 border-t border-white/10 pt-3">
            <button
              type="button"
              onClick={() => setOpenSources((prev) => !prev)}
              className="rounded-md px-2 py-1 text-xs text-cyan-300 transition duration-300 hover:scale-[1.02] hover:bg-cyan-400/10 hover:text-cyan-200"
            >
              {openSources ? "Hide Sources" : "Show Sources"}
            </button>

            {openSources && (
              <div className="mt-2 space-y-2">
                {sources.map((source, index) => (
                  <SourceCard key={`${source.source || "src"}-${index}`} source={source} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
