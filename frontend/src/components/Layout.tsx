import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useStore } from '../store'
import {
  LayoutDashboard, MessageSquare, Settings, List, ShieldCheck, Cpu, Circle,
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/permissions', label: 'Permissions', icon: ShieldCheck },
  { to: '/logs', label: 'Logs', icon: List },
  { to: '/settings', label: 'Settings', icon: Settings },
]

const STATUS_COLOR: Record<string, string> = {
  idle: 'text-gray-500',
  thinking: 'text-yellow-400 animate-pulse',
  acting: 'text-blue-400 animate-pulse',
  waiting_approval: 'text-orange-400 animate-pulse',
  error: 'text-red-400',
}

export default function Layout({ children }: { children: ReactNode }) {
  const { agentStatus, selectedModel } = useStore()

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Cpu className="text-brand-500 w-5 h-5" />
            <span className="font-semibold text-sm">macOS Agent</span>
          </div>
          <div className={clsx('flex items-center gap-1.5 mt-2 text-xs', STATUS_COLOR[agentStatus.status])}>
            <Circle className="w-2 h-2 fill-current" />
            <span className="capitalize">{agentStatus.status}</span>
          </div>
          {agentStatus.current_task && (
            <p className="text-xs text-gray-500 mt-1 truncate">{agentStatus.current_task}</p>
          )}
        </div>

        <nav className="flex-1 p-2 space-y-0.5">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-brand-600/20 text-brand-400'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200',
                )
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-800 text-xs text-gray-600">
          {selectedModel || agentStatus.model || 'No model selected'}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
