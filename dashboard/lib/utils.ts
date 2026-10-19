import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { DifficultyColor } from '~/types/record'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getDefaultDifficulty(contestType: string, problem: string): DifficultyColor {
  const p = (problem || '').toUpperCase()
  const type = (contestType || '').toUpperCase()

  // ARCの場合の目安
  if (type === 'ARC') {
    switch (p) {
      case 'A': return 'green'
      case 'B': return 'cyan'
      case 'C': return 'blue'
      case 'D': return 'yellow'
      case 'E': return 'orange'
      case 'F': return 'red'
      default: return 'blue'
    }
  }

  // AGCの場合の目安
  if (type === 'AGC') {
    switch (p) {
      case 'A': return 'cyan'
      case 'B': return 'blue'
      case 'C': return 'yellow'
      case 'D': return 'orange'
      default: return 'red'
    }
  }

  // ABCおよび標準の目安
  // A, B: 灰 / C: 茶 / D: 緑 / E: 水 / F: 青 / G: 黄 / Ex: 橙
  switch (p) {
    case 'A':
    case 'B':
      return 'gray'
    case 'C':
      return 'brown'
    case 'D':
      return 'green'
    case 'E':
      return 'cyan'
    case 'F':
      return 'blue'
    case 'G':
      return 'yellow'
    case 'EX':
    case 'H':
      return 'orange'
    default:
      return 'brown'
  }
}

export function formatDifficulty(diff?: string): { label: string; textClass: string; bgClass: string; borderClass: string } {
  switch ((diff || '').toLowerCase()) {
    case 'gray':
      return { label: '灰', textClass: 'text-zinc-400', bgClass: 'bg-zinc-500/15', borderClass: 'border-zinc-500/30' }
    case 'brown':
      return { label: '茶', textClass: 'text-amber-600', bgClass: 'bg-amber-600/15', borderClass: 'border-amber-600/30' }
    case 'green':
      return { label: '緑', textClass: 'text-emerald-500', bgClass: 'bg-emerald-500/15', borderClass: 'border-emerald-500/30' }
    case 'cyan':
      return { label: '水', textClass: 'text-cyan-400', bgClass: 'bg-cyan-400/15', borderClass: 'border-cyan-400/30' }
    case 'blue':
      return { label: '青', textClass: 'text-blue-500', bgClass: 'bg-blue-500/15', borderClass: 'border-blue-500/30' }
    case 'yellow':
      return { label: '黄', textClass: 'text-yellow-400', bgClass: 'bg-yellow-400/15', borderClass: 'border-yellow-400/30' }
    case 'orange':
      return { label: '橙', textClass: 'text-orange-500', bgClass: 'bg-orange-500/15', borderClass: 'border-orange-500/30' }
    case 'red':
      return { label: '赤', textClass: 'text-rose-500', bgClass: 'bg-rose-500/15', borderClass: 'border-rose-500/30' }
    default:
      return { label: '未定', textClass: 'text-zinc-400', bgClass: 'bg-zinc-500/15', borderClass: 'border-zinc-500/30' }
  }
}

export function formatResult(result: string): { textClass: string; bgClass: string; borderClass: string } {
  switch (result) {
    case 'AC':
      return { textClass: 'text-emerald-400', bgClass: 'bg-emerald-500/15', borderClass: 'border-emerald-500/40' }
    case '解説AC':
      return { textClass: 'text-amber-400', bgClass: 'bg-amber-500/15', borderClass: 'border-amber-500/40' }
    case 'WA':
      return { textClass: 'text-rose-400', bgClass: 'bg-rose-500/15', borderClass: 'border-rose-500/40' }
    case 'TLE':
    case 'MLE':
      return { textClass: 'text-orange-400', bgClass: 'bg-orange-500/15', borderClass: 'border-orange-500/40' }
    case 'RE':
    case 'CE':
      return { textClass: 'text-purple-400', bgClass: 'bg-purple-500/15', borderClass: 'border-purple-500/40' }
    default:
      return { textClass: 'text-zinc-400', bgClass: 'bg-zinc-500/15', borderClass: 'border-zinc-500/40' }
  }
}
