<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProblemRecord, DifficultyColor } from '~/types/record'
import StatCards from '~/components/StatCards.vue'
import DifficultyBadge from '~/components/DifficultyBadge.vue'
import ResultBadge from '~/components/ResultBadge.vue'
import RecordFormModal from '~/components/RecordFormModal.vue'
import RecordDetailModal from '~/components/RecordDetailModal.vue'

const toast = useToast()

// Fetch records from backend API
const { data: recordsData, refresh, pending } = await useFetch<ProblemRecord[]>('/api/records', {
  default: () => []
})

const records = computed(() => recordsData.value || [])

// UI State
const isFormModalOpen = ref(false)
const editingRecord = ref<ProblemRecord | null>(null)
const isDetailModalOpen = ref(false)
const selectedRecord = ref<ProblemRecord | null>(null)
const viewMode = ref<'table' | 'cards'>('table')

// Filters & Sorting
const searchQuery = ref('')
const filterDifficulty = ref<string>('all')
const filterResult = ref<string>('all')
const filterTag = ref<string>('all')
const filterReviewOnly = ref(false)
const sortBy = ref<'date_desc' | 'date_asc' | 'diff_desc' | 'diff_asc' | 'time_desc'>('date_desc')

const diffOrder: Record<string, number> = {
  gray: 1,
  brown: 2,
  green: 3,
  cyan: 4,
  blue: 5,
  yellow: 6,
  orange: 7,
  red: 8
}

const difficultyOptions = [
  { label: '難易度: すべて', value: 'all' },
  { label: '灰', value: 'gray' },
  { label: '茶', value: 'brown' },
  { label: '緑', value: 'green' },
  { label: '水', value: 'cyan' },
  { label: '青', value: 'blue' },
  { label: '黄', value: 'yellow' },
  { label: '橙', value: 'orange' },
  { label: '赤', value: 'red' }
]

const resultOptions = [
  { label: '結果: すべて', value: 'all' },
  { label: 'AC (正答)', value: 'AC' },
  { label: '解説AC', value: '解説AC' },
  { label: 'WA (誤答)', value: 'WA' },
  { label: 'TLE / MLE', value: 'TLE' },
  { label: 'RE / CE', value: 'RE' }
]

const sortOptions = [
  { label: '解答日 (新しい順)', value: 'date_desc' },
  { label: '解答日 (古い順)', value: 'date_asc' },
  { label: '難易度 (高い順)', value: 'diff_desc' },
  { label: '難易度 (低い順)', value: 'diff_asc' },
  { label: '所要時間 (長い順)', value: 'time_desc' }
]

// 蓄積されている全ユニークタグ一覧
const allTags = computed(() => {
  const set = new Set<string>()
  for (const r of records.value) {
    if (Array.isArray(r.tags)) {
      for (const t of r.tags) {
        if (t.trim()) set.add(t.trim())
      }
    }
  }
  return Array.from(set).sort()
})

const tagOptions = computed(() => [
  { label: 'タグ: すべて', value: 'all' },
  ...allTags.value.map(t => ({ label: `#${t}`, value: t }))
])

// フィルタリング & ソート済みレコード
const filteredRecords = computed(() => {
  return records.value.filter(r => {
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.trim().toLowerCase()
      const matchContest = r.contest?.toLowerCase().includes(q)
      const matchProblem = r.problem?.toLowerCase().includes(q)
      const matchMemo = r.memo?.toLowerCase().includes(q)
      const matchTags = r.tags?.some(t => t.toLowerCase().includes(q))
      if (!matchContest && !matchProblem && !matchMemo && !matchTags) {
        return false
      }
    }

    if (filterDifficulty.value !== 'all' && r.difficulty !== filterDifficulty.value) {
      return false
    }

    if (filterResult.value !== 'all' && r.result !== filterResult.value) {
      return false
    }

    if (filterTag.value !== 'all' && (!r.tags || !r.tags.includes(filterTag.value))) {
      return false
    }

    if (filterReviewOnly.value && !r.reviewNeeded) {
      return false
    }

    return true
  }).sort((a, b) => {
    if (sortBy.value === 'date_desc') {
      return new Date(b.solvedAt).getTime() - new Date(a.solvedAt).getTime()
    }
    if (sortBy.value === 'date_asc') {
      return new Date(a.solvedAt).getTime() - new Date(b.solvedAt).getTime()
    }
    if (sortBy.value === 'diff_desc') {
      return (diffOrder[b.difficulty] || 0) - (diffOrder[a.difficulty] || 0)
    }
    if (sortBy.value === 'diff_asc') {
      return (diffOrder[a.difficulty] || 0) - (diffOrder[b.difficulty] || 0)
    }
    if (sortBy.value === 'time_desc') {
      return (b.timeMinutes || 0) - (a.timeMinutes || 0)
    }
    return 0
  })
})

