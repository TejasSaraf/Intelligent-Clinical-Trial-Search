import type { TrialHit } from '../types/search'
import TrialCard from './TrialCard'

interface ResultsListProps {
  results: TrialHit[]
  total: number
  page: number
  size: number
  onShowMore?: () => void
  isLoadingMore?: boolean
}

function ResultsList({
  results,
  total,
  page,
  size,
  onShowMore,
  isLoadingMore = false,
}: ResultsListProps) {
  if (results.length === 0) {
    return (
      <p className="py-8 text-center text-gray-400">No trials found.</p>
    )
  }

  const from = (page - 1) * size + 1
  const to = Math.min(page * size, total)
  const hasMore = total > results.length

  return (
    <section className="w-full max-w-4xl">
      <p className="mb-4 text-sm text-gray-400">
        Showing {from}–{to} of {total} trials
      </p>
      <ul className="flex flex-col gap-3">
        {results.map((trial) => (
          <li key={trial.nct_id ?? undefined}>
            <TrialCard trial={trial} />
          </li>
        ))}
      </ul>
      {hasMore && onShowMore && (
        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={onShowMore}
            disabled={isLoadingMore}
            className="rounded-lg border border-gray-500 bg-gray-800 px-4 py-2 text-sm font-medium text-gray-200 transition hover:bg-gray-700 disabled:opacity-50"
          >
            {isLoadingMore ? 'Loading…' : 'Show more'}
          </button>
        </div>
      )}
    </section>
  )
}

export default ResultsList
