<script setup lang="ts">
import { convertFileSrc } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog'
import { Alert, Button, Card, Empty, InputNumber, message, Popconfirm, Space } from 'antdv-next'
import { computed } from 'vue'

import type { PetStateId } from '@/pet-frame/states'

import {
  getMissingStateIds,
  PET_STATE_IDS,
  PET_STATE_LABELS,
} from '@/pet-frame/states'
import { usePetFrameStore } from '@/stores/petFrame'

const petFrameStore = usePetFrameStore()

const missingLabels = computed(() => {
  return getMissingStateIds(petFrameStore.pack).map(id => PET_STATE_LABELS[id]).join('、')
})

async function selectFrames(stateId: PetStateId) {
  const selected = await open({
    multiple: true,
    filters: [
      {
        name: 'Images',
        extensions: ['png', 'jpg', 'jpeg', 'webp'],
      },
    ],
  })

  if (!selected) return

  const paths = Array.isArray(selected) ? selected : [selected]

  try {
    await petFrameStore.replaceStateFrames(stateId, paths)
    message.success('状态素材已更新')
  } catch (error) {
    message.error(String(error))
  }
}

async function clearFrames(stateId: PetStateId) {
  try {
    await petFrameStore.clearStateFrames(stateId)
    message.success('状态素材已清空')
  } catch (error) {
    message.error(String(error))
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <Alert
      v-if="!petFrameStore.complete"
      description="每个状态至少需要一张图片帧。完整后，桌面小狗会根据键盘、鼠标和空闲状态自动切换动画。"
      :message="`还缺少状态素材：${missingLabels}`"
      show-icon
      type="warning"
    />

    <Alert
      description="例如先上传“打字”状态素材；其他状态未配置时，桌宠触发到该状态会显示缺素材提示，不会阻止已配置状态播放。"
      message="可以先只配置一个状态"
      show-icon
      type="info"
    />

    <div class="grid grid-cols-1 gap-4 2xl:grid-cols-3 xl:grid-cols-2">
      <Card
        v-for="stateId in PET_STATE_IDS"
        :key="stateId"
        size="small"
        :title="PET_STATE_LABELS[stateId]"
      >
        <template #extra>
          <span class="color-text-secondary text-xs">
            {{ petFrameStore.pack.states[stateId].frames.length }} frames
          </span>
        </template>

        <div class="flex flex-col gap-3">
          <div class="h-42 flex items-center justify-center overflow-hidden bg-[--ant-color-fill-quaternary] rounded">
            <img
              v-if="petFrameStore.pack.states[stateId].frames[0]"
              class="max-h-full max-w-full object-contain"
              :src="convertFileSrc(petFrameStore.pack.states[stateId].frames[0])"
            >

            <Empty
              v-else
              :description="`${PET_STATE_LABELS[stateId]}素材未上传`"
              :image="Empty.PRESENTED_IMAGE_SIMPLE"
            />
          </div>

          <div class="flex items-center justify-between gap-3">
            <Space>
              <Button
                type="primary"
                @click="selectFrames(stateId)"
              >
                上传帧
              </Button>

              <Popconfirm
                title="清空这组素材？"
                @confirm="clearFrames(stateId)"
              >
                <Button danger>
                  清空
                </Button>
              </Popconfirm>
            </Space>

            <div class="flex items-center gap-2 color-text-secondary text-xs">
              <span>FPS</span>
              <InputNumber
                v-model:value="petFrameStore.pack.states[stateId].fps"
                class="w-18"
                :max="24"
                :min="1"
                @change="petFrameStore.persistManifest"
              />
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>
