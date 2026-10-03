import { useState, useEffect, useCallback } from 'react'
import { Clock, CheckCircle2 } from 'lucide-react'
import { apiClient, type HistoryEntry } from '@/lib/api'
import { toast } from 'sonner'

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getHistory(days)
      setEntries(res.data.entries)
    } catch {
      toast.error('Could not load history.')
    } finally {
      setLoading(false)
    }
  }, [days])

  useEffect(() => { load() }, [load])

  // Group by date
  const grouped: Record<string, HistoryEntry[]> = {}
  for (const entry of entries) {
    const date = entry.completed_at.split('T')[0]
    if (!grouped[date]) grouped[date] = []
    grouped[date].push(entry)
  }
  const dates = Object.keys(grouped).sort().reverse()

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="text-2xl font-serif text-ink-100">History</h1>
        <p className="text-sm text-ink-400 mt-1">
          Here''s where you''ve been. Just patterns, no pressure.
        </p>
      </div>

      {/* Time range selector */}
      <div className="flex gap-2">
        {[7, 30, 90].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-3 py-1.5 rounded-xl text-sm transition-colors ${
              days === d
                ? 'bg-teal-500 text-white'
                : 'bg-plum-100 text-plum-500 hover:bg-plum-200'
            }`}
          >
            {d} days
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-ink-400 text-sm">Loading...</p>
      ) : entries.length === 0 ? (
        <div className="text-center py-12 space-y-2">
          <Clock className="h-10 w-10 text-violet-400 mx-auto" strokeWidth={1.5} />
          <p className="text-sm text-ink-400">
            Nothing here yet. That''s okay. Start when you''re ready.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {dates.map((date) => {
            const dayEntries = grouped[date]
            const dayDate = new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
              weekday: 'short', month: 'short', day: 'numeric',
            })
            return (
              <div key={date} className="space-y-1.5">
                <p className="text-xs font-medium text-ink-400">{dayDate}</p>
                <div className="space-y-1">
                  {dayEntries.map((entry, i) => (
                    <div key={i} className="flex items-center gap-2 pl-1">
                      <CheckCircle2 className="h-4 w-4 text-teal-400 flex-shrink-0" strokeWidth={1.5} />
                      <span className="text-sm text-ink-200">{entry.task_title}</span>
                      <span className="text-[11px] text-ink-400 ml-auto">{entry.zone}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <p className="text-xs text-ink-400 italic text-center pt-2">
        No streaks to break. Just a record of what you''ve done.
      </p>
    </div>
  )
}
