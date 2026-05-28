import { basename } from '@tauri-apps/api/path'

export const PET_STATE_IDS = ['idle', 'typing', 'click', 'mouse', 'sleep', 'random', 'space'] as const

export type PetStateId = typeof PET_STATE_IDS[number]

export interface PetStateAsset {
  id: PetStateId
  frames: string[]
  fps: number
  loop: boolean
}

export interface PetFramePackage {
  name: string
  version: number
  states: Record<PetStateId, PetStateAsset>
}

export const PET_STATE_LABELS: Record<PetStateId, string> = {
  idle: '待机',
  typing: '打字',
  click: '点击',
  mouse: '拖拽',
  sleep: '睡觉',
  random: '待机小动作',
  space: '空格弹跳',
}

export function createDefaultPetPackage(): PetFramePackage {
  const states = {} as Record<PetStateId, PetStateAsset>

  for (const id of PET_STATE_IDS) {
    states[id] = {
      id,
      frames: [],
      fps: 10,
      loop: id !== 'click' && id !== 'random' && id !== 'space',
    }
  }

  return {
    name: 'My Pet',
    version: 1,
    states,
  }
}

export function isPetStateId(value: string): value is PetStateId {
  return PET_STATE_IDS.includes(value as PetStateId)
}

export function isImageFrame(path: string) {
  return /\.(?:png|jpe?g|webp)$/i.test(path)
}

export function normalizeFrames(frames: string[]) {
  return [...frames]
    .filter(isImageFrame)
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }))
}

export async function getFrameFileName(path: string) {
  return basename(path).catch(() => path.split(/[\\/]/).pop() ?? path)
}

export function isPetPackageComplete(pack: PetFramePackage) {
  return PET_STATE_IDS.every(id => pack.states[id]?.frames.length > 0)
}

export function hasRenderableState(pack: PetFramePackage, stateId: PetStateId) {
  return pack.states[stateId]?.frames.length > 0
}

export function getMissingStateIds(pack: PetFramePackage) {
  return PET_STATE_IDS.filter(id => pack.states[id]?.frames.length === 0)
}
