import { useEffect, useState } from 'react'
import './App.css'
import Nav from './components/Nav'
import SearchInput from './components/SearchInput'
import { getThinkingMessage, searchClinicalTrials } from './api/search'

type Message = { role: 'user' | 'assistant'; content: string }

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
      setMessages((prev) => [...prev, { role: 'assistant', content: summary }])
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : 'Search failed'
      setError(errMsg)
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${errMsg}` }])
    } finally {
      setLoading(false)
      setThinkingText(null)
    }
  }

  const hasSearched = messages.length > 0 || loading

  return (
    <div className="flex min-h-screen flex-col bg-black text-white">
      <Nav />
      {!hasSearched ? (
        <main className="flex flex-1 flex-col items-center justify-center px-4 py-10 sm:px-6">
          <SearchInput onSearch={handleSearch} isLoading={loading} showTitle />
        </main>
      ) : (
        <>
          <main className="flex-1 overflow-auto px-4 pb-56 pt-6 sm:px-6">
            <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
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
                  <div key={i} className="flex justify-end">
                    <div className="max-w-[85%] rounded-xl rounded-br-none bg-gray-700 px-4 py-3 text-sm text-gray-100">
                      {msg.content}
                    </div>
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
            <div className="mx-auto max-w-4xl px-4 sm:px-6">
              <SearchInput onSearch={handleSearch} isLoading={loading} showTitle={false} />
            </div>
          </footer>
        </>
      )}
    </div>
  )
}

export default App
