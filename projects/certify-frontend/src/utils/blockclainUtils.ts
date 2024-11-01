import { CertBoardClient } from '@/contracts/CertBoard'
import { StressTestingClient } from '@/contracts/StressTesting'
import { CertBoardGlobalStateType, StressTestGlobalStateType } from '@/types/types'
import * as algosdk from 'algosdk'
import * as algokit from '@algorandfoundation/algokit-utils'

export async function getCertBoardGlobalState(cbClient: CertBoardClient): Promise<CertBoardGlobalStateType | undefined> {
  try {
    const gs = await cbClient.getGlobalState()

    return {
      blockedAlgo: gs.blockedAlgo!.asNumber(),
      certificateFee: gs.certificateFee!.asNumber(),
      maxTestBlocking: gs.maxTestBlocking!.asNumber(),
      maxTestDuration: gs.maxTestDuration!.asNumber(),
      paymentAsset: gs.paymentAsset!.asNumber(),
      plaManager: new algosdk.ABIAddressType().decode(gs.plaManager!.asByteArray()),
      stakeMax: gs.stakeMax!.asNumber(),
      stakeMin: gs.stakeMin!.asNumber(),
      state: gs.state!.asString(),
      stressTestFeeRound: gs.stressTestFeeRound!.asNumber(),
      expectedConsensusRate: gs.expectedConsensusRate!.asNumber(),
    }
  } catch (err) {
    console.error(`Failed to fetch CertBoad Global-State`)
    return undefined
  }
}

export async function getStressTestGlobalState(stClient: StressTestingClient): Promise<StressTestGlobalStateType | undefined> {
  try {
    const gs = await stClient.getGlobalState()
    return {
      userAddress: algosdk.encodeAddress(gs.userAddress!.asByteArray()),
      ownerAddress: algosdk.encodeAddress(gs.ownerAddress!.asByteArray()),
      stake: gs.stake!.asNumber(),
      duration: gs.duration!.asNumber(),
      durationMax: gs.durationMax!.asNumber(),
      roundCreated: gs.roundCreated!.asNumber(),
      roundStart: gs.roundStart!.asNumber(),
      roundEnd: gs.roundEnd!.asNumber(),
      roundEnded: gs.roundEnded!.asNumber(),
      roundEndMax: gs.roundEndMax!.asNumber(),
      lastBlock: gs.lastBlock!.asNumber(),
      cntProducedBlocks: gs.cntProducedBlocks!.asNumber(),
      totalStakeSum: gs.totalStakeSum!.asNumber(),
      cntTotalStakeSum: gs.cntTotalStakeSum!.asNumber(),
      state: algosdk.encodeAddress(gs.state!.asByteArray()),
    }
  } catch (err) {
    console.error(`Failed to fetch Stress Test Global-State`)
    console.log(err)
    return undefined
  }
}

export async function getBlockchainCurrentRound(algorand: algokit.AlgorandClient): Promise<number> {
  const algod = algorand.client.algod

  const status = await algod.status().do()
  return status['last-round']
}



