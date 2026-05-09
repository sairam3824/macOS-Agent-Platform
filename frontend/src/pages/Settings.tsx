import { useState, useEffect } from 'react'
import { getSettings, getOllamaModels, pullOllamaModel } from '../api/client'
import { api } from '../api/client'
import { RefreshCw, Save, Download } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>(null)
  const [ollamaModels, setOllamaModels] = useState<any[]>([])
  const [pulling, setPulling] = useState<string | null>(null)

  const [safeMode, setSafeMode] = useState(false)
  const [dryRun, setDryRun] = useState(false)
  const [requireConfirm, setRequireConfirm] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getSettings().then((s) => {
      setSettings(s)
      if (s.safety) {
        setSafeMode(s.safety.safe_mode ?? false)
        setDryRun(s.safety.dry_run_mode ?? false)
        setRequireConfirm(s.safety.require_confirmation ?? true)
      }
    }).catch(() => {})

    getOllamaModels().then(setOllamaModels).catch(() => {})
  }, [])

  const handleSaveSafety = async () => {
    setSaving(true)
    try {
      await api.put(
        `/api/settings/safety?require_confirmation=${requireConfirm}&dry_run=${dryRun}&safe_mode=${safeMode}`
      )
    } catch {}
    setSaving(false)
  }

  const handlePull = async (model: string) => {
    setPulling(model)
    await pullOllamaModel(model).catch(() => {})
    setTimeout(() => {
      getOllamaModels().then(setOllamaModels).catch(() => {})
      setPulling(null)
    }, 3000)
  }

  const RECOMMENDED = ['gemma3:4b', 'gemma3:12b', 'llava:7b', 'mistral:7b', 'qwen2.5:7b']

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* Safety */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-gray-300">Safety & Permissions</h2>

        <label className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Require Confirmation</p>
            <p className="text-xs text-gray-500">Ask before medium/high risk actions</p>
          </div>
          <input
            type="checkbox"
            checked={requireConfirm}
            onChange={(e) => setRequireConfirm(e.target.checked)}
            className="accent-brand-500 w-4 h-4"
          />
        </label>

        <label className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Dry Run Mode</p>
            <p className="text-xs text-gray-500">Simulate actions without executing them</p>
          </div>
          <input
            type="checkbox"
            checked={dryRun}
            onChange={(e) => setDryRun(e.target.checked)}
            className="accent-brand-500 w-4 h-4"
          />
        </label>

        <label className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Safe Mode</p>
            <p className="text-xs text-gray-500">Analyze only — no actions taken</p>
          </div>
          <input
            type="checkbox"
            checked={safeMode}
            onChange={(e) => setSafeMode(e.target.checked)}
            className="accent-brand-500 w-4 h-4"
          />
        </label>

        <button className="btn-primary flex items-center gap-2" onClick={handleSaveSafety} disabled={saving}>
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Safety Settings'}
        </button>
      </div>

      {/* Ollama models */}
      <div className="card space-y-4">
        <h2 className="text-sm font-semibold text-gray-300">Ollama Models</h2>

        {ollamaModels.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-2">Installed</p>
            <div className="space-y-1">
              {ollamaModels.map((m: any) => (
                <div key={m.name} className="flex items-center gap-2 text-sm">
                  <span className="badge-green">installed</span>
                  <span className="font-mono">{m.name}</span>
                  {m.size && (
                    <span className="text-gray-500 text-xs">
                      {(m.size / 1e9).toFixed(1)} GB
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs text-gray-500 mb-2">Pull a model</p>
          <div className="space-y-1.5">
            {RECOMMENDED.filter((m) => !ollamaModels.find((om: any) => om.name === m)).map((m) => (
              <div key={m} className="flex items-center gap-2">
                <code className="text-sm text-brand-400 flex-1">{m}</code>
                <button
                  className="btn-secondary text-xs flex items-center gap-1"
                  onClick={() => handlePull(m)}
                  disabled={pulling === m}
                >
                  {pulling === m ? (
                    <RefreshCw className="w-3 h-3 animate-spin" />
                  ) : (
                    <Download className="w-3 h-3" />
                  )}
                  {pulling === m ? 'Pulling...' : 'Pull'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Provider status */}
      {settings?.providers && (
        <div className="card space-y-3">
          <h2 className="text-sm font-semibold text-gray-300">Configured Providers</h2>
          {settings.providers.map((p: any) => (
            <div key={p.provider} className="flex items-center gap-3 text-sm">
              <span className={p.enabled ? 'badge-green' : 'badge-gray'}>
                {p.enabled ? 'active' : 'disabled'}
              </span>
              <span className="capitalize font-medium">{p.provider}</span>
              {p.api_key && <span className="text-gray-500 font-mono text-xs">{p.api_key}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
