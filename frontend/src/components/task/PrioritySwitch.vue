<template>
  <el-dropdown trigger="click" @command="handleCommand" @click.stop>
    <el-tag
      size="small"
      :color="currentOption.color"
      effect="dark"
      style="cursor: pointer; border: none; color: #fff"
      @click.stop
    >
      {{ props.priority }}
    </el-tag>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="p in PRIORITY_OPTIONS"
          :key="p.value"
          :command="p.value"
          :disabled="p.value === props.priority"
        >
          {{ p.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed } from 'vue'
import { PRIORITY_OPTIONS } from '../../utils/constants'

const props = defineProps({
  priority: { type: String, required: true },
})
const emit = defineEmits(['change'])

const currentOption = computed(() =>
  PRIORITY_OPTIONS.find((o) => o.value === props.priority) || PRIORITY_OPTIONS[1]
)

function handleCommand(newPriority) {
  emit('change', newPriority)
}
</script>
