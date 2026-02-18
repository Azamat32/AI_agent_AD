export default function AnalysisPanel({ stats, suspicious }) {
  if (!stats) return null

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <section className="rounded-2xl border border-slate-700 bg-slate-900 p-4">
        <h3 className="mb-2 text-lg font-semibold">Dataset Info</h3>
        <ul className="space-y-1 text-sm text-slate-300">
          <li>Rows: {stats.rows}</li>
          <li>Columns: {stats.cols}</li>
          <li>Detected important columns: {(stats.important_columns_detected || []).join(', ') || 'None'}</li>
        </ul>
      </section>

      <section className="rounded-2xl border border-slate-700 bg-slate-900 p-4">
        <h3 className="mb-2 text-lg font-semibold">Missing Values</h3>
        <div className="max-h-40 overflow-auto text-sm text-slate-300">
          {Object.entries(stats.missing_values || {}).map(([col, count]) => (
            <div key={col} className="flex justify-between border-b border-slate-800 py-1">
              <span>{col}</span>
              <span>{count}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-700 bg-slate-900 p-4 md:col-span-2">
        <h3 className="mb-2 text-lg font-semibold">Suspicious Detections</h3>
        <div className="space-y-2 text-sm">
          {(suspicious?.detections || []).length === 0 && (
            <p className="text-slate-400">No suspicious detections from current rules.</p>
          )}
          {(suspicious?.detections || []).map((detection) => (
            <div key={detection.rule} className="rounded-lg border border-slate-700 bg-slate-950 p-3">
              <div className="font-medium text-cyan-300">{detection.rule}</div>
              <div className="text-slate-300">{detection.description}</div>
              <pre className="mt-2 whitespace-pre-wrap text-xs text-slate-400">
                {JSON.stringify(detection.evidence, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