function openNewModal() {
  editingRecord.value = null
  isFormModalOpen.value = true
}

function openEditModal(record: ProblemRecord) {
  editingRecord.value = record
  isDetailModalOpen.value = false
  isFormModalOpen.value = true
}

function openDetailModal(record: ProblemRecord) {
  selectedRecord.value = record
  isDetailModalOpen.value = true
}

async function onRecordSaved(savedRecord?: ProblemRecord & { isOverwritten?: boolean }) {
  await refresh()
  const isOverwritten = Boolean(savedRecord?.isOverwritten)
  toast.add({
    title: isOverwritten ? '上書き保存しました' : '保存しました',
    description: isOverwritten
      ? `${savedRecord?.contest} ${savedRecord?.problem} の既存記録を最新の内容で上書き更新しました。`
      : '解答記録が正常に保存されました。',
    color: isOverwritten ? 'amber' : 'emerald',
    icon: isOverwritten ? 'i-lucide-refresh-cw' : 'i-lucide-check'
  })
}

async function toggleReview(record: ProblemRecord) {
  const updatedValue = !record.reviewNeeded
  try {
    record.reviewNeeded = updatedValue
    await $fetch(`/api/records/${record.id}`, {
      method: 'PUT',
      body: { reviewNeeded: updatedValue }
    })
    await refresh()
    toast.add({
      title: updatedValue ? '要復習に追加しました' : '復習完了にしました',
      color: updatedValue ? 'amber' : 'gray',
      icon: updatedValue ? 'i-lucide-bookmark' : 'i-lucide-check'
    })
  } catch (err) {
    console.error('Failed to toggle review:', err)
    record.reviewNeeded = !updatedValue
  }
}

async function deleteRecord(id: string) {
  if (!confirm('この記録を削除してもよろしいですか？')) return
  try {
    await $fetch(`/api/records/${id}`, { method: 'DELETE' })
    if (selectedRecord.value?.id === id) {
      isDetailModalOpen.value = false
      selectedRecord.value = null
    }
    await refresh()
    toast.add({
      title: '削除しました',
      color: 'red',
      icon: 'i-lucide-trash-2'
    })
  } catch (err) {
    console.error('Failed to delete record:', err)
    alert('削除に失敗しました。')
  }
}

function filterByDiffFromCard(diff: DifficultyColor) {
  filterDifficulty.value = filterDifficulty.value === diff ? 'all' : diff
}

function toggleReviewFilter() {
  filterReviewOnly.value = !filterReviewOnly.value
}

function resetFilters() {
  searchQuery.value = ''
  filterDifficulty.value = 'all'
  filterResult.value = 'all'
  filterTag.value = 'all'
  filterReviewOnly.value = false
}

