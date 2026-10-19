import { readRecords, writeRecords } from '../utils/storage'
import type { ProblemRecord } from '~/types/record'

export default defineEventHandler(async (event) => {
  const body = await readBody<Partial<ProblemRecord>>(event)

  if (!body.contest || !body.problem || !body.result) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Contest, Problem, and Result are required'
    })
  }

  const now = new Date().toISOString()
  const contestClean = body.contest.trim().toLowerCase()
  const problemClean = body.problem.trim().toLowerCase()
  const id = body.id?.trim() || `${contestClean}_${problemClean}_${Date.now()}`

  // URLが未指定の場合、AtCoderの標準URLを自動補完
  let url = body.url?.trim() || ''
  if (!url && contestClean && problemClean) {
    url = `https://atcoder.jp/contests/${contestClean}/tasks/${contestClean}_${problemClean}`
  }

  const newRecord: ProblemRecord = {
    id,
    contest: body.contest.trim().toUpperCase(),
    problem: body.problem.trim().toUpperCase(),
    url,
    difficulty: body.difficulty || 'brown',
    result: body.result,
    solvedAt: body.solvedAt || now,
    timeMinutes: body.timeMinutes !== undefined ? body.timeMinutes : null,
    tags: Array.isArray(body.tags) ? body.tags.map(t => t.trim()).filter(Boolean) : [],
    reviewNeeded: Boolean(body.reviewNeeded),
    memo: body.memo?.trim() || '',
    createdAt: now,
    updatedAt: now
  }

  const records = await readRecords()
  records.unshift(newRecord)
  await writeRecords(records)

  return newRecord
})
