import { useState } from 'react'
import { Lock } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

export default function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!password) return
    setLoading(true)
    try {
      const res = await apiClient.login(password)
      localStorage.setItem('ten_token', res.data.token)
      onLogin()
    } catch {
      toast.error('Not quite. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-plum-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 rounded-2xl bg-plum-200 flex items-center justify-center mx-auto">
            <Lock className="h-8 w-8 text-teal-400" strokeWidth={1.5} />
          </div>
          <div>
            <h1 className="text-2xl font-serif text-ink-100">Ten at a Time</h1>
            <p className="text-sm text-ink-400 mt-1">Sign in to continue.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            autoFocus
            className="w-full px-4 py-3 rounded-2xl bg-plum-200 text-ink-100 placeholder-ink-400 border border-plum-300 focus:border-teal-500 focus:outline-none transition-colors"
          />
          <button
            type="submit"
            disabled={loading || !password}
            className="w-full px-4 py-3 rounded-2xl bg-teal-500 text-white font-medium hover:bg-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
