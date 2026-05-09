import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useStore } from '../store'
import { getHealth, getActionLogs, getPendingApprovals, SystemHealth } from '../api/client'
import {
  MessageSquare, ShieldCheck, List, Cpu, Wifi, WifiOff,
  CheckCircle2, Clock, AlertTriangle,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import PermissionModal from '../components/PermissionModal'
import clsx from 'clsx'

const QUICK_ACTIONS = [
  { label: 'Summarize selected text', prompt: 'Summarize the text I currently have selected' },
  { label: 'Capture & describe screen', prompt: 'Take a screenshot and describe what you see' },
  { label: 'Latest downloads', prompt: 'Show me my most recently downloaded files' },
  { label: 'Check recent emails', prompt: 'Read my recent emails and summarize them' },
  { label: 'Frontmost app', prompt: 'What app am I currently using?' },
]

export default function Dashboard() {
  const { agentStatus, pendingApprovals, setPendingApprovals } = useStore()
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [logs, setLogs] = useState<any[]>([])

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {})
    getActionLogs(10).then(setLogs).catch(() => {})
    getPendingApprovals().then(setPendingApprovals).catch(() => {})
  }, [])

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {pendingApprovals.map((a) => (
        <PermissionModal key={a.id} approval={a} />
      ))}

      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-400 text-sm mt-0.5">macOS Agent Platform</p>
      </div>

      {/* System status cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            {health?.ollama === 'connected' ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-400" />
            )}
            <span className="text-sm font-medium">Ollama</span>
          </div>
          <p className={clsx('text-xs', health?.ollama === 'connected' ? 'text-green-400' : 'text-red-400')}>
            {health?.ollama || 'checking...'}
          </p>
          <p className="text-xs text-gray-500 mt-1">{health?.default_model}</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Cpu className="w-4 h-4 text-brand-400" />
            <span className="text-sm font-medium">Agent</span>
          </div>
          <p className="text-xs text-brand-400 capitalize">{agentStatus.status}</p>
          {agentStatus.current_task && (
            <p className="text-xs text-gray-500 mt-1 truncate">{agentStatus.current_task}</p>
          )}
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-medium">Routing</span>
          </div>
          <p className="text-xs text-yellow-400 capitalize">{health?.model_routing?.replace(/_/g, ' ')}</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card">
        <h2 className="text-sm font-semibold mb-3 text-gray-300">Quick Actions</h2>
        <div className="space-y-1.5">
          {QUICK_ACTIONS.map((qa) => (
            <Link
              key={qa.label}
              to={`/chat?prompt=${encodeURIComponent(qa.prompt)}`}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors text-sm text-gray-300 hover:text-white"
            >
              <MessageSquare className="w-3.5 h-3.5 text-brand-400" />
              {qa.label}
            </Link>
          ))}
        </div>
      </div>

      {/* Recent action log */}
      {logs.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-300">Recent Actions</h2>
            <Link to="/logs" className="text-xs text-brand-400 hover:underline">View all</Link>
          </div>
          <div className="space-y-1.5">
            {logs.slice(0, 5).map((log: any) => (
              <div key={log.id} className="flex items-center gap-3 text-xs text-gray-400">
                {log.status === 'completed' ? (
                  <CheckCircle2 className="w-3 h-3 text-green-400 flex-shrink-0" />
                ) : log.status === 'pending' ? (
                  <Clock className="w-3 h-3 text-yellow-400 flex-shrink-0" />
                ) : (
                  <AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0" />
                )}
                <span className="font-mono text-brand-400">{log.action_type}</span>
                <span className="flex-1 truncate">{log.description}</span>
                <span className="text-gray-600">
                  {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {pendingApprovals.length > 0 && (
        <div className="card border-orange-800">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <h2 className="text-sm font-semibold text-orange-400">
              {pendingApprovals.length} Pending Approval{pendingApprovals.length > 1 ? 's' : ''}
            </h2>
          </div>
          <p className="text-sm text-gray-400">
            The agent is waiting for you to approve an action before continuing.
          </p>
        </div>
      )}
    </div>
  )
}
