const SPACE_KEY_VALUES = new Set([
  'Space',
  'Spacebar',
  'KeySpace',
  'Unknown(49)',
])

export function isSpaceKey(value: string) {
  return SPACE_KEY_VALUES.has(value)
}
