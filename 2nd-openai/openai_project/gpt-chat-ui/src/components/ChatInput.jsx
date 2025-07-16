import { ArrowUpIcon, StopIcon } from '@heroicons/react/24/solid'
import { useRef, useEffect } from 'react'

export default function ChatInput({ input, setInput, onSubmit, isDisabled, isGenerating, onStop }) {
  const textareaRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isGenerating) {
      // 생성 중이면 중지
      onStop?.()
    } else if (input.trim()) {
      // 일반 전송
      onSubmit(input)
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      const maxHeight = 160
      if (textarea.scrollHeight > maxHeight) {
        textarea.style.height = `${maxHeight}px`
        textarea.style.overflowY = 'auto'
      } else {
        textarea.style.height = `${textarea.scrollHeight}px`
        textarea.style.overflowY = 'hidden'
      }
    }
  }, [input])

  return (
    <form onSubmit={handleSubmit} className="px-4 py-3 border-t border-gray-200">
      <div className="relative w-full bg-white rounded-2xl shadow-sm p-3 border border-gray-300/70">
        <div className="pb-10">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder={isGenerating ? "답변을 생성하는 중..." : "무엇이든 물어보세요."}
            disabled={isDisabled && !isGenerating}
            className="w-full resize-none border-none bg-transparent px-1
                       focus:outline-none text-sm max-h-40
                       scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100
                       overflow-y-auto"
          />
        </div>

        <div className="absolute bottom-2 right-2">
          <button
            type="submit"
            disabled={isDisabled && !isGenerating}
            className={`w-9 h-9 flex items-center justify-center
                       rounded-full text-white hover:scale-105
                       transition-all duration-200 disabled:opacity-40
                       bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:from-[#5a6fd8] hover:to-[#6a4190]
                       ${!input.trim() && !isGenerating ? 'opacity-40' : ''}`}
          >
            {isGenerating ? (
              <StopIcon className="w-5 h-5" />
            ) : (
              <ArrowUpIcon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </form>
  )
}