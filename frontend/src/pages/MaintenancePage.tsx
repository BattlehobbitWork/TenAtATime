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

  if (loading) return <div className="flex items-center justify-center py-20"><p className="text-warm-400 text-sm">Loading...</p></div>
  if (!summary) return null

  const sorted = [...summary.maintenance].sort((a, b) => a.days_until_due - b.days_until_due)

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="text-2xl font-serif text-warm-700">Home Care</h1>
        <p className="text-sm text-warm-400 mt-1">
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

      <p className="text-xs text-warm-400 italic text-center pt-2">
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
          ? 'bg-cream-100 opacity-60 border-cream-200'
          : is_due_soon || days_until_due <= 0
          ? 'bg-terracotta-400/10 border-terracotta-400/30 hover:bg-terracotta-400/15'
          : 'bg-cream-100 border-cream-200 hover:bg-cream-200'
      )}
    >
      {is_done_today ? (
        <CheckCircle2 className="h-5 w-5 text-sage-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      ) : (
        <Circle className="h-5 w-5 text-warm-300 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      )}
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm', is_done_today ? 'text-warm-400 line-through' : 'text-warm-700')}>
          {task.title}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="flex items-center gap-0.5 text-[11px] text-warm-400">
            <Calendar className="h-3 w-3" strokeWidth={1.5} />
            {dueText}
          </span>
          <span className="flex items-center gap-0.5 text-[11px] text-warm-400">
            <Clock className="h-3 w-3" strokeWidth={1.5} />
            {task.estimated_minutes} min
          </span>
        </div>
      </div>
    </button>
  )
}
