import { useState, useEffect, useCallback } from 'react'
import { CheckCircle2, Circle, Clock, MapPin, Sparkles } from 'lucide-react'
import { apiClient, type TodaySummary, type TaskOut } from '@/lib/api'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

const CATEGORY_LABELS: Record<string, string> = {
  daily: 'Daily Anchors',
  weekly: "Today's Rhythm",
  zone: "This Week's Zone",
  monthly: 'This Month',
  maintenance: 'Home Care',
}

export default function TodayPage() {
  const [summary, setSummary] = useState<TodaySummary | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getToday()
      setSummary(res.data)
    } catch {
      toast.error('Could not load tasks. Check your connection.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleComplete = async (taskId: number) => {
    try {
      await apiClient.completeTask(taskId)
      toast.success('Done.', { description: 'One small thing taken care of.' })
      load()
    } catch {
      toast.error('Could not save. Try again.')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-ink-400 text-sm">Loading...</p>
      </div>
    )
  }

  if (!summary) return null

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric',
  })

  return (
    <div className="space-y-6">
      {/* Header -- calm, warm */}
      <div>
        <p className="text-sm text-ink-400">{today}</p>
        <h1 className="text-2xl font-serif text-ink-100 mt-1">Ready when you are.</h1>
        {summary.completed_count > 0 && (
          <p className="text-sm text-teal-500 mt-1">
            {summary.completed_count} {summary.completed_count === 1 ? 'thing' : 'things'} done today.
          </p>
        )}
      </div>

      {/* Daily anchors */}
      <TaskSection
        label={CATEGORY_LABELS.daily}
        tasks={summary.daily}
        onComplete={handleComplete}
        hint="Pick 2-3. This is enough."
      />

      {/* Weekly rhythm */}
      {summary.weekly.length > 0 && (
        <TaskSection
          label={CATEGORY_LABELS.weekly}
          tasks={summary.weekly}
          onComplete={handleComplete}
        />
      )}

      {/* Zone rotation */}
      {summary.zone.length > 0 && (
        <TaskSection
          label={CATEGORY_LABELS.zone}
          tasks={summary.zone}
          onComplete={handleComplete}
          hint="One or two is plenty."
        />
      )}

      {/* Monthly */}
      {summary.monthly.length > 0 && (
        <TaskSection
          label={CATEGORY_LABELS.monthly}
          tasks={summary.monthly}
          onComplete={handleComplete}
        />
      )}

      {/* Maintenance */}
      {summary.maintenance.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-medium text-plum-500">{CATEGORY_LABELS.maintenance}</h2>
          <div className="space-y-2">
            {summary.maintenance
              .filter(m => m.is_due_soon || m.days_until_due <= 0)
              .map((m) => (
                <MaintenanceCard
                  key={m.task.id}
                  task={m.task}
                  daysUntilDue={m.days_until_due}
                  isDone={m.is_done_today}
                  onComplete={() => handleComplete(m.task.id)}
                />
              ))}
          </div>
        </div>
      )}

      {/* Footer message */}
      <div className="pt-4 pb-2 text-center">
        <p className="text-xs text-ink-400 italic">
          Here''s where you are. What feels doable right now?
        </p>
      </div>
    </div>
  )
}

function TaskSection({
  label, tasks, onComplete, hint,
}: {
  label: string
  tasks: TaskOut[]
  onComplete: (id: number) => void
  hint?: string
}) {
  if (tasks.length === 0) return null

  const allDone = tasks.every(t => t.is_done_today)

  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <h2 className="text-sm font-medium text-plum-500">{label}</h2>
        {hint && !allDone && (
          <span className="text-xs text-ink-400">{hint}</span>
        )}
      </div>
      <div className="space-y-1.5">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} onComplete={() => onComplete(task.id)} />
        ))}
      </div>
      {allDone && (
        <p className="text-xs text-teal-500 italic pl-1">All done. Nice.</p>
      )}
    </div>
  )
}

function TaskCard({
  task, onComplete,
}: {
  task: TaskOut
  onComplete: () => void
}) {
  return (
    <button
      onClick={onComplete}
      disabled={task.is_done_today}
      className={cn(
        'w-full flex items-start gap-3 p-3 rounded-2xl text-left transition-colors',
        task.is_done_today
          ? 'bg-plum-100 opacity-60'
          : 'bg-plum-100 hover:bg-plum-200 active:bg-plum-200'
      )}
    >
      {task.is_done_today ? (
        <CheckCircle2 className="h-5 w-5 text-teal-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      ) : (
        <Circle className="h-5 w-5 text-violet-400 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      )}
      <div className="flex-1 min-w-0">
        <p className={cn(
          'text-sm',
          task.is_done_today ? 'text-ink-400 line-through' : 'text-ink-100'
        )}>
          {task.title}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          {task.zone && (
            <span className="flex items-center gap-0.5 text-[11px] text-ink-400">
              <MapPin className="h-3 w-3" strokeWidth={1.5} />
              {task.zone}
            </span>
          )}
          <span className="flex items-center gap-0.5 text-[11px] text-ink-400">
            <Clock className="h-3 w-3" strokeWidth={1.5} />
            {task.estimated_minutes} min
          </span>
        </div>
      </div>
    </button>
  )
}

function MaintenanceCard({
  task, daysUntilDue, isDone, onComplete,
}: {
  task: TaskOut
  daysUntilDue: number
  isDone: boolean
  onComplete: () => void
}) {
  const dueText = daysUntilDue <= 0
    ? 'Ready when you are'
    : daysUntilDue === 1
    ? 'Tomorrow, maybe'
    : `In ${daysUntilDue} days`

  return (
    <button
      onClick={onComplete}
      disabled={isDone}
      className={cn(
        'w-full flex items-start gap-3 p-3 rounded-2xl text-left transition-colors border',
        isDone
          ? 'bg-plum-100 opacity-60 border-plum-200'
          : daysUntilDue <= 0
          ? 'bg-coral-400/10 border-coral-400/30 hover:bg-coral-400/15'
          : 'bg-plum-100 border-plum-200 hover:bg-plum-200'
      )}
    >
      {isDone ? (
        <CheckCircle2 className="h-5 w-5 text-teal-500 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      ) : (
        <Circle className="h-5 w-5 text-violet-400 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
      )}
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm', isDone ? 'text-ink-400 line-through' : 'text-ink-100')}>
          {task.title}
        </p>
        <span className="text-[11px] text-ink-400">{dueText}</span>
      </div>
    </button>
  )
}
