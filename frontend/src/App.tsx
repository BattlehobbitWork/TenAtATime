import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { Home, Heart, MapPin, Wrench, Settings, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import TodayPage from '@/pages/TodayPage'
import PainDayPage from '@/pages/PainDayPage'
import ZonePage from '@/pages/ZonePage'
import MaintenancePage from '@/pages/MaintenancePage'
import HistoryPage from '@/pages/HistoryPage'
import SettingsPage from '@/pages/SettingsPage'

const navItems = [
  { to: '/', icon: Home, label: 'Today' },
  { to: '/pain-day', icon: Heart, label: 'Pain Day' },
  { to: '/zones', icon: MapPin, label: 'Zones' },
  { to: '/maintenance', icon: Wrench, label: 'Care' },
  { to: '/history', icon: Clock, label: 'History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-cream-50 flex flex-col">
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 pb-24 pt-6 safe-top">
        <Routes>
          <Route path="/" element={<TodayPage />} />
          <Route path="/pain-day" element={<PainDayPage />} />
          <Route path="/zones" element={<ZonePage />} />
          <Route path="/maintenance" element={<MaintenancePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>

      {/* Bottom nav -- calm, not flashy */}
      <nav className="fixed bottom-0 left-0 right-0 bg-cream-100/95 backdrop-blur-sm border-t border-cream-200 safe-bottom z-50">
        <div className="max-w-2xl mx-auto flex justify-around items-center px-2 py-2">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors',
                  isActive
                    ? 'text-sage-600'
                    : 'text-warm-400 hover:text-warm-600'
                )
              }
            >
              <Icon className="h-5 w-5" strokeWidth={1.5} />
              <span className="text-[10px] font-medium">{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
