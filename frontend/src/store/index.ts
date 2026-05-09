import { create } from 'zustand'
import type { ModelInfo, AgentStatus, PendingApproval, Attachment } from '../api/client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: string
  actions?: { action: string; success: boolean; output_summary: string }[]
  attachments?: Attachment[]
}

interface AppStore {
  // Agent state
  agentStatus: AgentStatus
  setAgentStatus: (s: AgentStatus) => void

  // Models
  models: ModelInfo[]
  setModels: (m: ModelInfo[]) => void
  selectedModel: string | null
  setSelectedModel: (m: string | null) => void

  // Chat
  messages: Message[]
  addMessage: (m: Message) => void
  clearMessages: () => void
  sessionId: string

  // Approvals
  pendingApprovals: PendingApproval[]
  setPendingApprovals: (a: PendingApproval[]) => void
  addPendingApproval: (a: PendingApproval) => void
  removePendingApproval: (id: string) => void

  // Attachments (staged for next message)
  stagedAttachments: Attachment[]
  addAttachment: (a: Attachment) => void
  removeAttachment: (name: string) => void
  clearAttachments: () => void

  // Settings
  onboardingComplete: boolean
  setOnboardingComplete: (v: boolean) => void
}

export const useStore = create<AppStore>((set, get) => ({
  agentStatus: { status: 'idle' },
  setAgentStatus: (s) => set({ agentStatus: s }),

  models: [],
  setModels: (m) => set({ models: m }),
  selectedModel: null,
  setSelectedModel: (m) => set({ selectedModel: m }),

  messages: [],
  addMessage: (m) => set((state) => ({ messages: [...state.messages, m] })),
  clearMessages: () => set({ messages: [] }),
  sessionId: `session-${Date.now()}`,

  pendingApprovals: [],
  setPendingApprovals: (a) => set({ pendingApprovals: a }),
  addPendingApproval: (a) =>
    set((state) => ({ pendingApprovals: [...state.pendingApprovals, a] })),
  removePendingApproval: (id) =>
    set((state) => ({
      pendingApprovals: state.pendingApprovals.filter((p) => p.id !== id),
    })),

  stagedAttachments: [],
  addAttachment: (a) =>
    set((state) => ({ stagedAttachments: [...state.stagedAttachments, a] })),
  removeAttachment: (name) =>
    set((state) => ({
      stagedAttachments: state.stagedAttachments.filter((a) => a.name !== name),
    })),
  clearAttachments: () => set({ stagedAttachments: [] }),

  onboardingComplete: false,
  setOnboardingComplete: (v) => set({ onboardingComplete: v }),
}))
