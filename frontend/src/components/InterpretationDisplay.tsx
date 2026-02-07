import type { SearchInterpretation } from '../types/search'

interface InterpretationDisplayProps {
  interpretation: SearchInterpretation
}

function InterpretationDisplay({ interpretation }: InterpretationDisplayProps) {
  const parts: string[] = []
  if (interpretation.condition) parts.push(`Condition=${interpretation.condition}`)
  if (interpretation.phase) parts.push(`Phase=${interpretation.phase}`)
  if (interpretation.status) parts.push(`Status=${interpretation.status}`)
  if (interpretation.keywords?.length) parts.push(`Keywords=${interpretation.keywords.join(', ')}`)
  if (interpretation.title_contains) parts.push(`Title contains="${interpretation.title_contains}"`)
  if (interpretation.enrollment_min != null) parts.push(`Enrollment ≥ ${interpretation.enrollment_min}`)
  if (interpretation.location) parts.push(`Location=${interpretation.location}`)

  if (parts.length === 0) {
    return (
      <p className="text-sm text-gray-400">We understood: (no filters extracted)</p>
    )
  }

  return (
    <p className="text-sm text-gray-300">
      <span className="font-medium text-white">We understood:</span>{' '}
      {parts.join(', ')}
    </p>
  )
}

export default InterpretationDisplay
