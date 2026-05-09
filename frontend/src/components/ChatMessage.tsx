import ReactMarkdown from 'react-markdown'
import { format } from 'date-fns'
import { Bot, User, CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

interface Action {
  action: string
  success: boolean
  output_summary: string
}

interface Props {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: string
  actions?: Action[]
}

export default function ChatMessage({ role, content, timestamp, model, actions }: Props) {
  const [showActions, setShowActions] = useState(false)
  const isUser = role === 'user'

  return (
    <div className={clsx('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div
        className={clsx(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1',
          isUser ? 'bg-brand-600' : 'bg-gray-700',
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className={clsx('max-w-[75%] space-y-1', isUser ? 'items-end' : 'items-start')}>
        <div
          className={clsx(
            'rounded-2xl px-4 py-3 text-sm',
            isUser
              ? 'bg-brand-600 text-white rounded-tr-sm'
              : 'bg-gray-800 text-gray-100 rounded-tl-sm',
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
        </div>

        {actions && actions.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setShowActions(!showActions)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              {showActions ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {actions.length} action{actions.length > 1 ? 's' : ''} taken
            </button>

            {showActions && (
              <div className="mt-1 space-y-1">
                {actions.map((a, i) => (
                  <div key={i} className="flex items-start gap-2 bg-gray-900 rounded-lg px-3 py-2 text-xs">
                    {a.success ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <code className="text-brand-400">{a.action}</code>
                      <p className="text-gray-500 mt-0.5">{a.output_summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <p className="text-xs text-gray-600 px-1">
          {format(timestamp, 'HH:mm')}
          {model && !isUser && ` · ${model}`}
        </p>
      </div>
    </div>
  )
}
