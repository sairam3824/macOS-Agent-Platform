import { useState, useRef, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useStore } from '../store'
import { sendChat, api } from '../api/client'
import ChatMessage from '../components/ChatMessage'
import ModelSelector from '../components/ModelSelector'
import FileDropzone from '../components/FileDropzone'
import PermissionModal from '../components/PermissionModal'
import { Send, Square, Paperclip, Mic, MicOff, Circle } from 'lucide-react'
import clsx from 'clsx'

export default function Chat() {
  const [searchParams] = useSearchParams()
  const {
    messages, addMessage, selectedModel, setAgentStatus,
    pendingApprovals, addPendingApproval, stagedAttachments, clearAttachments, sessionId,
  } = useStore()

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showDropzone, setShowDropzone] = useState(false)
  const [voiceState, setVoiceState] = useState<'idle' | 'recording' | 'processing'>('idle')
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Handle quick-action prompt from URL
  useEffect(() => {
    const prompt = searchParams.get('prompt')
    if (prompt) {
      setInput(prompt)
      inputRef.current?.focus()
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMsg = {
      id: `${Date.now()}-user`,
      role: 'user' as const,
      content: input,
      timestamp: new Date(),
      attachments: stagedAttachments,
    }
    addMessage(userMsg)
    const userInput = input
    setInput('')
    clearAttachments()
    setLoading(true)
    setAgentStatus({ status: 'thinking' })

    try {
      const resp = await sendChat({
        message: userInput,
        session_id: sessionId,
        model: selectedModel || undefined,
        attachments: userMsg.attachments,
        allow_actions: true,
      })

      const assistantMsg = {
        id: `${Date.now()}-assistant`,
        role: 'assistant' as const,
        content: resp.message,
        timestamp: new Date(),
        model: resp.model_used,
        actions: resp.actions_taken,
      }
      addMessage(assistantMsg)

      for (const approval of resp.pending_approvals) {
        addPendingApproval(approval)
      }

      setAgentStatus({ status: 'idle', model: resp.model_used })
    } catch (err) {
      addMessage({
        id: `${Date.now()}-err`,
        role: 'assistant',
        content: 'Error connecting to agent backend. Make sure the server is running.',
        timestamp: new Date(),
      })
      setAgentStatus({ status: 'error' })
    }

    setLoading(false)
  }

  const startVoiceRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        setVoiceState('processing')

        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        const form = new FormData()
        form.append('file', blob, 'recording.webm')
        form.append('session_id', sessionId)

        try {
          const resp = await api.post('/api/voice/transcribe-and-chat', form, { timeout: 90000 })
          const data = resp.data
          const transcribed = data.transcription || ''
          const response = data.response

          if (transcribed) {
            addMessage({
              id: `${Date.now()}-user`,
              role: 'user',
              content: `🎤 ${transcribed}`,
              timestamp: new Date(),
            })
          }

          if (response) {
            addMessage({
              id: `${Date.now()}-assistant`,
              role: 'assistant',
              content: response.message,
              timestamp: new Date(),
              model: response.model_used,
              actions: response.actions_taken,
            })
            setAgentStatus({ status: 'idle', model: response.model_used })
          }
        } catch {
          addMessage({
            id: `${Date.now()}-err`,
            role: 'assistant',
            content: 'Voice processing failed. Check that the backend is running and Whisper is installed.',
            timestamp: new Date(),
          })
        }

        setVoiceState('idle')
      }

      recorder.start()
      setVoiceState('recording')
    } catch {
      alert('Microphone access denied. Allow microphone in browser settings.')
    }
  }, [sessionId, addMessage, setAgentStatus])

  const stopVoiceRecording = useCallback(() => {
    if (mediaRecorderRef.current && voiceState === 'recording') {
      mediaRecorderRef.current.stop()
    }
  }, [voiceState])

  const toggleVoice = () => {
    if (voiceState === 'recording') {
      stopVoiceRecording()
    } else if (voiceState === 'idle') {
      startVoiceRecording()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {pendingApprovals.map((a) => (
        <PermissionModal key={a.id} approval={a} />
      ))}

      {/* Header */}
      <div className="border-b border-gray-800 px-4 py-3 flex items-center gap-4">
        <h1 className="text-sm font-semibold text-gray-300">Chat</h1>
        <div className="flex-1 max-w-xs">
          <ModelSelector compact />
        </div>
        {loading && (
          <span className="text-xs text-yellow-400 animate-pulse">Agent thinking...</span>
        )}
        {voiceState === 'recording' && (
          <span className="flex items-center gap-1.5 text-xs text-red-400 animate-pulse">
            <Circle className="w-2 h-2 fill-current" /> Recording — press mic button or stop speaking to finish
          </span>
        )}
        {voiceState === 'processing' && (
          <span className="text-xs text-yellow-400 animate-pulse">Transcribing voice...</span>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-2">
            <p className="text-lg font-medium text-gray-400">What can I help you with?</p>
            <p className="text-sm">Try: "Summarize selected text" · "Take a screenshot" · "Check recent emails"</p>
          </div>
        )}
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            role={m.role}
            content={m.content}
            timestamp={m.timestamp}
            model={m.model}
            actions={m.actions}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-800 p-4 space-y-3">
        {showDropzone && <FileDropzone />}

        <div className="flex items-end gap-2">
          <button
            onClick={() => setShowDropzone((v) => !v)}
            className={clsx(
              'p-2 rounded-lg transition-colors',
              showDropzone ? 'text-brand-400 bg-brand-500/10' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800',
            )}
          >
            <Paperclip className="w-4 h-4" />
          </button>

          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message the agent..."
              className="input resize-none min-h-[42px] max-h-[200px] pr-10 py-2.5 leading-relaxed"
              style={{ height: 'auto' }}
              onInput={(e) => {
                const t = e.currentTarget
                t.style.height = 'auto'
                t.style.height = `${Math.min(t.scrollHeight, 200)}px`
              }}
            />
          </div>

          <button
            onClick={toggleVoice}
            disabled={loading || voiceState === 'processing'}
            title={voiceState === 'recording' ? 'Stop recording' : 'Start voice input'}
            className={clsx(
              'p-2.5 rounded-lg transition-colors',
              voiceState === 'recording'
                ? 'bg-red-600 hover:bg-red-500 text-white animate-pulse'
                : voiceState === 'processing'
                ? 'bg-yellow-700 text-white'
                : 'bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white',
            )}
          >
            {voiceState === 'recording' ? (
              <Circle className="w-4 h-4 fill-current" />
            ) : voiceState === 'processing' ? (
              <MicOff className="w-4 h-4 animate-spin" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="btn-primary p-2.5"
          >
            {loading ? (
              <Square className="w-4 h-4" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>

        {stagedAttachments.length > 0 && (
          <p className="text-xs text-gray-500">
            {stagedAttachments.length} attachment{stagedAttachments.length > 1 ? 's' : ''} staged
          </p>
        )}
      </div>
    </div>
  )
}
