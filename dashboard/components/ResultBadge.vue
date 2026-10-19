<script setup lang="ts">
import { formatResult } from '~/lib/utils'
import type { SubmissionResult } from '~/types/record'

const props = defineProps<{
  result: SubmissionResult | string
  class?: string
}>()

const resultInfo = computed(() => formatResult(props.result))

const iconName = computed(() => {
  switch (props.result) {
    case 'AC': return 'i-lucide-check-circle-2'
    case '解説AC': return 'i-lucide-help-circle'
    case 'WA': return 'i-lucide-x-circle'
    default: return 'i-lucide-alert-circle'
  }
})
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-xs font-semibold border transition-all',
      resultInfo.bgClass,
      resultInfo.textClass,
      resultInfo.borderClass,
      props.class
    ]"
  >
    <UIcon :name="iconName" class="w-3.5 h-3.5" />
    <span>{{ props.result }}</span>
  </span>
</template>
