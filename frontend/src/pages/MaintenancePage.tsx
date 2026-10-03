import { useState, useEffect, useCallback } from 'react'
import { Wrench, CheckCircle2, Circle, Clock, Calendar } from 'lucide-react'
import { apiClient, type TodaySummary, type MaintenanceOut } from '@/lib/api'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export default function MaintenancePage() {
  const [summary, setSummary] = useState<TodaySummary | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getToday()
      setSummary(res.data)
    } catch {
      toast.error('Could not load maintenance tasks.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleComplete = async (taskId: number) => {
    try {
      await apiClient.completeTask(taskId)
      toast.success('Done.')
      load()
    } catch {
      toast.error('Could not save.')
    }
  }

  if (loading) return <div className="flex items-center justify-center py-20"><p className="text-ink-400 text-sm">Loading...</p></div>
  if (!summary) return null

  const sorted = [...summary.maintenance].sort((a, b) => a.days_until_due - b.days_until_due)

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="text-2xl font-serif text-ink-100">Home Care</h1>
        <p className="text-sm text-ink-400 mt-1">
          Maintenance and seasonal tasks. Only when you''re ready.
        </p>
      </div>

      <div className="space-y-2">
        {sorted.map((m) => (
          <MaintenanceCard
            key={m.task.id}
            maintenance={m}
            onComplete={() => handleComplete(m.task.id)}
          />
        ))}
      </div>

      <p className="text-xs text-ink-400 italic text-center pt-2">
        No rush. These are here when you need them.
      </p>
    </div>
  )
}

function MaintenanceCard({
  maintenance, onComplete,
}: {
  maintenance: MaintenanceOut
  onComplete: () => void
}) {
  const { task, days_until_due, is_done_today, is_due_soon } = maintenance

  const dueText = days_until_due <= 0
    ? 'Ready when you are'
    : days_until_due === 1
    ? 'Tomorrow, maybe'
    : days_until_due <= 7
    ? `In ${days_until_due} days`
    : `In ${Math.ceil(days_until_due / 7)} weeks`

  return (
    <button
      onClick={onComplete}
      disabled={is_done_today}
      className={cn(
        'w-full flex items-start gap-3 p-3 rounded-2xl text-left transition-colors border',
        is_done_today
          ? 'bg-plum-100 opacity-60 border-plum-200'
          : is_due_soon || days_until_due <= 0
          ? 'bg-coral-400/10 border-coral-400/30 hover:bg-coral-400/15'
          : 'bg-plum-100 border-plum-200 hover:bg-plum-200'
      )}
    >
      {is_done_today ? (
        <CheckCircle2 className="h-5 w-5 text-teal-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      ) : (
        <Circle className="h-5 w-5 text-violet-400 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      )}
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm', is_done_today ? 'text-ink-400 line-through' : 'text-ink-100')}>
          {task.title}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="flex items-center gap-0.5 text-[11px] text-ink-400">
            <Calendar className="h-3 w-3" strokeWidth={1.5} />
            {dueText}
          </span>
          <span className="flex items-center gap-0.5 text-[11px] text-ink-400">
            <Clock className="h-3 w-3" strokeWidth={1.5} />
            {task.estimated_minutes} min
          </span>
        </div>
      </div>
    </button>
  )
}
