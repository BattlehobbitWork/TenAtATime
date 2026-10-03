import { useState, useEffect, useCallback } from 'react'
import { MapPin, CheckCircle2, Circle, Clock } from 'lucide-react'
import { apiClient, type TodaySummary } from '@/lib/api'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export default function ZonePage() {
  const [summary, setSummary] = useState<TodaySummary | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getToday()
      setSummary(res.data)
    } catch {
      toast.error('Could not load zones.')
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

  const zoneName = summary.zone[0]?.zone || "This week's zone"
  const zoneTasks = summary.zone

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="text-2xl font-serif text-ink-100">This Week''s Zone</h1>
        <p className="text-sm text-ink-400 mt-1 flex items-center gap-1">
          <MapPin className="h-4 w-4" strokeWidth={1.5} />
          {zoneName}
        </p>
      </div>

      {zoneTasks.length === 0 ? (
        <p className="text-sm text-ink-400 italic">No zone tasks this week.</p>
      ) : (
        <div className="space-y-2">
          {zoneTasks.map((task) => (
            <button
              key={task.id}
              onClick={() => handleComplete(task.id)}
              disabled={task.is_done_today}
              className={cn(
                'w-full flex items-start gap-3 p-3 rounded-2xl text-left transition-colors',
                task.is_done_today
                  ? 'bg-plum-100 opacity-60'
                  : 'bg-plum-100 hover:bg-plum-200'
              )}
            >
              {task.is_done_today ? (
                <CheckCircle2 className="h-5 w-5 text-teal-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
              ) : (
                <Circle className="h-5 w-5 text-violet-400 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
              )}
              <div className="flex-1">
                <p className={cn('text-sm', task.is_done_today ? 'text-ink-400 line-through' : 'text-ink-100')}>
                  {task.title}
                </p>
                <span className="flex items-center gap-0.5 text-[11px] text-ink-400 mt-0.5">
                  <Clock className="h-3 w-3" strokeWidth={1.5} />
                  {task.estimated_minutes} min
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      <p className="text-xs text-ink-400 italic text-center pt-2">
        Pick one or two. That''s plenty.
      </p>
    </div>
  )
}
