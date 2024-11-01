import { certBoardAppID } from '@/certBoardAppID'
import { CertBoardClient } from '@/contracts/CertBoard'
import * as algokit from '@algorandfoundation/algokit-utils'
import { microAlgos } from '@algorandfoundation/algokit-utils'
import { ABIAddressType, ABITupleType, ABIUintType, TransactionSigner, getApplicationAddress } from 'algosdk'
import { BR_STRESS_TESTING_CONTRACT, MBR_CRET_BOX, MBR_STRESS_BOX } from './constants'
import { StressTestingClient } from '@/contracts/StressTesting'
import { toBytesBigInt } from './utilFunctions'
import { getStressTestGlobalState } from './blockclainUtils'

type CreateTestResponse = {
  appId?: bigint
  error: boolean
  errorMsg?: string
}

type StartTestResponse = {
  error: boolean
  errorMsg?: string
}

type AttestResponse = StartTestResponse

export async function createStressTest(
  algorand: algokit.AlgorandClient,
  cbClient: CertBoardClient,
  stake: bigint,
  duration: bigint,
  durationMax: bigint,
  userAddress: string,
  signer: TransactionSigner,
): Promise<CreateTestResponse> {
  const algodClient = algorand.client.algod
  const certBoardAppAddress = getApplicationAddress(certBoardAppID)
  const cbGlobalState = await cbClient.getGlobalState()

  //Duration Check
  if (duration >= durationMax) return { error: true, errorMsg: 'Test Duration must be lesser than Max Duration' }

  const expectedConsensusRate = cbGlobalState.expectedConsensusRate!.asBigInt()
  if (duration < expectedConsensusRate)
    return { error: true, errorMsg: `Test Duration must be more than Expected Consensus Rate: ${expectedConsensusRate} ` }

  //Stake Check
  const stakeMin = cbGlobalState.stakeMin!.asBigInt()
  const stakeMax = cbGlobalState.stakeMax!.asBigInt()
  if (stake < stakeMin || stake > stakeMax)
    return { error: true, errorMsg: `Stake amount must be between ${Number(stakeMin)} and ${Number(stakeMax)}` }

  const blockedAlgo = cbGlobalState.blockedAlgo!.asBigInt()
  const accountInfo = await algodClient.accountInformation(certBoardAppAddress).do()
  if (blockedAlgo > accountInfo.balance - accountInfo.minBalance) return { error: true, errorMsg: `App doesn't have enough fund.` }

//  //Sending Algos to CertBoard to Stake
//  const res = await algorand.send.payment({
//    sender: userAddress,
//    receiver: certBoardAppAddress,
//    amount: microAlgos(Number(stake)),
//    signer,
//  })
//
//  console.log('Stake Amount has been sent to contract.') //checking if transaction is successful

  // Getting GlobalState
  const stressTestFeeAmt = cbGlobalState.stressTestFeeRound!.asNumber() * Number(durationMax)

  // Fee Transaction
  const txn = await algorand.transactions.payment({
    sender: userAddress,
    receiver: certBoardAppAddress,
    amount: microAlgos(stressTestFeeAmt),
    signer,
  })

  //Payment due to MBR Increase [Online Fee, Potential Reward Loss]
  const potentialLoss = cbGlobalState.expectedConsensusRate!.asNumber() * Number(stake) * Number(durationMax)

  const amount = potentialLoss + BR_STRESS_TESTING_CONTRACT

  const algoTxn = await algorand.transactions.payment({
    sender: userAddress,
    receiver: certBoardAppAddress,
    amount: microAlgos(amount),
    signer,
  })

  //Fee Adjustment
  const txnParams = await algodClient.getTransactionParams().do()
  txnParams.flatFee = true
  txnParams.fee = 2 * txnParams.minFee

  //Calling `stress_create`
  try {
    const response = await cbClient.stressCreate(
      {
        stake,
        duration,
        durationMax,
        algoTxn,
        txn,
      },
      {
        sender: {
          addr: userAddress,
          signer: signer,
        },
        sendParams: { fee: microAlgos(txnParams.fee) },
      },
    )

    return { appId: response.return, error: false }
  } catch (err) {
    return { error: true, errorMsg: 'Smart contract failed to execute.' }
  }
}

