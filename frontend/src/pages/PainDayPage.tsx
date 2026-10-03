import { useState, useEffect, useCallback } from 'react'
import { Heart, CheckCircle2, Circle, Clock } from 'lucide-react'
import { apiClient, type PainDayTask } from '@/lib/api'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export default function PainDayPage() {
  const [painTask, setPainTask] = useState<PainDayTask | null>(null)
  const [loading, setLoading] = useState(true)
  const [completed, setCompleted] = useState(false)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getPainDayTask()
      setPainTask(res.data)
      setCompleted(false)
    } catch {
      toast.error('Something went wrong. Try again in a moment.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleComplete = async () => {
    if (!painTask?.task) return
    try {
      await apiClient.completeTask(painTask.task.id)
      setCompleted(true)
      toast.success('This is enough.')
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

  return (
    <div className="space-y-8 pt-4">
      {/* Header -- gentle, validating */}
      <div className="text-center space-y-2">
        <Heart className="h-10 w-10 text-coral-400 mx-auto" strokeWidth={1.5} />
        <h1 className="text-2xl font-serif text-ink-100">Pain Day</h1>
        <p className="text-sm text-ink-400 max-w-xs mx-auto">
          One small thing. That''s all. The rest can wait.
        </p>
      </div>

      {completed ? (
        /* After completion -- the "this is enough" message */
        <div className="text-center space-y-4 py-8">
          <CheckCircle2 className="h-16 w-16 text-teal-500 mx-auto" strokeWidth={1} />
          <div className="space-y-2">
            <p className="text-lg font-serif text-ink-100">
              This is enough.
            </p>
            <p className="text-sm text-ink-400 max-w-xs mx-auto">
              You took care of something. The rest can wait.
            </p>
          </div>
          <button
            onClick={load}
            className="text-sm text-teal-500 hover:text-teal-600 underline underline-offset-2"
          >
            If you want one more thing...
          </button>
        </div>
      ) : painTask?.task ? (
        /* The single task */
        <div className="space-y-4">
          <button
            onClick={handleComplete}
            className="w-full flex items-start gap-4 p-5 rounded-2xl text-left bg-plum-100 hover:bg-plum-200 active:bg-plum-200 transition-colors border border-plum-200"
          >
            <Circle className="h-6 w-6 text-violet-400 flex-shrink-0 mt-0.5" strokeWidth={1.5} />
            <div className="flex-1 min-w-0">
              <p className="text-base text-ink-100">{painTask.task.title}</p>
              <div className="flex items-center gap-2 mt-1">
                {painTask.task.zone && (
                  <span className="text-xs text-ink-400">{painTask.task.zone}</span>
                )}
                <span className="flex items-center gap-0.5 text-xs text-ink-400">
                  <Clock className="h-3 w-3" strokeWidth={1.5} />
                  {painTask.task.estimated_minutes} min
                </span>
              </div>
            </div>
          </button>

          <p className="text-center text-sm text-ink-400 italic">
            {painTask.message}
          </p>
        </div>
      ) : (
        /* Everything is done */
        <div className="text-center space-y-4 py-8">
          <CheckCircle2 className="h-16 w-16 text-teal-500 mx-auto" strokeWidth={1} />
          <p className="text-lg font-serif text-ink-100">
            Everything''s been taken care of.
          </p>
          <p className="text-sm text-ink-400 max-w-xs mx-auto">
            Rest is okay too. You''ve done enough.
          </p>
        </div>
      )}
    </div>
  )
}
