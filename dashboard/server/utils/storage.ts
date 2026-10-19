import fs from 'node:fs/promises'
import path from 'node:path'
import type { ProblemRecord } from '~/types/record'

// プロジェクトルート（dashboard の親ディレクトリ）にある records.json を参照
const RECORDS_FILE = path.resolve(process.cwd(), '../records.json')
const FALLBACK_FILE = path.resolve(process.cwd(), './records.json')

async function getFilePath(): Promise<string> {
  try {
    await fs.access(RECORDS_FILE)
    return RECORDS_FILE
  } catch {
    // もし親ディレクトリになければ、dashboard直下または親に新規作成
    try {
      await fs.access(FALLBACK_FILE)
      return FALLBACK_FILE
    } catch {
      return RECORDS_FILE
    }
  }
}

export async function readRecords(): Promise<ProblemRecord[]> {
  const filePath = await getFilePath()
  try {
    const data = await fs.readFile(filePath, 'utf-8')
    const parsed = JSON.parse(data)
    if (Array.isArray(parsed)) {
      return parsed
    }
    return []
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      const initial: ProblemRecord[] = []
      await fs.writeFile(filePath, JSON.stringify(initial, null, 2), 'utf-8')
      return initial
    }
    console.error('Failed to read records:', error)
    return []
  }
}

export async function writeRecords(records: ProblemRecord[]): Promise<void> {
  const filePath = await getFilePath()
  // 見やすい整形済みJSONとして書き込む
  const json = JSON.stringify(records, null, 2)
  await fs.writeFile(filePath, json, 'utf-8')
}
