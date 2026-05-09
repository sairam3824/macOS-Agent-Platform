import { useState, useEffect } from 'react'
import { getPendingApprovals } from '../api/client'
import { useStore } from '../store'
import PermissionModal from '../components/PermissionModal'
import { ShieldCheck, ShieldX, Info } from 'lucide-react'

const MACOS_PERMS = [
  {
    id: 'screen',
    label: 'Screen Recording',
    description: 'Allows taking screenshots and inspecting the screen',
    how: 'System Settings → Privacy & Security → Screen Recording → Enable for Terminal/Python',
    required_for: ['capture_screen'],
  },
  {
    id: 'accessibility',
    label: 'Accessibility',
    description: 'Required for automated UI control and key simulation',
    how: 'System Settings → Privacy & Security → Accessibility → Enable for Terminal/Python',
    required_for: ['get_selected_text', 'ui_click'],
  },
  {
    id: 'automation',
    label: 'Automation',
    description: 'Allows controlling other apps via AppleScript',
    how: 'Granted automatically on first AppleScript use — approve the dialog',
    required_for: ['open_app', 'draft_email', 'get_recent_emails'],
  },
  {
    id: 'full_disk',
    label: 'Full Disk Access (optional)',
    description: 'Allows reading files in protected directories',
    how: 'System Settings → Privacy & Security → Full Disk Access → Enable for Terminal',
    required_for: ['open_file (protected dirs)'],
  },
]

export default function PermissionsPage() {
  const { pendingApprovals, setPendingApprovals } = useStore()

  useEffect(() => {
    getPendingApprovals().then(setPendingApprovals).catch(() => {})
  }, [])

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      {pendingApprovals.map((a) => (
        <PermissionModal key={a.id} approval={a} />
      ))}

      <h1 className="text-2xl font-bold">Permissions & Safety</h1>

      {/* Pending approvals */}
      {pendingApprovals.length > 0 ? (
        <div className="card border-orange-800 space-y-2">
          <p className="text-sm font-semibold text-orange-400">
            {pendingApprovals.length} Action{pendingApprovals.length > 1 ? 's' : ''} Awaiting Approval
          </p>
          {pendingApprovals.map((a) => (
            <div key={a.id} className="text-sm text-gray-300">
              <code className="text-brand-400">{a.action_name}</code> — {a.description}
            </div>
          ))}
        </div>
      ) : (
        <div className="card flex items-center gap-2 text-green-400">
          <ShieldCheck className="w-4 h-4" />
          <p className="text-sm">No pending approvals</p>
        </div>
      )}

      {/* macOS permissions guide */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-gray-300">macOS System Permissions</h2>
        <p className="text-xs text-gray-500">
          Some capabilities require macOS system permissions. Grant them when prompted, or manually via System Settings.
        </p>

        <div className="space-y-3">
          {MACOS_PERMS.map((p) => (
            <div key={p.id} className="border border-gray-800 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-brand-400" />
                <span className="text-sm font-medium">{p.label}</span>
              </div>
              <p className="text-xs text-gray-400">{p.description}</p>
              <div className="bg-gray-800 rounded-lg p-2 text-xs text-gray-300 font-mono">
                {p.how}
              </div>
              <div className="flex flex-wrap gap-1">
                {p.required_for.map((r) => (
                  <span key={r} className="badge-blue">{r}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk level legend */}
      <div className="card space-y-2">
        <h2 className="text-sm font-semibold text-gray-300">Action Risk Levels</h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="badge-green">low</span>
            <span className="text-gray-400">Read-only, no side effects. Never requires approval.</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-yellow">medium</span>
            <span className="text-gray-400">Minor changes, reversible. Requires approval once per session.</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-red">high</span>
            <span className="text-gray-400">Destructive or irreversible. Always requires explicit approval.</span>
          </div>
        </div>
      </div>
    </div>
  )
}
