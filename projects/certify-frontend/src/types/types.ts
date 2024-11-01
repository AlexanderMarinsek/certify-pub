export interface CertBoardGlobalStateType {
  blockedAlgo: number
  certificateFee: number
  maxTestBlocking: number
  maxTestDuration: number
  paymentAsset: number
  plaManager: string
  stakeMax: number
  stakeMin: number
  state: string
  stressTestFeeRound: number
  expectedConsensusRate: number
}

export interface StressTestGlobalStateType {
  userAddress: string
  ownerAddress: string
  stake: number
  duration: number
  durationMax: number
  roundCreated: number
  roundStart: number
  roundEnd: number
  roundEnded: number
  roundEndMax: number
  lastBlock: number
  cntProducedBlocks: number
  totalStakeSum: number
  cntTotalStakeSum: number
  state: string
}
