import type { TrialHit } from '../types/search'
import TrialCard from './TrialCard'

interface ResultsListProps {
  results: TrialHit[]
  total: number
  page: number
  size: number
  onShowMore?: () => void
  isLoadingMore?: boolean
  onViewDetails?: (nctId: string) => void
}

function TrialCardSkeleton() {
  return (
    <article
      className="rounded-xl border border-gray-700/80 bg-gray-800/50 p-4"
      aria-hidden
    >
      <div className="mb-2 h-5 w-3/4 max-w-sm animate-pulse rounded bg-gray-600" />
      <div className="grid grid-cols-2 gap-2">
        <div className="h-4 w-20 animate-pulse rounded bg-gray-600" />
        <div className="h-4 w-16 animate-pulse rounded bg-gray-600" />
        <div className="col-span-2 h-4 w-full animate-pulse rounded bg-gray-600" />
        <div className="h-4 w-24 animate-pulse rounded bg-gray-600" />
      </div>
    </article>
  )
}

function ResultsList({
  results,
  total,
  page,
  size,
  onShowMore,
  isLoadingMore = false,
  onViewDetails,
}: ResultsListProps) {
  if (results.length === 0) {
    return (
      <p className="py-8 text-center text-gray-400">No trials found.</p>
    )
  }

  const from = (page - 1) * size + 1
  const to = Math.min(page * size, total)
  const hasMore = total > results.length
  const remaining = total - results.length
  const nextBatch = Math.min(size, remaining)

  return (
    <section className="w-full max-w-4xl" aria-label="Search results">
      <div className="mb-4 flex flex-wrap items-baseline gap-x-2 gap-y-1 text-sm text-gray-400">
        <span>
          Showing <span className="font-medium text-gray-300">{from}–{to}</span> of {total} trials
        </span>
        {hasMore && (
          <span className="text-gray-500">· {remaining} more available</span>
        )}
      </div>
      <ul className="flex flex-col gap-3">
        {results.map((trial) => (
          <li key={trial.nct_id ?? undefined}>
            <TrialCard trial={trial} onViewDetails={onViewDetails} />
          </li>
        ))}
      </ul>
      {hasMore && onShowMore && (
        <div className="mt-6 border-t border-gray-700/80 pt-5">
          <div className="flex flex-col items-center gap-2">
            {isLoadingMore ? (
              <>
                <p className="text-sm text-gray-500">Loading more trials…</p>
                <ul className="flex w-full flex-col gap-3" aria-hidden>
                  {[1, 2, 3].map((i) => (
                    <li key={i}>
                      <TrialCardSkeleton />
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <button
                type="button"
                onClick={onShowMore}
                className="rounded-xl border border-gray-600 bg-gray-800/80 px-5 py-2.5 text-sm font-medium text-gray-200 shadow-sm transition hover:border-gray-500 hover:bg-gray-700/80 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-black"
              >
                Load {nextBatch} more {remaining > size ? `(${remaining} remaining)` : ''}
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  )
}

export default ResultsList
