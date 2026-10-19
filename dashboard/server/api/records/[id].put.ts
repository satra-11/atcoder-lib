import { readRecords, writeRecords } from '../../utils/storage'
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
  const updated: ProblemRecord = {
    ...existing,
    ...body,
    id: existing.id, // IDは不変
    tags: Array.isArray(body.tags) ? body.tags.map(t => t.trim()).filter(Boolean) : existing.tags,
    updatedAt: new Date().toISOString()
  }

  records[index] = updated
  await writeRecords(records)

  return updated
})
