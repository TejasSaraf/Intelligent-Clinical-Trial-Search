import type { SearchResponse } from '../types/search'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export function getSearchApiUrl(query: string, page = 1, size = 10): string {
  const encoded = encodeURIComponent(query.trim())
  return `${API_BASE}/search/${encoded}?page=${page}&size=${size}`
}

export async function searchClinicalTrials(
  query: string,
  page = 1,
  size = 10
): Promise<SearchResponse> {
  const url = getSearchApiUrl(query, page, size)
  const res = await fetch(url)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `Search failed: ${res.status}`)
  }
  return res.json()
}

export async function getThinkingMessage(query: string): Promise<string> {
  const encoded = encodeURIComponent(query.trim())
  const url = `${API_BASE}/search/thinking/${encoded}`
  const res = await fetch(url)
  if (!res.ok) return 'Searching clinical trials…'
  const data = await res.json()
  return data.thinking ?? 'Searching clinical trials…'
}
