import { readRecords, writeRecords } from '../../utils/storage'
import { generateRecordId } from '../../utils/recordHelper'
import type { ProblemRecord } from '~/types/record'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) {
    throw createError({ statusCode: 400, statusMessage: 'ID is required' })
  }

  const body = await readBody<Partial<ProblemRecord>>(event)
  const records = await readRecords()
  const index = records.findIndex(r => r.id === id)

  if (index === -1) {
    throw createError({ statusCode: 404, statusMessage: 'Record not found' })
  }

  const existing = records[index]
  const newContest = (body.contest?.trim() || existing.contest).toUpperCase()
  const newProblem = (body.problem?.trim() || existing.problem).toUpperCase()
  const newId = generateRecordId(newContest, newProblem)
  const now = new Date().toISOString()

  const contestClean = newContest.toLowerCase().replace(/\s+/g, '')
  const problemClean = newProblem.toLowerCase().replace(/\s+/g, '')

  let url = body.url !== undefined ? body.url.trim() : existing.url
  if (!url && contestClean && problemClean) {
    url = `https://atcoder.jp/contests/${contestClean}/tasks/${contestClean}_${problemClean}`
  }

  const updated: ProblemRecord = {
    ...existing,
    ...body,
    id: newId,
    contest: newContest,
    problem: newProblem,
    url,
    tags: Array.isArray(body.tags) ? body.tags.map(t => t.trim()).filter(Boolean) : existing.tags,
    updatedAt: now
  }

  // IDが変更された場合
  if (newId !== id) {
    const conflictIndex = records.findIndex(r => r.id === newId)
    if (conflictIndex !== -1 && conflictIndex !== index) {
      // 既に変更先のキーが存在する場合、変更先レコードを上書き更新して元の位置のレコードを削除
      records[conflictIndex] = {
        ...records[conflictIndex],
        ...updated,
        createdAt: records[conflictIndex].createdAt || existing.createdAt
      }
      records.splice(index, 1)
      await writeRecords(records)
      return records[conflictIndex]
    }
  }

  records[index] = updated
  await writeRecords(records)

  return updated
})

