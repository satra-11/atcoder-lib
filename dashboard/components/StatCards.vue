<script setup lang="ts">
import type { ProblemRecord, DifficultyColor } from '~/types/record'

const props = defineProps<{
  records: ProblemRecord[]
}>()

const emit = defineEmits<{
  (e: 'filter-review'): void
  (e: 'filter-diff', diff: DifficultyColor): void
}>()

const diffColors: DifficultyColor[] = ['gray', 'brown', 'green', 'cyan', 'blue', 'yellow', 'orange', 'red']

const diffBgMap: Record<DifficultyColor, string> = {
  gray: 'bg-zinc-400',
  brown: 'bg-amber-600',
  green: 'bg-emerald-500',
  cyan: 'bg-cyan-400',
  blue: 'bg-blue-500',
  yellow: 'bg-yellow-400',
  orange: 'bg-orange-500',
  red: 'bg-rose-500'
}

const stats = computed(() => {
  const total = props.records.length
  const acCount = props.records.filter(r => r.result === 'AC').length
  const kaisetsuCount = props.records.filter(r => r.result === '解説AC').length
  const waCount = props.records.filter(r => r.result === 'WA').length
  const reviewCount = props.records.filter(r => r.reviewNeeded).length

  const acRate = total > 0 ? Math.round((acCount / total) * 100) : 0
  const totalAcRate = total > 0 ? Math.round(((acCount + kaisetsuCount) / total) * 100) : 0

  const diffDistribution = diffColors.map(color => {
    const count = props.records.filter(r => r.difficulty === color).length
    const percentage = total > 0 ? Math.round((count / total) * 100) : 0
    return { color, count, percentage }
  })

  return {
    total,
    acCount,
    kaisetsuCount,
    waCount,
    reviewCount,
    acRate,
    totalAcRate,
    diffDistribution
  }
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Total Problems -->
    <UCard :ui="{ body: { padding: 'p-4 sm:p-5' } }" class="hover:border-border/80 transition-colors">
      <div class="flex items-center justify-between pb-2">
        <span class="text-sm font-medium text-muted-foreground">総解答記録数</span>
        <UIcon name="i-lucide-bar-chart-3" class="h-4 w-4 text-muted-foreground" />
      </div>
      <div>
        <div class="text-3xl font-bold font-mono tracking-tight">{{ stats.total }} <span class="text-sm font-normal text-muted-foreground">問</span></div>
        <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1.5">
          <span class="text-emerald-400 font-semibold font-mono">{{ stats.acCount + stats.kaisetsuCount }} AC</span>
          <span>(自力+解説AC)</span>
        </p>
      </div>
    </UCard>

    <!-- AC Rate -->
    <UCard :ui="{ body: { padding: 'p-4 sm:p-5' } }" class="hover:border-border/80 transition-colors">
      <div class="flex items-center justify-between pb-2">
        <span class="text-sm font-medium text-muted-foreground">自力AC率 / 全AC率</span>
        <UIcon name="i-lucide-check-circle-2" class="h-4 w-4 text-emerald-400" />
      </div>
      <div>
        <div class="flex items-baseline gap-2">
          <span class="text-3xl font-bold font-mono tracking-tight text-emerald-400">{{ stats.acRate }}%</span>
          <span class="text-xs text-muted-foreground font-mono">/ 全体 {{ stats.totalAcRate }}%</span>
        </div>
        <p class="text-xs text-muted-foreground mt-1">
          自力: {{ stats.acCount }} / 解説: {{ stats.kaisetsuCount }} / WA: {{ stats.waCount }}
        </p>
      </div>
    </UCard>

    <!-- Review Needed -->
    <UCard
      :ui="{ body: { padding: 'p-4 sm:p-5' } }"
      class="hover:border-amber-500/50 cursor-pointer transition-all group"
      @click="emit('filter-review')"
    >
      <div class="flex items-center justify-between pb-2">
        <span class="text-sm font-medium text-muted-foreground">要復習リスト</span>
        <UIcon name="i-lucide-bookmark-check" class="h-4 w-4 text-amber-400" />
      </div>
      <div>
        <div class="text-3xl font-bold font-mono tracking-tight text-amber-400">
          {{ stats.reviewCount }} <span class="text-sm font-normal text-muted-foreground">問</span>
        </div>
        <p class="text-xs text-muted-foreground mt-1 group-hover:text-amber-300 transition-colors">
          クリックで復習対象を絞り込み →
        </p>
      </div>
    </UCard>

    <!-- Difficulty Distribution -->
    <UCard :ui="{ body: { padding: 'p-4 sm:p-5' } }" class="hover:border-border/80 transition-colors">
      <div class="flex items-center justify-between pb-2">
        <span class="text-sm font-medium text-muted-foreground">難易度分布</span>
        <UIcon name="i-lucide-layers" class="h-4 w-4 text-muted-foreground" />
      </div>
      <div>
        <div class="h-2 w-full rounded-full bg-muted overflow-hidden flex mt-1.5 mb-2">
          <div
            v-for="d in stats.diffDistribution"
            :key="d.color"
            :style="{ width: `${d.percentage}%` }"
            :class="diffBgMap[d.color]"
            class="h-full transition-all duration-300"
            :title="`${d.color}: ${d.count}問`"
          />
        </div>
        <div class="flex items-center justify-between text-[11px] text-muted-foreground">
          <span
            v-for="d in stats.diffDistribution.filter(x => x.count > 0)"
            :key="d.color"
            class="cursor-pointer hover:underline font-mono"
            @click.stop="emit('filter-diff', d.color)"
          >
            <span class="inline-block w-1.5 h-1.5 rounded-full mr-0.5" :class="diffBgMap[d.color]" />
            {{ d.count }}
          </span>
          <span v-if="stats.diffDistribution.every(x => x.count === 0)" class="text-xs">データなし</span>
        </div>
      </div>
    </UCard>
  </div>
</template>
