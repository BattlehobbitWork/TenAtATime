import { useState, useEffect, useCallback } from 'react'
import { Bell, BellOff, Clock } from 'lucide-react'
import { apiClient, type SettingsOut } from '@/lib/api'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsOut | null>(null)
  const [loading, setLoading] = useState(true)
  const [pushSupported, setPushSupported] = useState(false)
  const [pushSubscribed, setPushSubscribed] = useState(false)

  const load = useCallback(async () => {
    try {
      const res = await apiClient.getSettings()
      setSettings(res.data)
      setPushSupported('Notification' in window && 'serviceWorker' in navigator)
    } catch {
      toast.error('Could not load settings.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const update = async (partial: Partial<SettingsOut>) => {
    try {
      const res = await apiClient.updateSettings(partial)
      setSettings(res.data)
    } catch {
      toast.error('Could not save settings.')
    }
  }

  const handlePushToggle = async () => {
    if (!pushSupported) return
    try {
      if (pushSubscribed) {
        const reg = await navigator.serviceWorker.ready
        const sub = await reg.pushManager.getSubscription()
        if (sub) {
          await sub.unsubscribe()
          await apiClient.unsubscribePush(sub.endpoint)
        }
        setPushSubscribed(false)
        toast.success('Reminders off.')
      } else {
        const reg = await navigator.serviceWorker.ready
        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
        })
        await apiClient.subscribePush(sub.endpoint, sub.toJSON().keys as Record<string, string>)
        setPushSubscribed(true)
        toast.success('Reminders on.')
      }
    } catch {
      toast.error('Could not change reminders.')
    }
  }

  if (loading) return <div className="flex items-center justify-center py-20"><p className="text-warm-400 text-sm">Loading...</p></div>
  if (!settings) return null

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="text-2xl font-serif text-warm-700">Settings</h1>
        <p className="text-sm text-warm-400 mt-1">Make it yours.</p>
      </div>

      {/* Pain Day Mode */}
      <Section label="Pain Day Mode">
        <div className="flex items-center justify-between p-3 rounded-2xl bg-cream-100">
          <div>
            <p className="text-sm text-warm-700">Pain day mode</p>
            <p className="text-xs text-warm-400">Shows just one thing at a time</p>
          </div>
          <Toggle
            checked={settings.pain_day_mode}
            onChange={(v) => update({ pain_day_mode: v })}
          />
        </div>
      </Section>

      {/* Reminders */}
      <Section label="Reminders">
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 rounded-2xl bg-cream-100">
            <div>
              <p className="text-sm text-warm-700">Daily reminder</p>
              <p className="text-xs text-warm-400">Gentle nudge each morning</p>
            </div>
            <input
              type="time"
              value={settings.reminder_time_daily}
              onChange={(e) => update({ reminder_time_daily: e.target.value })}
              className="bg-cream-200 text-warm-700 rounded-lg px-2 py-1 text-sm border-0 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-2xl bg-cream-100">
            <div>
              <p className="text-sm text-warm-700">Trash reminder</p>
              <p className="text-xs text-warm-400">Wednesday evening, before pickup</p>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="time"
                value={settings.trash_reminder_time}
                onChange={(e) => update({ trash_reminder_time: e.target.value })}
                className="bg-cream-200 text-warm-700 rounded-lg px-2 py-1 text-sm border-0 focus:outline-none"
              />
              <Toggle
                checked={settings.trash_reminder_enabled}
                onChange={(v) => update({ trash_reminder_enabled: v })}
              />
            </div>
          </div>

          {/* Push notification toggle */}
          {pushSupported && (
            <button
              onClick={handlePushToggle}
              className="w-full flex items-center justify-between p-3 rounded-2xl bg-cream-100 hover:bg-cream-200 transition-colors"
            >
              <div className="flex items-center gap-2">
                {pushSubscribed ? (
                  <Bell className="h-5 w-5 text-sage-500" strokeWidth={1.5} />
                ) : (
                  <BellOff className="h-5 w-5 text-warm-400" strokeWidth={1.5} />
                )}
                <div className="text-left">
                  <p className="text-sm text-warm-700">Push notifications</p>
                  <p className="text-xs text-warm-400">
                    {pushSubscribed ? 'On -- gentle reminders' : 'Off'}
                  </p>
                </div>
              </div>
            </button>
          )}
        </div>
      </Section>

      {/* Your name */}
      <Section label="About You">
        <div className="flex items-center justify-between p-3 rounded-2xl bg-cream-100">
          <p className="text-sm text-warm-700">Your name</p>
          <input
            type="text"
            value={settings.user_name}
            onChange={(e) => update({ user_name: e.target.value })}
            className="bg-cream-200 text-warm-700 rounded-lg px-2 py-1 text-sm border-0 focus:outline-none w-32 text-right"
          />
        </div>
      </Section>

      <p className="text-xs text-warm-400 italic text-center pt-2">
        Ten at a Time -- a home management partner, not a taskmaster.
      </p>
    </div>
  )
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <h2 className="text-sm font-medium text-warm-500">{label}</h2>
      {children}
    </div>
  )
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={cn(
        'relative w-11 h-6 rounded-full transition-colors',
        checked ? 'bg-sage-500' : 'bg-warm-300'
      )}
    >
      <span
        className={cn(
          'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform',
          checked && 'translate-x-5'
        )}
      />
    </button>
  )
}
