import type { PetStateId } from './states'

export type PetActivityEvent
  = | 'keyboard_active'
    | 'keyboard_idle'
    | 'mouse_move'
    | 'mouse_idle'
    | 'mouse_click'
    | 'pet_click'
    | 'drag_start'
    | 'drag_end'
    | 'inactive_timeout'
    | 'wake'
    | 'random_tick'

export interface PetStateMachine {
  readonly current: PetStateId
  send: (event: PetActivityEvent) => PetStateId
  finishOneShot: () => PetStateId
}

export function createPetStateMachine(): PetStateMachine {
  let current: PetStateId = 'idle'
  let keyboardActive = false
  let inactive = false
  let dragging = false

  function setLoopingState(next: PetStateId) {
    current = next

    return current
  }

  function settle() {
    if (keyboardActive) return setLoopingState('typing')
    if (inactive) return setLoopingState('sleep')

    return setLoopingState('idle')
  }

  function setUserActive() {
    inactive = false
  }

  function recordEvent(event: PetActivityEvent) {
    switch (event) {
      case 'keyboard_active':
        keyboardActive = true
        setUserActive()
        break
      case 'keyboard_idle':
        keyboardActive = false
        break
      case 'mouse_click':
      case 'mouse_move':
      case 'drag_start':
        setUserActive()
        break
      case 'drag_end':
      case 'mouse_idle':
        break
      case 'inactive_timeout':
        keyboardActive = false
        inactive = true
        break
      case 'wake':
        setUserActive()
        break
      case 'pet_click':
      case 'random_tick':
        break
    }
  }

  return {
    get current() {
      return current
    },
    send(event) {
      if (event === 'drag_start') {
        dragging = true
        setUserActive()
        current = 'mouse'

        return current
      }

      if (event === 'drag_end') {
        dragging = false

        return settle()
      }

      if (dragging) {
        recordEvent(event)

        return current
      }

      if (event === 'pet_click') {
        setUserActive()
        current = 'click'

        return current
      }

      if (current === 'click') {
        recordEvent(event)

        return current
      }

      if (current === 'random') {
        recordEvent(event)

        if (event === 'keyboard_active' || event === 'mouse_click' || event === 'mouse_move') {
          return settle()
        }

        return current
      }

      switch (event) {
        case 'keyboard_active':
          keyboardActive = true
          setUserActive()

          return setLoopingState('typing')
        case 'keyboard_idle':
          keyboardActive = false

          return settle()
        case 'mouse_click':
        case 'mouse_move':
          setUserActive()

          return settle()
        case 'mouse_idle':
          return settle()
        case 'inactive_timeout':
          keyboardActive = false
          inactive = true

          return setLoopingState('sleep')
        case 'wake':
          setUserActive()

          return settle()
        case 'random_tick':
          if (current !== 'idle') return current

          current = 'random'

          return current
      }
    },
    finishOneShot() {
      if (current !== 'click' && current !== 'random') return current

      return settle()
    },
  }
}
