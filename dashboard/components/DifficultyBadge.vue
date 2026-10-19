<script setup lang="ts">
import { formatDifficulty } from '~/lib/utils'
import type { DifficultyColor } from '~/types/record'

const props = defineProps<{
  difficulty?: DifficultyColor | string
  class?: string
}>()

const diffInfo = computed(() => formatDifficulty(props.difficulty))
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-all',
      diffInfo.bgClass,
      diffInfo.textClass,
      diffInfo.borderClass,
      props.class
    ]"
  >
    <span class="inline-block w-1.5 h-1.5 rounded-full" :class="diffInfo.textClass.replace('text-', 'bg-')" />
    <span>{{ diffInfo.label }}</span>
  </span>
</template>
