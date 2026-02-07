import { useEffect, useRef, useState } from 'react'

interface SearchInputProps {
  onSearch: (query: string) => void
  isLoading?: boolean
  showTitle?: boolean
}

const PLACEHOLDER = "e.g. List all Phase 2 trials for Breast Cancer associated with BRCA1 gene"

function SearchInput({ onSearch, isLoading, showTitle = true }: SearchInputProps) {
  const [query, setQuery] = useState('')
  const editRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (query === '' && editRef.current) {
      editRef.current.textContent = ''
    }
  }, [query])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const text = query.trim()
    if (!text) return
    onSearch(text)
  }

  function handleInput() {
    const text = editRef.current?.textContent ?? ''
    setQuery(text)
  }

  function handlePaste(e: React.ClipboardEvent) {
    e.preventDefault()
    const raw = e.clipboardData.getData('text/plain')
    const text = raw.replace(/\s+/g, ' ').trim()
    const el = editRef.current
    if (!el) return
    el.focus()
    const selection = window.getSelection()
    const range = selection?.rangeCount ? selection.getRangeAt(0) : null
    const inEl = range && el.contains(range.commonAncestorContainer)
    if (inEl && range) {
      try {
        range.deleteContents()
        range.insertNode(document.createTextNode(text))
        range.collapse(false)
        selection?.removeAllRanges()
        selection?.addRange(range)
      } catch {
        el.textContent = (el.textContent ?? '') + text
      }
    } else {
      el.textContent = (el.textContent ?? '') + text
    }
    requestAnimationFrame(() => handleInput())
  }

  const SearchIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  )

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-4xl flex-col gap-4">
      {showTitle && (
        <h2 className="mb-6 text-center text-5xl font-semibold text-white">
          What's on <span className="bg-gradient-to-r from-green-200 via-green-500 to-emerald-600 bg-clip-text text-transparent">agenda today?</span>
        </h2>
      )}
      <div className="relative w-full">
        <div
          ref={editRef}
          role="textbox"
          contentEditable={!isLoading}
          suppressContentEditableWarning
          onInput={handleInput}
          onPaste={handlePaste}
          className="min-h-[7rem] w-full rounded-xl border border-gray-600 pl-4 pr-12 py-4 text-left text-white focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
          aria-placeholder={PLACEHOLDER}
          style={{ wordBreak: 'break-word', backgroundColor: 'rgb(26, 26, 26)' }}
        />
        {!query && (
          <div
            className="pointer-events-none absolute inset-0 px-4 pr-12 py-4 text-left text-gray-400"
            aria-hidden
          >
            {PLACEHOLDER}
          </div>
        )}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg bg-gray-800 p-2 text-white transition hover:bg-gray-700 disabled:opacity-50 disabled:hover:bg-gray-800"
          title={isLoading ? 'Searching…' : 'Search'}
          aria-label={isLoading ? 'Searching…' : 'Search'}
        >
          <SearchIcon />
        </button>
      </div>
    </form>
  )
}

export default SearchInput
