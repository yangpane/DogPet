<script setup lang="ts">
import { PET_STATE_IDS, PET_STATE_LABELS } from '@/pet-frame/states'

const demoFrameCounts: Record<string, number> = {
  idle: 1,
  typing: 12,
  click: 4,
  mouse: 12,
  sleep: 6,
  random: 9,
  space: 8,
}

function getFrameCount(stateId: string) {
  return demoFrameCounts[stateId] ?? 0
}

function getPreviewGif(stateId: string) {
  if (stateId === 'typing') return '/pet-preview/typing-sequence-clean-preview.gif'
  if (stateId === 'mouse') return '/pet-preview/drag-sequence-clean-preview.gif'

  return `/pet-preview/${stateId}-hit-preview.gif`
}
</script>

<template>
  <div class="min-h-screen bg-[#f4f6f8] p-6 text-[#1f2328]">
    <div class="mx-auto max-w-6xl flex flex-col gap-5">
      <div class="p-5 bg-white rounded shadow-sm">
        <div class="font-bold text-xl">
          自定义图片帧桌宠 MVP 预览
        </div>
        <div class="mt-2 text-[#5f6b7a]">
          浏览器预览只展示设置界面和状态结构；完整桌面宠物、全局键鼠监听、透明置顶窗口需要通过 Tauri 桌面应用运行。
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        <div class="h-80 flex flex-col items-center justify-center gap-3 bg-black/85 p-5 text-center text-white rounded">
          <img
            alt="小狗待机预览"
            class="max-h-52 max-w-full object-contain"
            src="/pet-preview/idle-clean-preview.gif"
          >
          <div class="font-bold text-lg">
            待机状态预览
          </div>
          <div class="leading-6 opacity-75 text-sm">
            当前已接入你提供的 6 组小狗素材。完整桌宠、全局键鼠监听、透明置顶窗口需要通过 Tauri 桌面应用运行。
          </div>
        </div>

        <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <div
            v-for="stateId in PET_STATE_IDS"
            :key="stateId"
            class="p-4 bg-white rounded shadow-sm"
          >
            <div class="flex items-center justify-between">
              <div class="font-bold">
                {{ PET_STATE_LABELS[stateId] }}
              </div>
              <div class="text-[#5f6b7a] text-xs">
                {{ getFrameCount(stateId) }} frames
              </div>
            </div>

            <div class="mt-3 h-32 flex items-center justify-center overflow-hidden bg-[#eef1f4] text-[#5f6b7a] rounded">
              <img
                v-if="getFrameCount(stateId) > 0"
                :alt="`${PET_STATE_LABELS[stateId]}状态`"
                class="h-full w-full object-contain"
                :src="getPreviewGif(stateId)"
              >
              <template v-else>
                {{ PET_STATE_LABELS[stateId] }}素材未上传
              </template>
            </div>

            <div class="mt-3 flex items-center justify-between">
              <button class="bg-[#1677ff] px-3 py-1.5 text-white rounded">
                上传帧
              </button>
              <div class="text-[#5f6b7a] text-xs">
                FPS 10
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="p-4 text-[#5f6b7a] bg-white rounded shadow-sm">
        固定触发：键盘输入播放三段式打字动画，鼠标移动只计为活跃，按住宠物播放拖拽进入/循环/退出动画，长时间无操作进入睡觉，待机时偶尔插入小动作。
      </div>
    </div>
  </div>
</template>
