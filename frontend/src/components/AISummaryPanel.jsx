export default function AISummaryPanel({ aiSummary, loading, onGenerate }) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">AI Summary</h3>
        <button
          onClick={onGenerate}
          disabled={loading}
          className="rounded-lg bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950 hover:bg-cyan-400 disabled:opacity-60"
        >
          {loading ? 'Generating...' : 'Generate AI Summary'}
        </button>
      </div>
      <p className="mb-3 text-xs text-amber-300">
        Disclaimer: AI-generated analysis may be inaccurate and must be validated by a human analyst.
      </p>

      {!aiSummary ? (
        <p className="text-sm text-slate-400">No AI summary yet.</p>
      ) : (
        <div className="space-y-3 text-sm text-slate-200">
          <Panel title="Suspicious patterns" items={aiSummary.suspicious_patterns} />
          <Panel title="Most likely attack techniques" items={aiSummary.most_likely_attack_techniques} />
          <Panel title="Recommended detections" items={aiSummary.recommended_actions} />
          <Panel title="Limitations" items={aiSummary.limitations} />
        </div>
      )}
    </section>
  )
}

function Panel({ title, items = [] }) {
  return (
    <div>
      <div className="font-semibold text-cyan-300">{title}</div>
      <ul className="list-inside list-disc text-slate-300">
        {items.length === 0 ? <li>None reported.</li> : items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  )
}
