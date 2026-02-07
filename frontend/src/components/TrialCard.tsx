import type { TrialHit } from '../types/search'

interface TrialCardProps {
  trial: TrialHit
  onViewDetails?: (nctId: string) => void
}

function TrialCard({ trial, onViewDetails }: TrialCardProps) {
  const title = trial.brief_title || trial.official_title || 'Untitled'
  const status = trial.overall_status ?? '—'
  const phase = trial.phase ?? '—'
  const conditions = trial.condition_names?.length ? trial.condition_names.join(', ') : '—'
  const sponsor = trial.sponsor_names?.length ? trial.sponsor_names[0] : '—'
  const hasDetails = trial.nct_id && onViewDetails

  return (
    <article className="rounded-xl border border-gray-700 bg-black p-4 text-left transition hover:border-gray-600">
      <h3 className="mb-2 font-semibold text-white line-clamp-2">{title}</h3>
      <dl className="grid grid-cols-1 gap-1 text-sm sm:grid-cols-2">
        <div>
          <dt className="inline font-medium text-gray-400">Status </dt>
          <dd className="inline text-gray-300">{status}</dd>
        </div>
        <div>
          <dt className="inline font-medium text-gray-400">Phase </dt>
          <dd className="inline text-gray-300">{phase}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="inline font-medium text-gray-400">Conditions </dt>
          <dd className="inline text-gray-300 line-clamp-1">{conditions}</dd>
        </div>
        <div>
          <dt className="inline font-medium text-gray-400">Sponsor </dt>
          <dd className="inline text-gray-300 line-clamp-1">{sponsor}</dd>
        </div>
      </dl>
      {hasDetails && (
        <div className="mt-3 border-t border-gray-700/80 pt-3">
          <button
            type="button"
            onClick={() => onViewDetails(trial.nct_id!)}
            className="text-sm font-medium text-gray-400 underline decoration-gray-500 underline-offset-2 transition hover:text-gray-200 hover:decoration-gray-400"
          >
            View details
          </button>
        </div>
      )}
    </article>
  )
}

export default TrialCard
