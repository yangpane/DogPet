<script setup lang="ts">
import { convertFileSrc, invoke } from '@tauri-apps/api/core'
import { PhysicalSize } from '@tauri-apps/api/dpi'
import { Menu, PredefinedMenuItem } from '@tauri-apps/api/menu'
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow'
import { useDebounceFn } from '@vueuse/core'
import { round } from 'es-toolkit'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

import type { PetStateId } from '@/pet-frame/states'

import { useAppMenu } from '@/composables/useAppMenu'
import { useTauriListen } from '@/composables/useTauriListen'
import { INVOKE_KEY, LISTEN_KEY } from '@/constants'
import { createPetStateMachine } from '@/pet-frame/machine'
import { hasRenderableState, PET_STATE_LABELS } from '@/pet-frame/states'
import { hideWindow, setAlwaysOnTop, setTaskbarVisibility, showWindow } from '@/plugins/window'
import { useCatStore } from '@/stores/cat'
import { useGeneralStore } from '@/stores/general.ts'
import { usePetFrameStore } from '@/stores/petFrame'
import { isWindows } from '@/utils/platform'

interface MouseButtonEvent {
  kind: 'MousePress' | 'MouseRelease'
  value: string
}

interface MouseMoveEvent {
  kind: 'MouseMove'
  value: {
    x: number
    y: number
  }
}

interface KeyboardEvent {
  kind: 'KeyboardPress' | 'KeyboardRelease'
  value: string
}

type DeviceEvent = MouseButtonEvent | MouseMoveEvent | KeyboardEvent
type TypingPhase = 'intro' | 'loop' | 'outro'
type DragPhase = 'enter' | 'loop' | 'exit'

function createPetPreviewFrames(stateName: string, length: number) {
  const directoryName = stateName.endsWith('-hit') ? stateName : `${stateName}-clean`

  return Array.from(
    { length },
    (_, index) => `/pet-preview/${directoryName}/${String(index + 1).padStart(3, '0')}.png`,
  )
}

const KEYBOARD_IDLE_MS = 650
const TYPING_TRANSITION_FPS = 5
const MOUSE_IDLE_MS = 520
const INACTIVE_MS = 5 * 60_000
const RANDOM_ROLL_MS = 12_000
const RANDOM_COOLDOWN_MS = 36_000
const RANDOM_CHANCE = 0.35
const FALLBACK_SIZE = 320
const PET_WINDOW_SCALE_FACTOR = 0.55
const PET_CLICK_SUPPRESSION_MS = 160
const TYPING_INTRO_FRAMES = createPetPreviewFrames('typing-intro-hit', 3)
const TYPING_OUTRO_FRAMES = createPetPreviewFrames('typing-outro-hit', 3)
const DRAG_TRANSITION_FPS = 7
const DRAG_ENTER_FRAMES = createPetPreviewFrames('drag-enter-hit', 3)
const DRAG_EXIT_FRAMES = createPetPreviewFrames('drag-exit-hit', 3)

const appWindow = getCurrentWebviewWindow()
const catStore = useCatStore()
const generalStore = useGeneralStore()
const petFrameStore = usePetFrameStore()
const { getBaseMenu, getExitMenu } = useAppMenu()
const machine = createPetStateMachine()
const frameIndex = ref(0)
const renderedSize = ref({ width: FALLBACK_SIZE, height: FALLBACK_SIZE })
const typingPhase = ref<TypingPhase>('loop')
const dragPhase = ref<DragPhase>('loop')
let typingOutroTargetState: PetStateId = 'idle'
let dragExitTargetState: PetStateId = 'idle'
let frameTimer: ReturnType<typeof setInterval> | undefined
let keyboardIdleTimer: ReturnType<typeof setTimeout> | undefined
let mouseIdleTimer: ReturnType<typeof setTimeout> | undefined
let inactiveTimer: ReturnType<typeof setTimeout> | undefined
let randomTimer: ReturnType<typeof setInterval> | undefined
let suppressGlobalMouseClickUntil = 0
let lastRandomAt = 0
let dragActive = false
let dragMoved = false

