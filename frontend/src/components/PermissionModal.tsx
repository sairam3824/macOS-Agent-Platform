import { PendingApproval, approveAction } from '../api/client'
import { useStore } from '../store'
import { ShieldAlert, ShieldCheck, ShieldX, X } from 'lucide-react'
import clsx from 'clsx'

const RISK_ICON = {
  low: <ShieldCheck className="w-5 h-5 text-green-400" />,
  medium: <ShieldAlert className="w-5 h-5 text-yellow-400" />,
  high: <ShieldX className="w-5 h-5 text-red-400" />,
}

const RISK_LABEL = {
  low: 'badge-green',
  medium: 'badge-yellow',
  high: 'badge-red',
}

interface Props {
  approval: PendingApproval
}

export default function PermissionModal({ approval }: Props) {
  const { removePendingApproval } = useStore()

  const handle = async (approved: boolean) => {
    try {
      await approveAction(approval.id, approved)
    } catch {}
    removePendingApproval(approval.id)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="card max-w-md w-full mx-4 shadow-2xl">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2">
            {RISK_ICON[approval.risk_level]}
            <h2 className="font-semibold">Action Approval Required</h2>
          </div>
          <button onClick={() => handle(false)} className="text-gray-500 hover:text-gray-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 mb-5">
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">Action:</span>
            <code className="text-sm bg-gray-800 px-2 py-0.5 rounded text-brand-400">
              {approval.action_name}
            </code>
            <span className={clsx(RISK_LABEL[approval.risk_level])}>
              {approval.risk_level} risk
            </span>
          </div>

          <p className="text-sm text-gray-300">{approval.description}</p>

          {Object.keys(approval.parameters).length > 0 && (
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Parameters</p>
              <pre className="text-xs text-gray-300 overflow-auto max-h-32">
                {JSON.stringify(approval.parameters, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <button className="btn-danger flex-1" onClick={() => handle(false)}>
            Deny
          </button>
          <button className="btn-primary flex-1" onClick={() => handle(true)}>
            Approve
          </button>
        </div>
      </div>
    </div>
  )
}