export async function startStressTest(
  algorand: algokit.AlgorandClient,
  cbClient: CertBoardClient,
  stClient: StressTestingClient,
  userAddress: string,
  stressTestId: bigint,
  voteKeyDilution: bigint,
  votePk: Uint8Array,
  selectionPk: Uint8Array,
  stateProofPk: Uint8Array,
  signer: TransactionSigner,
): Promise<StartTestResponse> {
  try {
    const algodClient = algorand.client.algod
    const certBoardAppAddress = getApplicationAddress(certBoardAppID)
    const stressTestingAppAddress = getApplicationAddress(stressTestId)
    const stGlobleState = await stClient.getGlobalState()

    //Getting Valid Rounds
    const voteFirst = stGlobleState.roundCreated!.asBigInt()
    const voteLast = stGlobleState.roundEndMax!.asBigInt()

    const encodedUserAddress = new ABIAddressType().encode(userAddress)
    const testIdBytes = toBytesBigInt(stressTestId, 8)

    const boxName = new Uint8Array([...encodedUserAddress, ...testIdBytes])
    const boxes = [
      {
        appIndex: 0,
        name: boxName,
      },
    ]
    const foreignApps = [Number(stressTestId)]

    const mbrTxn = await algorand.transactions.payment({
      sender: userAddress,
      receiver: certBoardAppAddress,
      amount: microAlgos(MBR_STRESS_BOX),
      signer,
    })

    //Fees Adjustment
    const txnParams = await algodClient.getTransactionParams().do()
    txnParams.flatFee = true
    txnParams.fee = 4 * txnParams.minFee

    //Creating KeyRegTxnInfo
    await cbClient.stressStart(
      {
        stressTestId,
        keyRegInfo: [voteFirst, voteLast, voteKeyDilution, votePk, selectionPk, stateProofPk, stressTestingAppAddress],
        mbrTxn,
      },
      {
        sender: {
          addr: userAddress,
          signer: signer,
        },
        boxes,
        apps: foreignApps,
        sendParams: { fee: microAlgos(txnParams.fee) },
      },
    )

    return { error: false }
  } catch (err) {
    return { error: true, errorMsg: 'Smart contract failed to execute.' }
  }
}

export async function endStressTest(
  algorand: algokit.AlgorandClient,
  cbClient: CertBoardClient,
  stClient: StressTestingClient,
  stressTestId: number,
  signer: TransactionSigner,
) {
  const algod = algorand.client.algod

  const gs = await getStressTestGlobalState(stClient)

  const encodedUserAddress = new ABIAddressType().encode(gs!.userAddress)
  const stressTestIdBytes = toBytesBigInt(BigInt(stressTestId), 8)
  const boxName = new Uint8Array([...encodedUserAddress, ...stressTestIdBytes])
  const boxes = [
    {
      appIndex: 0,
      name: boxName,
    },
  ]
  const foreignApps = [Number(stressTestId)]

  //Fee Adjust
  const txnParams = await algod.getTransactionParams().do()
  txnParams.fee = 3 * txnParams.minFee
  txnParams.flatFee = true

  await cbClient.stressEnd(
    { userAddress: gs!.userAddress, stressTestId: stressTestId },
    {
      sender: {
        addr: gs!.userAddress,
        signer,
      },
      boxes,
      apps: foreignApps,
      sendParams: { fee: microAlgos(txnParams.fee) },
    },
  )

  console.log('Test Ended')
}

