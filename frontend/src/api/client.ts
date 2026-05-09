import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: BASE,
  timeout: 120000,
})

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface Attachment {
  type: 'image' | 'file' | 'screenshot' | 'text'
  name: string
  content: string
  mime_type?: string
}

export interface ChatRequest {
  message: string
  session_id?: string
  model?: string
  attachments?: Attachment[]
  allow_actions?: boolean
}

export interface ChatResponse {
  session_id: string
  message: string
  model_used: string
  actions_taken: ActionSummary[]
  pending_approvals: PendingApproval[]
  timestamp: string
}

export interface ActionSummary {
  action: string
  parameters: Record<string, unknown>
  success: boolean
  output_summary: string
}

export interface PendingApproval {
  id: string
  action_name: string
  description: string
  parameters: Record<string, unknown>
  risk_level: 'low' | 'medium' | 'high'
  requested_at: string
}

export interface ModelInfo {
  id: string
  name: string
  provider: 'ollama' | 'openai' | 'anthropic'
  available: boolean
  size?: string
  description?: string
}

export interface AgentStatus {
  status: 'idle' | 'thinking' | 'acting' | 'waiting_approval' | 'error'
  current_task?: string
  model?: string
  session_id?: string
}

export interface SystemHealth {
  status: string
  platform: string
  ollama: string
  model_routing: string
  default_model: string
}

// API calls
export const sendChat = (req: ChatRequest) =>
  api.post<ChatResponse>('/api/agent/chat', req).then(r => r.data)

export const getStatus = () =>
  api.get<AgentStatus>('/api/agent/status').then(r => r.data)

export const listModels = () =>
  api.get<ModelInfo[]>('/api/agent/models').then(r => r.data)

export const getHealth = () =>
  api.get<SystemHealth>('/api/system/health').then(r => r.data)

export const getOnboardingStatus = () =>
  api.get<{ complete: boolean }>('/api/settings/onboarding-status').then(r => r.data)

export const completeSetup = (data: {
  ollama_model: string
  openai_api_key?: string
  anthropic_api_key?: string
  routing_strategy: string
}) => api.post('/api/settings/setup', data).then(r => r.data)

export const getSettings = () =>
  api.get('/api/settings/').then(r => r.data)

export const listActions = () =>
  api.get('/api/actions/list').then(r => r.data)

export const getPendingApprovals = () =>
  api.get<PendingApproval[]>('/api/actions/approvals').then(r => r.data)

export const approveAction = (approval_id: string, approved: boolean) =>
  api.post('/api/actions/approve', { approval_id, approved }).then(r => r.data)

export const getActionLogs = (limit = 50) =>
  api.get(`/api/logs/actions?limit=${limit}`).then(r => r.data)

export const getOllamaModels = () =>
  api.get('/api/system/ollama/models').then(r => r.data)

export const pullOllamaModel = (model_name: string) =>
  api.post(`/api/system/ollama/pull?model_name=${encodeURIComponent(model_name)}`).then(r => r.data)

export const uploadImage = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<{ attachment: Attachment }>('/api/agent/upload-image', form).then(r => r.data)
}

export const uploadFile = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<{ attachment: Attachment }>('/api/agent/upload-file', form).then(r => r.data)
}
