import { useEffect, useState } from 'react'
import { getTrialById } from '../api/search'
import type { TrialDetail } from '../types/search'

interface TrialDetailModalProps {
  nctId: string | null
  onClose: () => void
}

function DetailRow({
  label,
  value,
  className = '',
}: {
  label: string
  value: string | null | undefined
  className?: string
}) {
  if (value == null || value === '') return null
  return (
    <div className={className}>
      <dt className="text-xs font-medium uppercase tracking-wider text-gray-500">{label}</dt>
      <dd className="mt-0.5 text-sm text-gray-200">{value}</dd>
    </div>
  )
}

function DetailBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-t border-gray-700/80 pt-4 first:border-t-0 first:pt-0">
      <h4 className="mb-2 text-sm font-semibold text-gray-300">{title}</h4>
      <div className="text-sm text-gray-300 whitespace-pre-wrap">{children}</div>
    </div>
  )
}

export default function TrialDetailModal({ nctId, onClose }: TrialDetailModalProps) {
  const [trial, setTrial] = useState<TrialDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!nctId) {
      setTrial(null)
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    getTrialById(nctId)
      .then(setTrial)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load trial'))
      .finally(() => setLoading(false))
  }, [nctId])

  if (nctId == null) return null

  const title = trial?.brief_title || trial?.official_title || nctId

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto pt-24 pb-8 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="trial-detail-title"
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div className="relative flex max-h-[90vh] w-full max-w-xl flex-col rounded-2xl border border-gray-600 bg-gray-700 shadow-xl">
        <div className="flex shrink-0 items-center justify-between border-b border-gray-700 px-5 py-4">
          <h2 id="trial-detail-title" className="pr-4 text-lg font-semibold text-white truncate">
            {loading ? 'Loading…' : title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-gray-500"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          {error && (
            <p className="text-sm text-red-400" role="alert">
              {error}
            </p>
          )}
          {loading && !trial && (
            <div className="flex items-center justify-center py-12">
              <span className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-gray-500 border-t-gray-200" />
            </div>
          )}
          {trial && !error && (
            <dl className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <DetailRow label="NCT ID" value={trial.nct_id} />
                <DetailRow label="Status" value={trial.overall_status} />
                <DetailRow label="Phase" value={trial.phase} />
                <DetailRow label="Study type" value={trial.study_type} />
                <DetailRow label="Enrollment" value={trial.enrollment != null ? String(trial.enrollment) : null} />
                <DetailRow label="Start date" value={trial.start_date} />
                <DetailRow label="Completion date" value={trial.completion_date} />
                <DetailRow label="Primary completion" value={trial.primary_completion_date} />
                <DetailRow label="Gender" value={trial.gender} />
                <DetailRow label="Age" value={[trial.minimum_age, trial.maximum_age].filter(Boolean).join(' – ') || undefined} />
              </div>
              {trial.condition_names?.length > 0 && (
                <DetailRow label="Conditions" value={trial.condition_names.join(', ')} />
              )}
              {trial.sponsor_names?.length > 0 && (
                <DetailRow label="Sponsors" value={trial.sponsor_names.join(', ')} />
              )}
              {(trial.facility_countries?.length || trial.facility_cities?.length) ? (
                <DetailRow
                  label="Locations"
                  value={[...(trial.facility_cities ?? []), ...(trial.facility_countries ?? [])].filter(Boolean).join(', ') || undefined}
                />
              ) : null}
              {trial.brief_summaries_description && (
                <DetailBlock title="Summary">{trial.brief_summaries_description}</DetailBlock>
              )}
              {trial.detailed_description && (
                <DetailBlock title="Detailed description">{trial.detailed_description}</DetailBlock>
              )}
              {trial.eligibility_criteria && (
                <DetailBlock title="Eligibility criteria">{trial.eligibility_criteria}</DetailBlock>
              )}
            </dl>
          )}
        </div>
      </div>
    </div>
  )
}