function formatDate(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="flex-1 flex flex-col">
    <!-- Top Navigation Header -->
    <header class="sticky top-0 z-40 border-b border-border/80 bg-background/80 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
            <UIcon name="i-lucide-book-open" class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-base font-bold tracking-tight text-foreground">AtCoder Problem Log</h1>
              <UBadge color="gray" variant="subtle" size="xs" class="font-mono">
                Local Live
              </UBadge>
            </div>
            <p class="text-xs text-muted-foreground hidden sm:block">
              正答記録・反省点・復習ダッシュボード
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <UButton
            color="gray"
            variant="outline"
            size="sm"
            icon="i-lucide-rotate-cw"
            :loading="pending"
            title="最新データに更新"
            @click="refresh"
          />
          <UButton
            color="primary"
            variant="solid"
            size="sm"
            icon="i-lucide-plus"
            label="新しい記録を追加"
            class="shadow-sm"
            @click="openNewModal"
          />
        </div>
      </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <!-- KPI Stats Summary -->
      <StatCards
        :records="records"
        @filter-review="toggleReviewFilter"
        @filter-diff="filterByDiffFromCard"
      />

      <!-- Controls & Filter Toolbar -->
      <div class="rounded-xl border border-border/80 bg-card/40 backdrop-blur p-4 space-y-3 shadow-sm">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <!-- Search Bar -->
          <div class="flex-1">
            <UInput
              v-model="searchQuery"
              icon="i-lucide-search"
              placeholder="コンテスト、問題記号、メモ、タグで検索..."
              size="sm"
            />
          </div>

          <!-- Review Only Toggle Button -->
          <UButton
            :color="filterReviewOnly ? 'amber' : 'gray'"
            :variant="filterReviewOnly ? 'solid' : 'outline'"
            size="sm"
            :icon="filterReviewOnly ? 'i-lucide-bookmark-check' : 'i-lucide-bookmark'"
            @click="filterReviewOnly = !filterReviewOnly"
          >
            <span>要復習のみ</span>
            <UBadge
              v-if="records.filter(r => r.reviewNeeded).length > 0"
              :color="filterReviewOnly ? 'white' : 'gray'"
              variant="subtle"
              size="xs"
              class="ml-1 font-mono"
            >
              {{ records.filter(r => r.reviewNeeded).length }}
            </UBadge>
          </UButton>

          <!-- View Mode Toggle -->
          <div class="hidden sm:flex items-center border border-border rounded-md p-0.5 bg-background/50">
            <button
              class="p-1.5 rounded text-xs transition-colors"
              :class="viewMode === 'table' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:text-foreground'"
              @click="viewMode = 'table'"
              title="テーブル表示"
            >
              <UIcon name="i-lucide-list" class="w-4 h-4" />
            </button>
            <button
              class="p-1.5 rounded text-xs transition-colors"
              :class="viewMode === 'cards' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:text-foreground'"
              @click="viewMode = 'cards'"
              title="カード表示"
            >
              <UIcon name="i-lucide-layout-grid" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Filter Selects row -->
        <div class="flex flex-wrap items-center gap-2 pt-2 border-t border-border/50 text-xs">
          <div class="flex items-center gap-1.5 text-muted-foreground">
            <UIcon name="i-lucide-filter" class="w-3.5 h-3.5" />
            <span>絞り込み:</span>
          </div>

          <!-- Difficulty Select -->
          <USelect
            v-model="filterDifficulty"
            :options="difficultyOptions"
            size="xs"
            class="w-32"
          />

          <!-- Result Select -->
          <USelect
            v-model="filterResult"
            :options="resultOptions"
            size="xs"
            class="w-32"
          />

          <!-- Tag Select -->
          <USelect
            v-if="allTags.length > 0"
            v-model="filterTag"
            :options="tagOptions"
            size="xs"
            class="w-32"
          />

          <!-- Sort Select -->
          <div class="ml-auto flex items-center gap-1.5">
            <span class="text-muted-foreground hidden sm:inline">並び順:</span>
            <USelect
              v-model="sortBy"
              :options="sortOptions"
              size="xs"
              class="w-44"
            />
          </div>

          <!-- Reset Filter Button -->
          <UButton
            v-if="searchQuery || filterDifficulty !== 'all' || filterResult !== 'all' || filterTag !== 'all' || filterReviewOnly"
            color="gray"
            variant="link"
            size="xs"
            label="リセット"
            @click="resetFilters"
          />
        </div>
      </div>

      <!-- Problem List: Empty State -->
      <div
        v-if="filteredRecords.length === 0"
        class="rounded-xl border border-dashed border-border/80 p-12 text-center bg-card/20 space-y-3"
      >
        <div class="w-12 h-12 rounded-full bg-muted/60 flex items-center justify-center mx-auto text-muted-foreground">
          <UIcon name="i-lucide-sparkles" class="w-6 h-6" />
        </div>
        <h3 class="text-base font-semibold text-foreground">表示する問題記録がありません</h3>
        <p class="text-xs text-muted-foreground max-w-sm mx-auto">
          検索条件に一致する問題がないか、まだ記録が登録されていません。新しい記録を追加してみましょう。
        </p>
        <div class="pt-2">
          <UButton color="primary" size="sm" icon="i-lucide-plus" label="最初の記録を追加" @click="openNewModal" />
        </div>
      </div>

      <!-- Problem List: Table View -->
      <div
        v-else-if="viewMode === 'table'"
        class="rounded-xl border border-border/80 bg-card/60 backdrop-blur overflow-hidden shadow-sm"
      >
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm border-collapse">
            <thead>
              <tr class="border-b border-border bg-muted/30 text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                <th class="px-3 py-3 w-10 text-center">復習</th>
                <th class="px-4 py-3 w-28">日付</th>
                <th class="px-4 py-3 w-40">問題</th>
                <th class="px-4 py-3 w-20">難易度</th>
                <th class="px-4 py-3 w-24">結果</th>
                <th class="px-4 py-3 w-20">時間</th>
                <th class="px-4 py-3 w-64">アルゴリズム / タグ</th>
                <th class="px-4 py-3 min-w-[240px]">反省点・メモ</th>
                <th class="px-4 py-3 w-24 text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/60">
              <tr
                v-for="record in filteredRecords"
                :key="record.id"
                class="hover:bg-muted/30 transition-colors group cursor-pointer"
                @click="openDetailModal(record)"
              >
                <!-- Review Bookmark Button -->
                <td class="px-4 py-3 text-center" @click.stop="toggleReview(record)">
                  <button
                    class="p-1 rounded hover:bg-muted/80 text-muted-foreground transition-colors"
                    :class="record.reviewNeeded ? 'text-amber-400' : 'opacity-30 group-hover:opacity-70'"
                    :title="record.reviewNeeded ? '要復習 (クリックで解除)' : '要復習にする'"
                  >
                    <UIcon name="i-lucide-bookmark" class="w-4 h-4" :class="record.reviewNeeded ? 'fill-amber-400' : ''" />
                  </button>
                </td>

                <!-- Date -->
                <td class="px-4 py-3 text-xs text-muted-foreground font-mono whitespace-nowrap">
                  {{ formatDate(record.solvedAt) }}
                </td>

                <!-- Contest & Problem -->
                <td class="px-4 py-3 font-medium whitespace-nowrap">
                  <div class="flex items-center gap-1.5">
                    <span class="font-mono text-xs px-2 py-0.5 rounded bg-muted text-foreground border border-border/60 font-bold group-hover:border-primary/50 transition-colors">
                      {{ record.contest }} - {{ record.problem }}
                    </span>
                    <a
                      v-if="record.url"
                      :href="record.url"
                      target="_blank"
                      class="text-muted-foreground hover:text-primary opacity-0 group-hover:opacity-100 transition-opacity p-0.5"
                      title="AtCoderで開く"
                      @click.stop
                    >
                      <UIcon name="i-lucide-external-link" class="w-3.5 h-3.5" />
                    </a>
                  </div>
                </td>

                <!-- Difficulty Badge -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <DifficultyBadge :difficulty="record.difficulty" />
                </td>

                <!-- Result -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <ResultBadge :result="record.result" />
                </td>

                <!-- Time -->
                <td class="px-4 py-3 text-xs text-muted-foreground font-mono whitespace-nowrap">
                  <span v-if="record.timeMinutes">{{ record.timeMinutes }} 分</span>
                  <span v-else class="opacity-30">-</span>
                </td>

                <!-- Tags -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-1.5 flex-nowrap">
                    <UBadge
                      v-for="tag in (record.tags || []).slice(0, 3)"
                      :key="tag"
                      color="gray"
                      variant="subtle"
                      size="xs"
                    >
                      #{{ tag }}
                    </UBadge>
                    <span v-if="(record.tags || []).length > 3" class="text-[10px] text-muted-foreground font-mono">
                      +{{ record.tags.length - 3 }}
                    </span>
                  </div>
                </td>

                <!-- Memo excerpt -->
                <td class="px-4 py-3 text-xs text-muted-foreground max-w-sm truncate font-sans">
                  {{ record.memo || '-' }}
                </td>

                <!-- Actions -->
                <td class="px-4 py-3 text-right whitespace-nowrap" @click.stop>
                  <div class="flex items-center justify-end gap-1">
                    <UButton
                      color="gray"
                      variant="ghost"
                      size="xs"
                      icon="i-lucide-edit-3"
                      @click="openEditModal(record)"
                    />
                    <UButton
                      color="red"
                      variant="ghost"
                      size="xs"
                      icon="i-lucide-trash-2"
                      @click="deleteRecord(record.id)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Problem List: Cards View -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard
          v-for="record in filteredRecords"
          :key="record.id"
          :ui="{ body: { padding: 'p-4 sm:p-5' } }"
          class="hover:border-border transition-all cursor-pointer group flex flex-col justify-between"
          @click="openDetailModal(record)"
        >
          <div>
            <!-- Top Card Header -->
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-mono text-sm px-2 py-0.5 rounded bg-muted text-foreground font-bold border border-border/60">
                  {{ record.contest }} - {{ record.problem }}
                </span>
                <DifficultyBadge :difficulty="record.difficulty" />
                <ResultBadge :result="record.result" />
              </div>

              <div class="flex items-center gap-1">
                <a
                  v-if="record.url"
                  :href="record.url"
                  target="_blank"
                  class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-primary transition-colors"
                  title="AtCoderで開く"
                  @click.stop
                >
                  <UIcon name="i-lucide-external-link" class="w-3.5 h-3.5" />
                </a>
                <button
                  class="p-1 rounded hover:bg-muted text-muted-foreground transition-colors"
                  :class="record.reviewNeeded ? 'text-amber-400' : 'opacity-40 hover:opacity-100'"
                  :title="record.reviewNeeded ? '要復習' : '復習マークをつける'"
                  @click.stop="toggleReview(record)"
                >
                  <UIcon name="i-lucide-bookmark" class="w-4 h-4" :class="record.reviewNeeded ? 'fill-amber-400' : ''" />
                </button>
              </div>
            </div>

            <!-- Memo preview -->
            <p v-if="record.memo" class="text-xs text-muted-foreground line-clamp-3 mt-3 leading-relaxed bg-muted/20 p-2 rounded border border-border/40">
              {{ record.memo }}
            </p>
          </div>

          <div>
            <!-- Tags -->
            <div v-if="record.tags && record.tags.length > 0" class="flex flex-wrap gap-1 mt-3">
              <UBadge
                v-for="tag in record.tags.slice(0, 4)"
                :key="tag"
                color="gray"
                variant="subtle"
                size="xs"
              >
                #{{ tag }}
              </UBadge>
            </div>

            <!-- Card Bottom row -->
            <div class="flex items-center justify-between pt-3 mt-3 border-t border-border/50 text-[11px] text-muted-foreground">
              <span class="font-mono">{{ formatDate(record.solvedAt) }}</span>
              <span v-if="record.timeMinutes" class="font-mono font-medium">{{ record.timeMinutes }} 分</span>
              <div class="flex items-center gap-1" @click.stop>
                <UButton
                  color="gray"
                  variant="ghost"
                  size="2xs"
                  icon="i-lucide-edit-3"
                  @click="openEditModal(record)"
                />
                <UButton
                  color="red"
                  variant="ghost"
                  size="2xs"
                  icon="i-lucide-trash-2"
                  @click="deleteRecord(record.id)"
                />
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </main>

    <!-- Modals -->
    <RecordFormModal
      v-model:open="isFormModalOpen"
      :record="editingRecord"
      :existing-tags="allTags"
      :existing-records="records"
      @saved="onRecordSaved"
    />

    <RecordDetailModal
      v-model:open="isDetailModalOpen"
      :record="selectedRecord"
      @edit="openEditModal"
      @delete="deleteRecord"
      @toggle-review="toggleReview"
    />
  </div>
</template>
