import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export interface TaskOut {
  id: number
  title: string
  description: string
  category: string
  zone: string
  estimated_minutes: number
  pain_day_eligible: boolean
  pain_day_priority: number
  day_of_week: number | null
  week_pattern: string | null
  zone_week: number | null
  month_week: number | null
  frequency_days: number | null
  sort_order: number
  is_active: boolean
  is_done_today: boolean
}

export interface MaintenanceOut {
  task: TaskOut
  last_completed: string | null
  due_date: string | null
  days_until_due: number
  is_due_soon: boolean
  is_done_today: boolean
}

export interface TodaySummary {
  date: string
  daily: TaskOut[]
  weekly: TaskOut[]
  zone: TaskOut[]
  monthly: TaskOut[]
  maintenance: MaintenanceOut[]
  completed_count: number
}

export interface PainDayTask {
  task: TaskOut | null
  message: string
}

export interface SettingsOut {
  pain_day_mode: boolean
  reminder_time_daily: string
  reminder_time_weekly: string
  trash_reminder_enabled: boolean
  trash_reminder_time: string
  user_name: string
}

export interface HistoryEntry {
  task_id: number
  task_title: string
  category: string
  zone: string
  completed_at: string
  completed_by: string
}

export const apiClient = {
  getToday: () => api.get<TodaySummary>('/tasks/today'),
  completeTask: (task_id: number, occurrence_date?: string) =>
    api.post('/tasks/complete', { task_id, occurrence_date }),
  undoCompletion: (completion_id: number) =>
    api.delete(`/tasks/complete/${completion_id}`),
  getPainDayTask: () => api.get<PainDayTask>('/tasks/pain-day'),
  getHistory: (days: number = 30) => api.get<{ entries: HistoryEntry[]; total: number; days: number }>(`/tasks/history?days=${days}`),
  getSettings: () => api.get<SettingsOut>('/settings'),
  updateSettings: (settings: Partial<SettingsOut>) => api.put<SettingsOut>('/settings', settings),
  subscribePush: (endpoint: string, keys: Record<string, string>) =>
    api.post('/push/subscribe', { endpoint, keys }),
  unsubscribePush: (endpoint: string) =>
    api.delete(`/push/subscribe?endpoint=${encodeURIComponent(endpoint)}`),
  testPush: () => api.post('/push/test'),
  healthCheck: () => api.get('/health'),
}