const displayState = computed(() => {
  if (hasRenderableState(petFrameStore.pack, petFrameStore.activeState)) {
    return petFrameStore.activeState
  }

  if (hasRenderableState(petFrameStore.pack, 'idle')) {
    return 'idle'
  }

  return petFrameStore.activeState
})
const currentAsset = computed(() => petFrameStore.pack.states[displayState.value])
const activeAsset = computed(() => petFrameStore.pack.states[petFrameStore.activeState])
const currentFps = computed(() => {
  if (displayState.value === 'typing' && typingPhase.value !== 'loop') return TYPING_TRANSITION_FPS
  if (displayState.value === 'mouse' && dragPhase.value !== 'loop') return DRAG_TRANSITION_FPS

  return currentAsset.value.fps
})
const currentFrames = computed(() => {
  if (displayState.value === 'typing' && typingPhase.value === 'intro') return TYPING_INTRO_FRAMES
  if (displayState.value === 'typing' && typingPhase.value === 'outro') return TYPING_OUTRO_FRAMES
  if (displayState.value === 'mouse' && dragPhase.value === 'enter') return DRAG_ENTER_FRAMES
  if (displayState.value === 'mouse' && dragPhase.value === 'exit') return DRAG_EXIT_FRAMES

  return currentAsset.value.frames
})
const currentFrame = computed(() => currentFrames.value[frameIndex.value])
const currentFrameSrc = computed(() => {
  if (!currentFrame.value) return undefined

  if (currentFrame.value.startsWith('/pet-preview/')) {
    return import.meta.env.DEV
      ? `http://localhost:1420${currentFrame.value}`
      : currentFrame.value
  }

  return convertFileSrc(currentFrame.value)
})
const currentStateReady = computed(() => hasRenderableState(petFrameStore.pack, displayState.value))
const activeOneShot = computed(() => {
  if (petFrameStore.activeState !== 'click' && petFrameStore.activeState !== 'random') return false

  return !activeAsset.value.loop
})
const resizeWindow = useDebounceFn(async () => {
  const { width, height } = renderedSize.value
  const scale = (catStore.window.scale / 100) * PET_WINDOW_SCALE_FACTOR

  await appWindow.setSize(new PhysicalSize(
    Math.max(80, Math.round(width * scale)),
    Math.max(80, Math.round(height * scale)),
  ))
}, 100)

onMounted(() => {
  if (catStore.window.visible) {
    showWindow()
  }

  invoke(INVOKE_KEY.START_DEVICE_LISTENING)
  resetInactiveTimer()
  randomTimer = setInterval(tryTriggerRandom, RANDOM_ROLL_MS)
})

onUnmounted(() => {
  clearFrameTimer()
  clearTimeout(keyboardIdleTimer)
  clearTimeout(mouseIdleTimer)
  clearTimeout(inactiveTimer)
  clearInterval(randomTimer)
})

watch(() => catStore.window.visible, (value) => {
  value ? showWindow() : hideWindow()
}, { immediate: true })

watch(() => catStore.window.passThrough, (value) => {
  appWindow.setIgnoreCursorEvents(value)
}, { immediate: true })

watch(() => catStore.window.alwaysOnTop, setAlwaysOnTop, { immediate: true })

watch(() => generalStore.app.taskbarVisible, setTaskbarVisibility, { immediate: true })

watch([() => catStore.window.scale, renderedSize], resizeWindow, { deep: true, immediate: true })

watch([currentAsset, displayState, typingPhase, dragPhase], () => {
  frameIndex.value = 0
  restartFrameTimer()
}, { immediate: true })

useTauriListen<DeviceEvent>(LISTEN_KEY.DEVICE_CHANGED, ({ payload }) => {
  resetInactiveTimer()

  if (payload.kind === 'KeyboardPress') {
    setPetState(machine.send('keyboard_active'))

    clearTimeout(keyboardIdleTimer)
    keyboardIdleTimer = setTimeout(handleKeyboardIdle, KEYBOARD_IDLE_MS)

    return
  }

  if (payload.kind === 'MousePress') {
    if (Date.now() < suppressGlobalMouseClickUntil) return

    setPetState(machine.send('mouse_click'))

    return
  }

  if (payload.kind === 'MouseRelease') {
    finishPetDrag()

    return
  }

  if (payload.kind === 'MouseMove') {
    if (dragActive) {
      dragMoved = true
      if (dragPhase.value === 'enter' && frameIndex.value >= DRAG_ENTER_FRAMES.length - 1) {
        dragPhase.value = 'loop'
      }
    }

    setPetState(machine.send('mouse_move'))

    clearTimeout(mouseIdleTimer)
    mouseIdleTimer = setTimeout(() => setPetState(machine.send('mouse_idle')), MOUSE_IDLE_MS)
  }
})

function setPetState(stateId: PetStateId) {
  if (stateId !== 'mouse') {
    dragPhase.value = 'loop'
  }

  if (stateId === 'typing') {
    if (petFrameStore.activeState !== 'typing' || typingPhase.value === 'outro') {
      typingPhase.value = 'intro'
      petFrameStore.activeState = 'typing'
      frameIndex.value = 0

      return
    }

    return
  }

  typingPhase.value = 'loop'

  if (petFrameStore.activeState === stateId) return

  petFrameStore.activeState = stateId
  frameIndex.value = 0
}

function startPetDrag() {
  dragActive = true
  dragMoved = false
  dragPhase.value = 'enter'
  setPetState(machine.send('drag_start'))
}

function finishPetDrag() {
  if (!dragActive) return

  dragActive = false
  dragMoved = false
  const nextState = machine.send('drag_end')

  if (petFrameStore.activeState === 'mouse') {
    startDragExit(nextState)

    return
  }

  setPetState(nextState)
}

function startDragExit(nextState: PetStateId) {
  dragExitTargetState = nextState
  dragPhase.value = 'exit'
  frameIndex.value = 0
}

