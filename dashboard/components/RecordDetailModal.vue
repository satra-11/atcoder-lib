<script setup lang="ts">
import type { ProblemRecord } from '~/types/record'
import DifficultyBadge from '~/components/DifficultyBadge.vue'
import ResultBadge from '~/components/ResultBadge.vue'

const props = defineProps<{
  open: boolean
  record: ProblemRecord | null
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'edit', record: ProblemRecord): void
  (e: 'delete', id: string): void
  (e: 'toggle-review', record: ProblemRecord): void
}>()

const isOpen = computed({
  get: () => props.open,
  set: (val: boolean) => emit('update:open', val)
})

function formatDate(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<template>
  <UModal v-model="isOpen" :ui="{ width: 'sm:max-w-2xl' }">
    <UCard v-if="props.record" :ui="{ ring: '', divide: 'divide-y divide-border/50' }">
      <template #header>
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex items-center gap-2 mb-1.5 flex-wrap">
              <DifficultyBadge :difficulty="props.record.difficulty" />
              <ResultBadge :result="props.record.result" />
              <UBadge
                v-if="props.record.reviewNeeded"
                color="amber"
                variant="subtle"
                size="xs"
                class="font-semibold"
              >
                <UIcon name="i-lucide-bookmark" class="w-3 h-3 mr-1 fill-amber-400" /> 要復習
              </UBadge>
            </div>
            <h2 class="text-2xl font-bold font-mono tracking-tight text-foreground flex items-center gap-2">
              <span>{{ props.record.contest }} - {{ props.record.problem }}</span>
              <a
                v-if="props.record.url"
                :href="props.record.url"
                target="_blank"
                class="text-xs font-sans font-normal text-primary hover:underline inline-flex items-center gap-0.5"
              >
                AtCoderで開く <UIcon name="i-lucide-external-link" class="w-3 h-3" />
              </a>
            </h2>
          </div>

          <div class="flex items-center gap-1.5">
            <UButton
              color="gray"
              variant="outline"
              size="xs"
              :icon="props.record.reviewNeeded ? 'i-lucide-bookmark-check' : 'i-lucide-bookmark'"
              :label="props.record.reviewNeeded ? '復習完了' : '要復習'"
              @click="emit('toggle-review', props.record)"
            />
            <UButton
              color="gray"
              variant="outline"
              size="xs"
              icon="i-lucide-edit-3"
              label="編集"
              @click="emit('edit', props.record)"
            />
            <UButton
              color="red"
              variant="ghost"
              size="xs"
              icon="i-lucide-trash-2"
              @click="emit('delete', props.record.id)"
            />
            <UButton
              color="gray"
              variant="ghost"
              size="xs"
              icon="i-lucide-x"
              @click="isOpen = false"
            />
          </div>
        </div>
      </template>

      <div class="space-y-5 py-1">
        <!-- Metadata -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3.5 rounded-lg bg-muted/40 border border-border/60 text-xs">
          <div class="flex items-center gap-1 text-muted-foreground">
            <UIcon name="i-lucide-calendar" class="w-3.5 h-3.5" />
            <span>解答日時:</span>
            <span class="text-foreground font-mono">{{ formatDate(props.record.solvedAt) }}</span>
          </div>
          <div v-if="props.record.timeMinutes" class="flex items-center gap-1 text-muted-foreground">
            <UIcon name="i-lucide-clock" class="w-3.5 h-3.5" />
            <span>所要時間:</span>
            <span class="text-foreground font-mono font-medium">{{ props.record.timeMinutes }} 分</span>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="props.record.tags && props.record.tags.length > 0">
          <h4 class="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
            <UIcon name="i-lucide-tag" class="w-3.5 h-3.5" /> アルゴリズム / トピック
          </h4>
          <div class="flex flex-wrap gap-1.5">
            <UBadge
              v-for="tag in props.record.tags"
              :key="tag"
              color="gray"
              variant="subtle"
              size="sm"
            >
              #{{ tag }}
            </UBadge>
          </div>
        </div>

        <!-- Memo -->
        <div>
          <h4 class="text-xs font-semibold text-muted-foreground mb-2">反省点・解法メモ</h4>
          <div
            v-if="props.record.memo"
            class="p-4 rounded-lg bg-muted/20 border border-border/80 text-sm whitespace-pre-wrap leading-relaxed font-sans text-foreground/90 select-text"
          >
            {{ props.record.memo }}
          </div>
          <div v-else class="text-xs text-muted-foreground italic p-3 rounded bg-muted/20">
            メモは記録されていません。
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <UButton color="gray" variant="solid" @click="isOpen = false">閉じる</UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>
