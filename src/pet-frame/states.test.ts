/* eslint-disable test/no-import-node-test */
import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import {
  createDefaultPetPackage,
  hasRenderableState,
  isPetPackageComplete,
  normalizeFrames,
  PET_STATE_IDS,
} from './states'

describe('pet frame package', () => {
  it('requires all fixed states to have at least one image frame', () => {
    const pack = createDefaultPetPackage()

    assert.deepEqual(PET_STATE_IDS, ['idle', 'typing', 'click', 'mouse', 'sleep', 'random', 'space'])
    assert.equal(isPetPackageComplete(pack), false)

    for (const stateId of PET_STATE_IDS) {
      pack.states[stateId].frames = [`/${stateId}/001.png`]
    }

    assert.equal(isPetPackageComplete(pack), true)
  })

  it('sorts image frames by file name and rejects non-image assets', () => {
    const frames = normalizeFrames([
      '/pet/typing/003.webp',
      '/pet/typing/readme.txt',
      '/pet/typing/001.png',
      '/pet/typing/002.jpg',
    ])

    assert.deepEqual(frames, [
      '/pet/typing/001.png',
      '/pet/typing/002.jpg',
      '/pet/typing/003.webp',
    ])
  })

  it('allows one configured state to render before the full package is complete', () => {
    const pack = createDefaultPetPackage()

    pack.states.typing.frames = ['/typing/001.png']

    assert.equal(isPetPackageComplete(pack), false)
    assert.equal(hasRenderableState(pack, 'typing'), true)
    assert.equal(hasRenderableState(pack, 'idle'), false)
  })
})