function handleKeyboardIdle() {
  const nextState = machine.send('keyboard_idle')

  if (petFrameStore.activeState === 'typing') {
    startTypingOutro(nextState)

    return
  }

  setPetState(nextState)
}

function startTypingOutro(nextState: PetStateId) {
  typingOutroTargetState = nextState
  typingPhase.value = 'outro'
  frameIndex.value = 0
}

function tryTriggerRandom() {
  if (petFrameStore.activeState !== 'idle') return
  if (Date.now() - lastRandomAt < RANDOM_COOLDOWN_MS) return
  if (Math.random() > RANDOM_CHANCE) return

  lastRandomAt = Date.now()
  setPetState(machine.send('random_tick'))
}

function resetInactiveTimer() {
  clearTimeout(inactiveTimer)
  inactiveTimer = setTimeout(() => setPetState(machine.send('inactive_timeout')), INACTIVE_MS)

  if (petFrameStore.activeState === 'sleep') {
    setPetState(machine.send('wake'))
  }
}

function clearFrameTimer() {
  if (!frameTimer) return

  clearInterval(frameTimer)
  frameTimer = void 0
}

function restartFrameTimer() {
  clearFrameTimer()

  const fps = Math.max(1, currentFps.value)

  frameTimer = setInterval(() => {
    const frameCount = currentFrames.value.length

    if (frameCount <= 1) return

    const nextIndex = frameIndex.value + 1

    if (nextIndex < frameCount) {
      frameIndex.value = nextIndex

      return
    }

    if (displayState.value === 'typing' && typingPhase.value === 'intro') {
      typingPhase.value = 'loop'

      return
    }

    if (displayState.value === 'typing' && typingPhase.value === 'outro') {
      typingPhase.value = 'loop'
      setPetState(typingOutroTargetState)

      return
    }

    if (displayState.value === 'mouse' && dragPhase.value === 'enter') {
      if (dragMoved) {
        dragPhase.value = 'loop'

        return
      }

      frameIndex.value = frameCount - 1

      return
    }

    if (displayState.value === 'mouse' && dragPhase.value === 'exit') {
      dragPhase.value = 'loop'
      setPetState(dragExitTargetState)

      return
    }

    if (activeOneShot.value) {
      setPetState(machine.finishOneShot())

      return
    }

    if (currentAsset.value.loop) {
      frameIndex.value = 0

      return
    }

    setPetState(machine.finishOneShot())
  }, 1000 / fps)
}

function handleImageLoad(event: Event) {
  const image = event.target as HTMLImageElement

  renderedSize.value = {
    width: image.naturalWidth || FALLBACK_SIZE,
    height: image.naturalHeight || FALLBACK_SIZE,
  }
}

function handleMouseDown() {
  suppressGlobalMouseClickUntil = Date.now() + PET_CLICK_SUPPRESSION_MS
  resetInactiveTimer()
  startPetDrag()
  appWindow.startDragging()
}

async function handleContextmenu(event: MouseEvent) {
  event.preventDefault()

  if (event.shiftKey) return

  const menu = await Menu.new({
    items: [
      ...await getBaseMenu(),
      await PredefinedMenuItem.new({ item: 'Separator' }),
      ...await getExitMenu(),
    ],
  })

  if (isWindows && catStore.window.alwaysOnTop) {
    setAlwaysOnTop(false)
  }

  await menu.popup()

  if (!isWindows && catStore.window.alwaysOnTop) return

  setAlwaysOnTop(catStore.window.alwaysOnTop)
}

function handleScale(event: MouseEvent) {
  const { buttons, shiftKey, movementX, movementY } = event

  if (buttons !== 2 || !shiftKey) return

  const delta = (movementX + movementY) * 0.5
  const nextScale = Math.max(10, Math.min(catStore.window.scale + delta, 500))

  catStore.window.scale = round(nextScale)
}
</script>

<template>
  <div
    class="relative size-screen overflow-hidden"
    :class="{ '-scale-x-100': catStore.model.mirror }"
    :style="{
      opacity: catStore.window.opacity / 100,
      borderRadius: `${catStore.window.radius}%`,
    }"
    @contextmenu="handleContextmenu"
    @mousedown="handleMouseDown"
    @mousemove="handleScale"
  >
    <img
      v-if="currentStateReady && currentFrame"
      class="size-full object-contain"
      :src="currentFrameSrc"
      @load="handleImageLoad"
    >

    <div
      v-else
      class="size-full flex flex-col items-center justify-center gap-2 bg-black/82 p-4 text-center text-white"
    >
      <div class="i-solar:gallery-add-bold text-10" />
      <div class="font-bold text-sm">
        请先上传完整桌宠素材
      </div>
      <div class="leading-5 opacity-75 text-xs">
        当前状态缺少素材：{{ PET_STATE_LABELS[petFrameStore.activeState] }}
      </div>
    </div>
  </div>
</template>
