/* eslint-disable test/no-import-node-test */
import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import { isSpaceKey } from './deviceKey'

describe('device key helpers', () => {
  it('detects common native space key names', () => {
    assert.equal(isSpaceKey('Space'), true)
    assert.equal(isSpaceKey('Spacebar'), true)
    assert.equal(isSpaceKey('KeySpace'), true)
    assert.equal(isSpaceKey('Unknown(49)'), true)
  })

  it('does not treat normal typing keys as space', () => {
    assert.equal(isSpaceKey('A'), false)
    assert.equal(isSpaceKey('KeyA'), false)
    assert.equal(isSpaceKey('Enter'), false)
  })
})
