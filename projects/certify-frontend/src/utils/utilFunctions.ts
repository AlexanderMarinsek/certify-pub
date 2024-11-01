export function toBytesBigInt(value: bigint, byteLength: number): Uint8Array {
  const bytes = new Uint8Array(byteLength)
  for (let i = byteLength - 1; i >= 0; i--) {
    bytes[i] = Number(value & BigInt(0xff))
    value >>= BigInt(8)
  }
  return bytes
}

export function getEstRemainingTime(currentRound: number, roundEndMax: number): [number, number] {
  const estSec = Math.ceil((roundEndMax - currentRound) * 3.3)
  const min = Math.floor(estSec / 60)
  const sec = estSec % 60

  return [min, sec]
}