export interface SearchInterpretation {
  phase: string | null
  condition: string | null
  status: string | null
  keywords: string[]
  title_contains: string | null
  enrollment_min: number | null
  location: string | null
}

export interface TrialHit {
  nct_id: string | null
  brief_title: string | null
  official_title: string | null
  overall_status: string | null
  phase: string | null
  condition_names: string[]
  sponsor_names: string[]
  enrollment: number | null
  completion_date: string | null
  score?: number | null
}

export interface TrialDetail extends TrialHit {
  brief_summaries_description?: string | null
  detailed_description?: string | null
  eligibility_criteria?: string | null
  study_type?: string | null
  start_date?: string | null
  primary_completion_date?: string | null
  facility_countries?: string[]
  facility_cities?: string[]
  gender?: string | null
  minimum_age?: string | null
  maximum_age?: string | null
}

export interface SearchResponse {
  interpretation: SearchInterpretation
  results: TrialHit[]
  total: number
  page: number
  size: number
  summary: string | null
}
