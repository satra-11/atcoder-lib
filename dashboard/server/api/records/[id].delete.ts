import { readRecords, writeRecords } from '../../utils/storage'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) {
    throw createError({ statusCode: 400, statusMessage: 'ID is required' })
  }

  const records = await readRecords()
  const filtered = records.filter(r => r.id !== id)

  if (filtered.length === records.length) {
    throw createError({ statusCode: 404, statusMessage: 'Record not found' })
  }

  await writeRecords(filtered)
  return { success: true, id }
})
