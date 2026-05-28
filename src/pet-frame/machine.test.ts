/* eslint-disable test/no-import-node-test */
import assert from 'node:assert/strict'
import { describe, it } from 'node:test'

import { createPetStateMachine } from './machine'

describe('pet state machine', () => {
  it('uses pet click as a one-shot priority state and then returns to current behavior', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.current, 'idle')
    assert.equal(machine.send('keyboard_active'), 'typing')
    assert.equal(machine.send('pet_click'), 'click')
    assert.equal(machine.finishOneShot(), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
  })

  it('sleeps after inactivity and wakes on user input', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('inactive_timeout'), 'sleep')
    assert.equal(machine.send('mouse_move'), 'idle')
    assert.equal(machine.send('mouse_idle'), 'idle')
  })

  it('plays random as a one-shot idle animation only while idle', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('keyboard_active'), 'typing')
    assert.equal(machine.send('random_tick'), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.finishOneShot(), 'idle')
  })

  it('lets user input interrupt a random idle action', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.send('keyboard_active'), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.send('mouse_move'), 'idle')
  })

  it('keeps click visually locked while recording current behavior for settle', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('pet_click'), 'click')
    assert.equal(machine.send('keyboard_active'), 'click')
    assert.equal(machine.finishOneShot(), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
  })

  it('treats non-pet mouse clicks as activity without a dedicated visual state', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('mouse_click'), 'idle')
    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.send('mouse_click'), 'idle')
    assert.equal(machine.send('mouse_idle'), 'idle')
  })

  it('lets an idle random action finish into sleep if inactivity times out while it plays', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.send('inactive_timeout'), 'random')
    assert.equal(machine.finishOneShot(), 'sleep')
    assert.equal(machine.send('random_tick'), 'sleep')
  })

  it('uses the mouse state as a drag lock and settles to idle on release', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('drag_start'), 'mouse')
    assert.equal(machine.send('random_tick'), 'mouse')
    assert.equal(machine.send('mouse_move'), 'mouse')
    assert.equal(machine.send('drag_end'), 'idle')
  })

  it('records keyboard input during drag and settles to typing on release', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('drag_start'), 'mouse')
    assert.equal(machine.send('keyboard_active'), 'mouse')
    assert.equal(machine.send('drag_end'), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
  })

  it('wakes from sleep into drag and returns to idle when released', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('inactive_timeout'), 'sleep')
    assert.equal(machine.send('drag_start'), 'mouse')
    assert.equal(machine.send('drag_end'), 'idle')
  })

  it('plays space as a one-shot action and then returns to idle', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('space_press'), 'space')
    assert.equal(machine.finishOneShot(), 'idle')
  })

  it('records normal typing during space and settles to typing after the jump', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('space_press'), 'space')
    assert.equal(machine.send('keyboard_active'), 'space')
    assert.equal(machine.finishOneShot(), 'typing')
    assert.equal(machine.send('keyboard_idle'), 'idle')
  })

  it('lets space interrupt random and wake from sleep', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('random_tick'), 'random')
    assert.equal(machine.send('space_press'), 'space')
    assert.equal(machine.finishOneShot(), 'idle')
    assert.equal(machine.send('inactive_timeout'), 'sleep')
    assert.equal(machine.send('space_press'), 'space')
    assert.equal(machine.finishOneShot(), 'idle')
  })

  it('keeps drag visually locked over space', () => {
    const machine = createPetStateMachine()

    assert.equal(machine.send('drag_start'), 'mouse')
    assert.equal(machine.send('space_press'), 'mouse')
    assert.equal(machine.send('drag_end'), 'idle')
  })
})