export async function certBoard_Attest(
  algorand: algokit.AlgorandClient,
  cbClient: CertBoardClient,
  issuerAddress: string,
  recipient: string,
  info: Uint8Array,
  signer: TransactionSigner,
): Promise<AttestResponse> {
  //Getting the AlgodClient
  const algodClient = algorand.client.algod
  const certBoardAppAddress = getApplicationAddress(certBoardAppID)

  //Making an MBR Transaction
  const mbr_txn = await algorand.transactions.payment({
    sender: issuerAddress,
    receiver: certBoardAppAddress,
    amount: microAlgos(MBR_CRET_BOX),
    signer,
  })

  //Getting the Certification Fees from Contract Global State
  const globleState = await cbClient.getGlobalState()
  const certificationFees = globleState.certificateFee!.asNumber()

  //Fees Transaction
  //Note: For starters this is fine. In future, it needs to be checked if acceptable payment
  //      on CertBoard (globleState.paymentAsset) is not ALGO (!=0) but an ASA.

  const fee_txn = await algorand.transactions.payment({
    sender: issuerAddress,
    receiver: certBoardAppAddress,
    amount: microAlgos(certificationFees),
    signer,
  })

  //Calling the Smart Contract
  const txnParams = await algodClient.getTransactionParams().do()
  txnParams.flatFee = true
  txnParams.fee = 2 * txnParams.minFee

  const encodedRecipient = new ABIAddressType().encode(recipient)
  const encodedIssuer = new ABIAddressType().encode(issuerAddress)
  const boxName = new Uint8Array([...encodedRecipient, ...encodedIssuer])
  const boxes = [
    {
      appIndex: 0,
      name: boxName,
    },
  ]

  try {
    await cbClient.certCreate(
      {
        recipient,
        info,
        mbrTxn: mbr_txn,
        txn: fee_txn,
      },
      {
        sender: {
          addr: issuerAddress,
          signer: signer,
        },
        boxes: boxes,
        sendParams: { fee: microAlgos(txnParams.fee) },
      },
    )
    return { error: false }
  } catch (err) {
    return { error: true, errorMsg: 'Failed to Attest' }
  }
}

export async function certBoard_VerifyByIssuer(algorand: algokit.AlgorandClient, issuerAddress: string, validatorAddress: string) {
  try {
    const algodClient = algorand.client.algod

    const encodedRecipient = new ABIAddressType().encode(validatorAddress)
    const encodedIssuer = new ABIAddressType().encode(issuerAddress)
    const boxName = new Uint8Array([...encodedRecipient, ...encodedIssuer])

    const boxData = await algodClient.getApplicationBoxByName(certBoardAppID, boxName).do()
    const info = new TextDecoder().decode(boxData.value)
    return info
  } catch (err) {
    return '404: Not Found'
  }
}

export async function certBoard_VerifyByTestId(algorand: algokit.AlgorandClient, testId: number, validatorAddress: string) {
  try {
    const algodClient = algorand.client.algod
    const encodedValidatorAddress = new ABIAddressType().encode(validatorAddress)
    const testIdBytes = toBytesBigInt(BigInt(testId), 8)
    const boxName = new Uint8Array([...encodedValidatorAddress, ...testIdBytes])
    const boxData = await algodClient.getApplicationBoxByName(certBoardAppID, boxName).do()

    const stressTestInfo = new ABITupleType([
      new ABIUintType(64),
      new ABIUintType(64),
      new ABIUintType(64),
      new ABIUintType(64),
      new ABIUintType(64),
    ])
    const decodedStressTestInfo = stressTestInfo.decode(boxData.value)

    const resObject = {
      avrOnlineStake: decodedStressTestInfo[0].toString(),
      cntProducedBlock: decodedStressTestInfo[1].toString(),
      roundStart: decodedStressTestInfo[2].toString(),
      roundEnd: decodedStressTestInfo[3].toString(),
      stake: decodedStressTestInfo[4].toString(),
    }

    return JSON.stringify(resObject, null, 2)
  } catch (err) {
    console.error(err)
    return '404: Not Found'
  }
}
