import { appDataDir } from '@tauri-apps/api/path'
import { copyFile, mkdir, remove, writeTextFile } from '@tauri-apps/plugin-fs'
import { nanoid } from 'nanoid'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { PetFramePackage, PetStateId } from '@/pet-frame/states'

import {
  createDefaultPetPackage,
  isPetPackageComplete,
  normalizeFrames,
} from '@/pet-frame/states'
import { join } from '@/utils/path'

function createDemoFrames(stateName: string, length: number) {
  const directoryName = stateName.endsWith('-hit') ? stateName : `${stateName}-clean`

  return Array.from(
    { length },
    (_, index) => `/pet-preview/${directoryName}/${String(index + 1).padStart(3, '0')}.png`,
  )
}

const DEMO_DOG_FRAMES: Record<PetStateId, string[]> = {
  idle: createDemoFrames('idle-hit', 1),
  typing: createDemoFrames('typing-loop-hit', 6),
  click: createDemoFrames('click-hit', 4),
  mouse: createDemoFrames('drag-loop-hit', 6),
  sleep: createDemoFrames('sleep-hit', 6),
  random: createDemoFrames('random-hit', 9),
}

const DEMO_DOG_OPTIONS: Record<PetStateId, { fps: number, loop: boolean }> = {
  idle: { fps: 8, loop: true },
  typing: { fps: 10, loop: true },
  click: { fps: 12, loop: false },
  mouse: { fps: 10, loop: true },
  sleep: { fps: 6, loop: true },
  random: { fps: 10, loop: false },
}

export const usePetFrameStore = defineStore('pet-frame', () => {
  const pack = ref<PetFramePackage>(createDefaultPetPackage())
  const activeState = ref<PetStateId>('idle')

  const complete = computed(() => isPetPackageComplete(pack.value))

  async function persistManifest() {
    const dir = join(await appDataDir(), 'pet-frame-package')

    await mkdir(dir, { recursive: true })
    await writeTextFile(join(dir, 'manifest.json'), JSON.stringify(pack.value, null, 2))
  }

  async function replaceStateFrames(stateId: PetStateId, sourcePaths: string[]) {
    const frames = normalizeFrames(sourcePaths)

    if (frames.length === 0) {
      pack.value.states[stateId].frames = []
      await persistManifest()

      return
    }

    const root = join(await appDataDir(), 'pet-frame-package')
    const stateDir = join(root, stateId)

    await remove(stateDir, { recursive: true }).catch(() => {})
    await mkdir(stateDir, { recursive: true })

    const copiedFrames: string[] = []

    for (const [index, fromPath] of frames.entries()) {
      const ext = fromPath.match(/\.[^.\\/]+$/)?.[0] ?? '.png'
      const toPath = join(stateDir, `${String(index + 1).padStart(3, '0')}-${nanoid(6)}${ext}`)

      await copyFile(fromPath, toPath)
      copiedFrames.push(toPath)
    }

    pack.value.states[stateId].frames = copiedFrames
    await persistManifest()
  }

  async function clearStateFrames(stateId: PetStateId) {
    pack.value.states[stateId].frames = []
    await remove(join(await appDataDir(), 'pet-frame-package', stateId), { recursive: true }).catch(() => {})
    await persistManifest()
  }

  async function ensureDemoTypingFrames() {
    const states = pack.value.states
    let changed = false

    for (const [stateId, demoFrames] of Object.entries(DEMO_DOG_FRAMES) as [PetStateId, string[]][]) {
      const currentFrames = states[stateId].frames
      const expectedDemoDir = demoFrames[0]?.match(/\/pet-preview\/([^/]+)\//)?.[1]
      const hasFrames = currentFrames.length > 0
      const usesOldDemoPath = currentFrames.some(frame =>
        frame.includes('/public/pet-preview/')
        || frame.includes('/Users/yangpanyi/')
        || frame.includes('/public/pet-preview/typing/'))
      const isIdleUsingTypingDemo = stateId === 'idle' && currentFrames.some(frame => frame.includes('/typing-clean/'))
      const isTypingUsingPreviousDemo = stateId === 'typing' && currentFrames.some(frame =>
        frame.includes('/typing-clean/')
        || frame.includes('/typing-pixel-clean/')
        || frame.includes('/typing-sequence-clean/'))
      const isIdleUsingPreviousDemo = stateId === 'idle' && currentFrames.length !== demoFrames.length
      const isOutdatedDemo = currentFrames.some(frame =>
        frame.includes('/pet-preview/')
        && expectedDemoDir
        && !frame.includes(`/pet-preview/${expectedDemoDir}/`))

      if (!hasFrames || usesOldDemoPath || isIdleUsingTypingDemo || isTypingUsingPreviousDemo || isIdleUsingPreviousDemo || isOutdatedDemo) {
        states[stateId].frames = demoFrames
        states[stateId].fps = DEMO_DOG_OPTIONS[stateId].fps
        states[stateId].loop = DEMO_DOG_OPTIONS[stateId].loop
        changed = true
      }
    }

    if (!changed) return

    await persistManifest()
  }

  return {
    pack,
    activeState,
    complete,
    persistManifest,
    replaceStateFrames,
    clearStateFrames,
    ensureDemoTypingFrames,
  }
}, {
  tauri: {
    filterKeys: ['activeState'],
  },
})
