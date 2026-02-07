import { useEffect, useState } from 'react'
import './App.css'
import Nav from './components/Nav'
import ResultsList from './components/ResultsList'
import SearchInput from './components/SearchInput'
import TrialDetailModal from './components/TrialDetailModal'
import { getThinkingMessage, searchClinicalTrials } from './api/search'
import type { TrialHit } from './types/search'

type Message = {
  role: 'user' | 'assistant'
  content: string
  trials?: TrialHit[]
  total?: number
  page?: number
  size?: number
  query?: string
  corrected_query?: string | null
}

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [thinkingText, setThinkingText] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])

  useEffect(() => {
    if (window.location.pathname.startsWith('/search')) {
      window.history.replaceState(null, '', window.location.origin + '/')
    }
  }, [])

  async function handleSearch(query: string) {
    setError(null)
    setThinkingText(null)
    const trimmed = query.trim()
    setMessages((prev) => [...prev, { role: 'user', content: query }])
    const path = `/search/${encodeURIComponent(trimmed)}`
    window.history.pushState(null, '', path)
    setLoading(true)
    getThinkingMessage(query).then(setThinkingText)
    try {
      const res = await searchClinicalTrials(trimmed, 1, 10)
      const summary = res.summary ?? 'No summary available.'
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: summary,
          trials: res.results,
          total: res.total,
          page: res.page,
          size: res.size,
          query: res.corrected_query ?? trimmed,
          corrected_query: res.corrected_query ?? null,
        },
      ])
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : 'Search failed'
      setError(errMsg)
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${errMsg}` }])
    } finally {
      setLoading(false)
      setThinkingText(null)
    }
  }

  const [loadingMoreIndex, setLoadingMoreIndex] = useState<number | null>(null)
  const [detailNctId, setDetailNctId] = useState<string | null>(null)

  async function loadMoreForMessage(messageIndex: number) {
    const msg = messages[messageIndex]
    if (!msg?.query || msg.trials == null || msg.total == null) return
    const nextPage = (msg.page ?? 1) + 1
    if (msg.trials.length >= msg.total) return
    setLoadingMoreIndex(messageIndex)
    try {
      const res = await searchClinicalTrials(msg.query, nextPage, msg.size ?? 10)
      setMessages((prev) =>
        prev.map((m, i) =>
          i === messageIndex
            ? {
                ...m,
                trials: [...(m.trials ?? []), ...res.results],
                page: res.page,
              }
            : m
        )
      )
    } finally {
      setLoadingMoreIndex(null)
    }
  }

  const hasSearched = messages.length > 0 || loading

  return (
    <div className="flex min-h-screen flex-col bg-black text-white">
      <TrialDetailModal nctId={detailNctId} onClose={() => setDetailNctId(null)} />
      <Nav />
      {!hasSearched ? (
        <main className="flex flex-1 flex-col items-center justify-center px-4 py-10 sm:px-6">
          <SearchInput onSearch={handleSearch} isLoading={loading} showTitle />
        </main>
      ) : (
        <>
          <main className="flex-1 overflow-auto px-4 pb-56 pt-6 sm:px-6">
            <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
              {error && (
                <p className="w-full text-sm text-red-400" role="alert">
                  {error}
                </p>
              )}
              {messages.map((msg, i) =>
                msg.role === 'user' ? (
                  <div key={i} className="flex justify-start">
                    <div className="max-w-[85%] rounded-xl rounded-bl-none bg-gray-800 px-4 py-3 text-sm text-gray-100">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div key={i} className="flex flex-col items-end gap-3">
                    <div className="max-w-[85%] rounded-xl rounded-br-none bg-gray-700 px-4 py-3 text-sm text-gray-100">
                      {msg.corrected_query && (
                        <p className="mb-2 text-xs text-green-400" role="status">
                          Did you mean: <span className="font-medium">{msg.corrected_query}</span>? Results shown for corrected query.
                        </p>
                      )}
                      {msg.content}
                    </div>
                    {msg.trials != null && msg.trials.length > 0 && (
                      <div className="w-full max-w-[85%] border-t border-gray-600 pt-3">
                        <ResultsList
                          results={msg.trials}
                          total={msg.total ?? msg.trials.length}
                          page={msg.page ?? 1}
                          size={msg.size ?? 10}
                          onShowMore={
                            (msg.total ?? 0) > msg.trials.length && msg.query
                              ? () => loadMoreForMessage(i)
                              : undefined
                          }
                          isLoadingMore={loadingMoreIndex === i}
                          onViewDetails={setDetailNctId}
                        />
                      </div>
                    )}
                  </div>
                )
              )}
              {loading && (
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-xl rounded-br-none bg-gray-700 px-4 py-3 text-sm text-gray-100">
                    <span className="flex items-center gap-2" aria-live="polite">
                      <span className="inline-block h-2 w-2 shrink-0 animate-pulse rounded-full bg-gray-400" />
                      {thinkingText ?? 'Thinking…'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </main>
          <footer className="fixed bottom-0 left-0 right-0 bg-black py-4">
            <div className="mx-auto max-w-5xl px-4 sm:px-6">
              <SearchInput onSearch={handleSearch} isLoading={loading} showTitle={false} />
            </div>
          </footer>
        </>
      )}
    </div>
  )
}

export default App
