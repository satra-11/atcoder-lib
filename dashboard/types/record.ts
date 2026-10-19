export type DifficultyColor =
  | 'gray'
  | 'brown'
  | 'green'
  | 'cyan'
  | 'blue'
  | 'yellow'
  | 'orange'
  | 'red'

export type SubmissionResult =
  | 'AC'
  | 'WA'
  | 'TLE'
  | 'MLE'
  | 'RE'
  | 'CE'
  | '解説AC'

export interface ProblemRecord {
  id: string
  contest: string
  problem: string
  url: string
  difficulty: DifficultyColor
  result: SubmissionResult
  solvedAt: string
  timeMinutes?: number | null
  tags: string[]
  reviewNeeded: boolean
  memo: string
  createdAt?: string
  updatedAt?: string
}

export interface SummaryStats {
  total: number
  acCount: number
  kaisetsuAcCount: number
  waCount: number
  reviewCount: number
  diffCounts: Record<DifficultyColor, number>
  tagCounts: Record<string, number>
}
