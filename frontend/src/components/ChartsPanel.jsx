import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function ChartsPanel({ stats }) {
  const topEvents = (stats?.top_event_ids || []).map((item) => ({
    eventId: String(item.event_id),
    count: item.count,
  }))

  const successVsFailed = [
    {
      name: 'Logons',
      failed: Number(
        topEvents.find((item) => Number(item.eventId) === 4625)?.count || 0,
      ),
      successful: Number(
        topEvents.find((item) => Number(item.eventId) === 4624)?.count || 0,
      ),
    },
  ]

  const hourly = stats?.hourly_distribution || []

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <ChartCard title="Top Event IDs">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={topEvents}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="eventId" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#22d3ee" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Failed vs Successful Logons">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={successVsFailed}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="failed" fill="#f43f5e" />
            <Bar dataKey="successful" fill="#34d399" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Logons per Hour" className="md:col-span-2">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={hourly}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#818cf8" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  )
}

function ChartCard({ title, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-slate-700 bg-slate-900 p-4 ${className}`}>
      <h3 className="mb-3 text-lg font-semibold">{title}</h3>
      {children}
    </section>
  )
}
