import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cpu, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { getHealth, getOllamaModels, pullOllamaModel, completeSetup } from '../api/client'
import { useStore } from '../store'
import clsx from 'clsx'

type Step = 'welcome' | 'model' | 'api_keys' | 'done'

export default function Onboarding() {
  const navigate = useNavigate()
  const { setOnboardingComplete } = useStore()

  const [step, setStep] = useState<Step>('welcome')
  const [ollamaConnected, setOllamaConnected] = useState(false)
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('gemma3:4b')
  const [pulling, setPulling] = useState(false)
  const [openaiKey, setOpenaiKey] = useState('')
  const [anthropicKey, setAnthropicKey] = useState('')
  const [routing, setRouting] = useState<'local_first' | 'local_only' | 'cloud_first'>('local_first')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getHealth()
      .then((h) => {
        setOllamaConnected(h.ollama === 'connected')
      })
      .catch(() => {})

    getOllamaModels()
      .then((models) => setAvailableModels(models.map((m: any) => m.name)))
      .catch(() => {})
  }, [])

  const handlePullModel = async () => {
    setPulling(true)
    try {
      await pullOllamaModel(selectedModel)
      await new Promise((r) => setTimeout(r, 2000))
      const models = await getOllamaModels()
      setAvailableModels(models.map((m: any) => m.name))
    } catch {}
    setPulling(false)
  }

  const handleFinish = async () => {
    setLoading(true)
    try {
      await completeSetup({
        ollama_model: selectedModel,
        openai_api_key: openaiKey || undefined,
        anthropic_api_key: anthropicKey || undefined,
        routing_strategy: routing,
      })
      setOnboardingComplete(true)
      navigate('/')
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const POPULAR_MODELS = ['gemma3:4b', 'gemma3:12b', 'llama3.2:3b', 'mistral:7b', 'qwen2.5:7b']

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">macOS Agent</h1>
            <p className="text-sm text-gray-400">Local-first desktop intelligence</p>
          </div>
        </div>

        {/* Step: Welcome */}
        {step === 'welcome' && (
          <div className="card space-y-5">
            <div>
              <h2 className="text-lg font-semibold mb-2">Welcome</h2>
              <p className="text-gray-400 text-sm leading-relaxed">
                This agent runs locally on your Mac. It uses Ollama to run AI models
                entirely on your device — your data never leaves your machine unless you
                explicitly configure a cloud provider.
              </p>
            </div>

            <div className="flex items-center gap-2">
              {ollamaConnected ? (
                <CheckCircle2 className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-400" />
              )}
              <span className="text-sm">
                Ollama:{' '}
                {ollamaConnected ? (
                  <span className="text-green-400">Connected</span>
                ) : (
                  <span className="text-red-400">
                    Not found — install from{' '}
                    <a href="#" className="underline text-brand-400">ollama.com</a>
                  </span>
                )}
              </span>
            </div>

            {!ollamaConnected && (
              <div className="bg-gray-800 rounded-lg p-3 text-sm font-mono text-gray-300">
                brew install ollama && ollama serve
              </div>
            )}

            <button
              className="btn-primary w-full"
              onClick={() => setStep('model')}
            >
              Get Started
            </button>
          </div>
        )}

        {/* Step: Model */}
        {step === 'model' && (
          <div className="card space-y-5">
            <div>
              <h2 className="text-lg font-semibold mb-1">Choose a Local Model</h2>
              <p className="text-gray-400 text-sm">Gemma 3 4B is recommended for most Macs.</p>
            </div>

            <div className="space-y-2">
              {POPULAR_MODELS.map((m) => {
                const installed = availableModels.includes(m)
                return (
                  <label
                    key={m}
                    className={clsx(
                      'flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors',
                      selectedModel === m
                        ? 'border-brand-500 bg-brand-500/10'
                        : 'border-gray-700 hover:border-gray-600',
                    )}
                  >
                    <input
                      type="radio"
                      name="model"
                      value={m}
                      checked={selectedModel === m}
                      onChange={() => setSelectedModel(m)}
                      className="accent-brand-500"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{m}</p>
                    </div>
                    {installed ? (
                      <span className="badge-green">installed</span>
                    ) : (
                      <span className="badge-gray">not pulled</span>
                    )}
                  </label>
                )
              })}
            </div>

            {!availableModels.includes(selectedModel) && (
              <button
                className="btn-secondary w-full flex items-center justify-center gap-2"
                onClick={handlePullModel}
                disabled={pulling}
              >
                {pulling ? <RefreshCw className="w-4 h-4 animate-spin" /> : null}
                {pulling ? 'Pulling model...' : `Pull ${selectedModel}`}
              </button>
            )}

            <div className="flex gap-3">
              <button className="btn-secondary flex-1" onClick={() => setStep('welcome')}>Back</button>
              <button className="btn-primary flex-1" onClick={() => setStep('api_keys')}>Continue</button>
            </div>
          </div>
        )}

        {/* Step: API Keys */}
        {step === 'api_keys' && (
          <div className="card space-y-5">
            <div>
              <h2 className="text-lg font-semibold mb-1">Cloud API Keys (Optional)</h2>
              <p className="text-gray-400 text-sm">
                Leave blank to use local models only. Keys are stored in your macOS Keychain.
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 font-medium mb-1 block">OpenAI API Key</label>
                <input
                  type="password"
                  className="input"
                  placeholder="sk-..."
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 font-medium mb-1 block">Anthropic API Key</label>
                <input
                  type="password"
                  className="input"
                  placeholder="sk-ant-..."
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs text-gray-400 font-medium mb-1 block">Routing Strategy</label>
                <select
                  className="input"
                  value={routing}
                  onChange={(e) => setRouting(e.target.value as any)}
                >
                  <option value="local_first">Local First (recommended)</option>
                  <option value="local_only">Local Only (max privacy)</option>
                  <option value="cloud_first">Cloud First (max capability)</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3">
              <button className="btn-secondary flex-1" onClick={() => setStep('model')}>Back</button>
              <button
                className="btn-primary flex-1"
                onClick={handleFinish}
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Finish Setup'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
