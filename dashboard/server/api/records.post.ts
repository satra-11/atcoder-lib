import { readRecords, writeRecords } from '../utils/storage'
import { generateRecordId } from '../utils/recordHelper'
import type { ProblemRecord } from '~/types/record'

export default defineEventHandler(async (event) => {
  const body = await readBody<Partial<ProblemRecord>>(event)

  if (!body.contest?.trim() || !body.problem?.trim() || !body.result) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Contest, Problem, and Result are required'
    })
  }

  const contest = body.contest.trim().toUpperCase()
  const problem = body.problem.trim().toUpperCase()
  const id = generateRecordId(contest, problem)
  const now = new Date().toISOString()

  const contestClean = contest.toLowerCase().replace(/\s+/g, '')
  const problemClean = problem.toLowerCase().replace(/\s+/g, '')

  // URLが未指定の場合、AtCoderの標準URLを自動補完
  let url = body.url?.trim() || ''
  if (!url && contestClean && problemClean) {
    url = `https://atcoder.jp/contests/${contestClean}/tasks/${contestClean}_${problemClean}`
  }

  const records = await readRecords()
  const existingIndex = records.findIndex(r => r.id === id)

  let savedRecord: ProblemRecord
  let isOverwritten = false

  if (existingIndex !== -1) {
    // 同一プライマリーキー（コンテスト＋開催番号＋難易度/問題記号）が存在する場合は上書き更新（Upsert）
    const existing = records[existingIndex]
    savedRecord = {
      ...existing,
      ...body,
      id,
      contest,
      problem,
      url,
      difficulty: body.difficulty || existing.difficulty || 'brown',
      result: body.result,
      solvedAt: body.solvedAt || existing.solvedAt || now,
      timeMinutes: body.timeMinutes !== undefined ? body.timeMinutes : existing.timeMinutes,
      tags: Array.isArray(body.tags) ? body.tags.map(t => t.trim()).filter(Boolean) : existing.tags,
      reviewNeeded: body.reviewNeeded !== undefined ? Boolean(body.reviewNeeded) : existing.reviewNeeded,
      memo: body.memo !== undefined ? body.memo.trim() : existing.memo,
      createdAt: existing.createdAt || now,
      updatedAt: now
    }
    records[existingIndex] = savedRecord
    isOverwritten = true
  } else {
    // 新規登録
    savedRecord = {
      id,
      contest,
      problem,
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
    records.unshift(savedRecord)
  }

  await writeRecords(records)

  return {
    ...savedRecord,
    isOverwritten
  }
})
