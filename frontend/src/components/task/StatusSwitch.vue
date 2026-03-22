<template>
  <el-dropdown trigger="click" @command="handleCommand" @click.stop>
    <el-tag
      :type="currentOption.type"
      :class="{ 'cancelled-tag': props.status === '已取消' }"
      style="cursor: pointer"
      @click.stop
    >
      {{ props.status }}
    </el-tag>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="s in allStatuses"
          :key="s.value"
          :command="s.value"
          :disabled="s.value === props.status"
        >
          {{ s.value }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed } from 'vue'
import { STATUS_OPTIONS } from '../../utils/constants'

const props = defineProps({
  status: { type: String, required: true },
})
const emit = defineEmits(['change'])

const currentOption = computed(() =>
  STATUS_OPTIONS.find((s) => s.value === props.status) || STATUS_OPTIONS[0]
)

const allStatuses = computed(() => STATUS_OPTIONS)

function handleCommand(newStatus) {
  emit('change', newStatus)
}
</script>

<style scoped>
.cancelled-tag {
  text-decoration: line-through;
}
</style>
