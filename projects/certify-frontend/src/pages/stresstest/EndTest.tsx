import Loading from '@/components/Loading'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { StressTestingClient } from '@/contracts/StressTesting'
import { useDappState } from '@/providers/DappStateProvider'
import { StressTestGlobalStateType } from '@/types/types'
import { getBlockchainCurrentRound, getStressTestGlobalState } from '@/utils/blockclainUtils'
import { endStressTest } from '@/utils/method'
import { getEstRemainingTime } from '@/utils/utilFunctions'
import { useWallet } from '@txnlab/use-wallet'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

type TimerType = {
  min: number
  sec: number
}

const EndTestButton = ({
  timer,
  setTimer,
  isTestComplete,
  btnLoading,
  endTestFunc,
}: {
  timer: TimerType
  setTimer: React.Dispatch<React.SetStateAction<TimerType>>
  isTestComplete: boolean
  btnLoading: boolean
  endTestFunc: () => void
}) => {
  //Timer Countdown
  useEffect(() => {
    if (isTestComplete) {
      return
    }

    let countdown: string | number | NodeJS.Timeout | undefined
    if (timer.sec > 0 || timer.min > 0) {
      countdown = setInterval(() => {
        if (timer.sec > 0) {
          setTimer({ ...timer, sec: timer.sec - 1 })
        } else if (timer.min > 0) {
          setTimer({ min: timer.min - 1, sec: 59 })
        }
      }, 1000)
    }

    return () => {
      clearInterval(countdown)
    }
  }, [timer])

  return (
    <>
      <Button className="" disabled={!isTestComplete || btnLoading} onClick={endTestFunc}>
        {!isTestComplete ? (
          <span>
            {timer.min > 9 ? timer.min : `0${timer.min}`}:{timer.sec > 9 ? timer.sec : `0${timer.sec}`}
          </span>
        ) : (
          <>
            <Loading visible={btnLoading} />
            <span className="ml-2">End Test</span>
          </>
        )}
      </Button>
    </>
  )
}

const EndTest = ({ stressTestingId }: { stressTestingId: number }) => {
  const roundCheckInterval: number = 10000
  const { activeAddress, signer } = useWallet()
  const { algorandClient, certBoardClient } = useDappState()

  const navigate = useNavigate()

  const [isTestComplete, setIsTestComplete] = useState<boolean>(false)
  const [isTestEnded, setIsTestEnded] = useState<boolean>(false)
  const [pageLoading, setPageLoading] = useState<boolean>(false)
  const [btnLoading, setBtnLoading] = useState<boolean>(false)
  const [currentRound, setCurrentRound] = useState<number>(0)
  const [stGlobalState, setSTGlobalState] = useState<StressTestGlobalStateType>()
  const [apiCaller, setApiCaller] = useState<boolean>(false)
  const [progess, setProgress] = useState<number>(0)
  const [timer, setTimer] = useState<{ min: number; sec: number }>({ min: 5, sec: 0 })

  const stressTestingClient = new StressTestingClient(
    {
      resolveBy: 'id',
      id: Number(stressTestingId),
    },
    algorandClient.client.algod,
  )

  //Initializing
  useEffect(() => {
    const fetchRound = async () => {
      setPageLoading(true)
      const round = await getBlockchainCurrentRound(algorandClient)
      const gs = await getStressTestGlobalState(stressTestingClient)
      setSTGlobalState(gs)
      setCurrentRound(round)

      const [min, sec] = getEstRemainingTime(round, gs!.roundEndMax)
      setTimer({ min, sec })
      setPageLoading(false)
      setApiCaller(true)
    }

    fetchRound()
  }, [])

  //Fetching Current Round
  useEffect(() => {
    let currentRoundCheck: NodeJS.Timeout | undefined

    if (stGlobalState != undefined) {
      currentRoundCheck = setTimeout(async () => {
        const round = await getBlockchainCurrentRound(algorandClient)

        if (round >= stGlobalState!.roundEndMax || isTestComplete) {
          setProgress(100)
          clearInterval(currentRoundCheck)
          return setIsTestComplete(true)
        }

        setProgress(Math.floor(((round - stGlobalState!.roundCreated) / (stGlobalState!.roundEndMax - stGlobalState!.roundCreated)) * 100))
        const [min, sec] = getEstRemainingTime(round, stGlobalState!.roundEndMax)
        if ((timer.min == 0 && timer.sec < 20) || (min == 0 && sec < 15)) {
          setTimer({ min: 0, sec: 40 })
        } else {
          setTimer({ min, sec })
        }

        setCurrentRound(round)
        setApiCaller(!apiCaller)
      }, roundCheckInterval)
    }

    return () => clearTimeout(currentRoundCheck)
  }, [stGlobalState, apiCaller])

  async function onEndTest() {
    setBtnLoading(true)
    await endStressTest(algorandClient, certBoardClient, stressTestingClient, stressTestingId, signer)
    setIsTestEnded(true)
    setBtnLoading(false)
    toast('Test Completed', {
      description: 'Stress Test ended successfully.',
      action: {
        label: 'Verify',
        onClick: () => navigate(`verify/${stressTestingId}/${activeAddress}`),
      },
    })
  }

  return (
    <>
      {pageLoading ? (
        <div>
          <div className="ml-2 flex gap-4 items-center">
            <Loading visible={true} />
            <div>
              <h1 className="font-bold">Starting Stress Test</h1>
              <p>Please wait</p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex gap-2 items-center justify-between">
            <h1 className="font-bold text-lg">Stress Test started successfully.</h1>
            <Badge variant={'outline'} className="">
              Test ID: {stressTestingId}
            </Badge>
          </div>
          <p className="text-sm">Please wait, while the stress is running. You will be able to end the test, once it is complete.</p>

          <div className="mt-2">
            <Badge variant={'secondary'} className="mt-6 space-x-2">
              {' '}
              <Loading visible={!isTestComplete} />
              <span>Status :</span>
              {isTestComplete ? <span>Completed</span> : <span>Running</span>}
            </Badge>
          </div>
          <div className="w-full">
            <div className="w-full flex justify-between  gap-6 mt-4">
              <div className="flex flex-col items-start">
                <h1 className="font-semibold text-sm">Round Created:</h1>
                <p className="text-sm">{stGlobalState?.roundCreated}</p>
              </div>
              <div className="flex flex-col items-end">
                <h1 className="font-semibold text-sm">Round Ended:</h1>
                <p className="text-sm">{stGlobalState?.roundEndMax}</p>
              </div>
            </div>
            <Progress className="mt-2" value={progess} />
          </div>
          <div className="mt-4 flex gap-1">
            <h1 className="font-semibold text-sm">Current Round:</h1>
            <p className="text-sm">{currentRound}</p>
          </div>
          <div className="mt-10 flex w-full justify-center">
            {!isTestEnded ? (
              <EndTestButton
                timer={timer}
                setTimer={setTimer}
                isTestComplete={isTestComplete}
                btnLoading={btnLoading}
                endTestFunc={onEndTest}
              />
            ) : (
              <div>
                <Button onClick={() => navigate(`/verify/${stressTestingId}/${activeAddress}`)}>Verify On-Chain</Button>
              </div>
            )}
          </div>
          <div className="mt-6 flex justify-center">
            <p className="text-xs">
              Please Note: The timer shows an estimated time. The test will be completed once the current-round reaches end-round.
            </p>
          </div>
        </div>
      )}
    </>
  )
}

export default EndTest
