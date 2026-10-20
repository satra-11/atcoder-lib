/**
 * AtCoderの問題レコードの一意なプライマリーキー（ID）を生成します。
 * 例: contest: "ABC345", problem: "A" -> "abc345_a"
 * 例: contest: "ABC345", problem: "BC" -> "abc345_bc"
 * 例: contest: "typical90", problem: "001" -> "typical90_001"
 */
export function generateRecordId(contest: string, problem: string): string {
  const contestClean = (contest || '').trim().toLowerCase().replace(/\s+/g, '')
  const problemClean = (problem || '').trim().toLowerCase().replace(/\s+/g, '')
  return `${contestClean}_${problemClean}`
}
