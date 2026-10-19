import { readRecords } from '../utils/storage'

export default defineEventHandler(async () => {
  const records = await readRecords()
  // solvedAt の降順（新しい順）で返す
  return records.sort((a, b) => {
    return new Date(b.solvedAt).getTime() - new Date(a.solvedAt).getTime()
  })
})
