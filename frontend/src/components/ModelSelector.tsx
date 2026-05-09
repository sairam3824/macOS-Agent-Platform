import { useStore } from '../store'
import { ModelInfo } from '../api/client'
import clsx from 'clsx'

const PROVIDER_COLORS = {
  ollama: 'badge-green',
  openai: 'badge-blue',
  anthropic: 'badge-yellow',
}

interface Props {
  compact?: boolean
}

export default function ModelSelector({ compact }: Props) {
  const { models, selectedModel, setSelectedModel } = useStore()

  return (
    <div className={clsx('space-y-1', compact ? '' : 'w-full')}>
      {!compact && (
        <label className="text-xs text-gray-400 font-medium">Model</label>
      )}
      <select
        value={selectedModel || ''}
        onChange={(e) => setSelectedModel(e.target.value || null)}
        className="input text-sm"
      >
        <option value="">Auto (use routing strategy)</option>
        {models.map((m: ModelInfo) => (
          <option key={m.id} value={m.id} disabled={!m.available}>
            {m.name} [{m.provider}]{m.available ? '' : ' (unavailable)'}
          </option>
        ))}
      </select>
    </div>
  )
}
