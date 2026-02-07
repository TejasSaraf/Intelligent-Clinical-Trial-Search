import type { TrialHit } from '../types/search'
import TrialCard from './TrialCard'

interface ResultsListProps {
  results: TrialHit[]
  total: number
  page: number
  size: number
}

function ResultsList({ results, total, page, size }: ResultsListProps) {
  if (results.length === 0) {
    return (
      <p className="py-8 text-center text-gray-400">No trials found.</p>
    )
  }

  const from = (page - 1) * size + 1
  const to = Math.min(page * size, total)

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
    </section>
  )
}

export default ResultsList
