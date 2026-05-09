import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image, FileText } from 'lucide-react'
import { useStore } from '../store'
import { uploadImage, uploadFile, Attachment } from '../api/client'
import clsx from 'clsx'

export default function FileDropzone() {
  const { stagedAttachments, addAttachment, removeAttachment } = useStore()

  const onDrop = useCallback(async (files: File[]) => {
    for (const file of files) {
      try {
        const isImage = file.type.startsWith('image/')
        const res = isImage ? await uploadImage(file) : await uploadFile(file)
        addAttachment(res.attachment)
      } catch (err) {
        console.error('Upload failed', err)
      }
    }
  }, [addAttachment])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'application/pdf': ['.pdf'],
      'text/*': ['.txt', '.md', '.csv'],
    },
  })

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors text-sm',
          isDragActive
            ? 'border-brand-500 bg-brand-500/10 text-brand-400'
            : 'border-gray-700 text-gray-500 hover:border-gray-600 hover:text-gray-400',
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-5 h-5 mx-auto mb-1 opacity-60" />
        <p>Drop image, PDF, or text file</p>
      </div>

      {stagedAttachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {stagedAttachments.map((a: Attachment) => (
            <div
              key={a.name}
              className="flex items-center gap-1.5 bg-gray-800 rounded-lg px-2 py-1 text-xs text-gray-300"
            >
              {a.type === 'image' ? (
                <Image className="w-3 h-3 text-brand-400" />
              ) : (
                <FileText className="w-3 h-3 text-yellow-400" />
              )}
              <span className="max-w-[120px] truncate">{a.name}</span>
              <button
                onClick={() => removeAttachment(a.name)}
                className="text-gray-500 hover:text-gray-300 ml-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
