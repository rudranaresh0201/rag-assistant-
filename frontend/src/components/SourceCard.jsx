export default function SourceCard({ source }) {
  const rawText = String(source?.content ?? "").trim();   // ✅ FIXED
  const text = rawText.length > 150 ? `${rawText.slice(0, 150)}...` : rawText;

  const fileName = String(source?.document ?? "Source");  // ✅ FIXED
  const score = Number(source?.score ?? 0);

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3 shadow-md backdrop-blur transition duration-300 hover:-translate-y-0.5 hover:border-cyan-300/30 hover:bg-white/[0.05] hover:shadow-[0_8px_24px_rgba(14,116,144,0.2)]">
      
      <p className="text-xs leading-relaxed text-slate-300">
        {text || "Relevant context retrieved from documents."}
      </p>

      <div className="mt-2 flex items-center justify-between gap-2 text-[11px] text-slate-400">
        <span className="truncate">{fileName}</span>

        <span className="rounded-full border border-cyan-300/30 bg-cyan-400/10 px-2 py-0.5 text-cyan-200">
          {score.toFixed(2)}
        </span>
      </div>

    </div>
  );
}