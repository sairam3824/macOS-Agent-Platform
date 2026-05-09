import { useState, useEffect } from 'react'
import { getActionLogs } from '../api/client'
import { api } from '../api/client'
import { format } from 'date-fns'
import { CheckCircle2, XCircle, Clock, Trash2 } from 'lucide-react'
import clsx from 'clsx'

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const loadLogs = async () => {
    setLoading(true)
    try {
      const data = await getActionLogs(100)
      setLogs(data)
    } catch {}
    setLoading(false)
  }

  useEffect(() => { loadLogs() }, [])

  const handleClear = async () => {
    if (!confirm('Clear all logs?')) return
    await api.delete('/api/logs/clear').catch(() => {})
    setLogs([])
  }

  const STATUS_ICON: Record<string, React.ReactNode> = {
    completed: <CheckCircle2 className="w-4 h-4 text-green-400" />,
    failed: <XCircle className="w-4 h-4 text-red-400" />,
    pending: <Clock className="w-4 h-4 text-yellow-400" />,
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Action Logs</h1>
        <button
          className="btn-danger flex items-center gap-2 text-sm"
          onClick={handleClear}
        >
          <Trash2 className="w-4 h-4" />
          Clear
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading...</p>
      ) : logs.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">
          <p>No actions logged yet.</p>
          <p className="text-xs mt-1">Actions taken by the agent will appear here.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {logs.map((log) => (
            <div key={log.id} className="card flex items-start gap-3">
              <div className="mt-0.5">{STATUS_ICON[log.status] || STATUS_ICON.pending}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <code className="text-sm text-brand-400">{log.action_type}</code>
                  {log.dry_run && <span className="badge-gray">dry run</span>}
                  {log.approved && <span className="badge-green">approved</span>}
                </div>
                <p className="text-sm text-gray-300 mt-0.5">{log.description}</p>
                {log.result && (
                  <p className="text-xs text-gray-500 mt-1 font-mono truncate">{log.result}</p>
                )}
              </div>
              <time className="text-xs text-gray-600 flex-shrink-0">
                {format(new Date(log.timestamp), 'MM/dd HH:mm:ss')}
              </time>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
