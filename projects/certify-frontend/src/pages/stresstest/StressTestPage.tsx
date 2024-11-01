import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { useWallet } from '@txnlab/use-wallet'
import { useState } from 'react'
import CreateTestForm from './CreateTestForm'
import StartTestForm from './StartTestForm'
import ConnectWalletCard from '@/components/ConnectWalletCard'
import EndTest from './EndTest'

const StressTestPage = () => {
  const { activeAddress } = useWallet()
  const [cardState, setCardState] = useState<number>(0)
  const [stressTestingId, setStressTestingId] = useState<number>(0)

  function createTestCallback(appId: bigint) {
    setStressTestingId(Number(appId))
    setCardState(1)
  }

  return (
    <>
      <div className="flex justify-center ">
        <div className="w-full lg:w-[850px] max-w-[850px]">
          <div className="mb-6">
            <h1 className="text-xl font-bold">Self-Stress Test</h1>
            <p className="text-sm">Prove you are an excellent node runner, without having to large stake yourself.</p>
          </div>
          {!activeAddress ? (
            <ConnectWalletCard />
          ) : (
            <>
              {cardState == 0 && (
                <Card>
                  <CardHeader></CardHeader>
                  <CardContent>
                    <CreateTestForm callback={createTestCallback} />
                  </CardContent>
                </Card>
              )}
              {cardState == 1 && (
                <Card>
                  <CardHeader></CardHeader>
                  <CardContent>
                    <StartTestForm stressTestingId={stressTestingId} callback={() => setCardState(2)} />
                  </CardContent>
                </Card>
              )}
              {cardState == 2 && (
                <Card>
                  <CardHeader></CardHeader>
                  <CardContent>
                    <EndTest stressTestingId={stressTestingId} />
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default StressTestPage
