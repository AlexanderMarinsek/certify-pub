import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ChevronRight } from 'lucide-react'
import { FormError, FormFieldError } from '@/components/FormErrors'
import { useEffect, useState } from 'react'
import { createStressTest } from '@/utils/method'
import { useWallet } from '@txnlab/use-wallet'
import { useDappState } from '@/providers/DappStateProvider'
import Loading from '@/components/Loading'
import { getCertBoardGlobalState } from '@/utils/blockclainUtils'
import { BR_STRESS_TESTING_CONTRACT } from '@/utils/constants'
import AlgorandUnitLogo from '@/components/AlgorandUnitLogo'
import { Separator } from '@/components/ui/separator'
import ActiveWalletBadge from '@/components/ActiveWalletBadge'
import { CertBoardGlobalStateType } from '@/types/types'

const formSchema = z.object({
  stake: z.number({ invalid_type_error: 'Stake Amount must be a Number', message: 'Invalid stake amount' }),
  duration: z.number({ message: 'Invalid duration value' }),
  durationMax: z.number({ message: 'Invalid max duration value' }),
})

type FormData = z.infer<typeof formSchema>

const CreateTestForm = ({ callback }: { callback: (appId: bigint) => void }) => {
  const { activeAddress, signer } = useWallet()
  const { algorandClient, certBoardClient } = useDappState()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(formSchema) })

  const [error, setError] = useState<{ active: boolean; message: string }>({ active: false, message: '' })
  const [loading, setLoading] = useState<boolean>(false)
  const [cbGlobalState, setCBGlobalState] = useState<CertBoardGlobalStateType | undefined>()
  const [stake, setStake] = useState<number>(0)
  const [duration, setDuration] = useState<number>(0)
  const [durationMax, setDurationMax] = useState<number>(0)
  const [expectedTotalAmt, setExpectedTotalAmt] = useState<number>()

  useEffect(() => {
    const fetchGS = async () => {
      setLoading(true)
      const gs = await getCertBoardGlobalState(certBoardClient)
      setCBGlobalState(gs)
      setLoading(false)
    }

    fetchGS()
  }, [])


  //Calculating Expected Amount
  useEffect(() => {
    if (cbGlobalState === undefined) return

    const stressTestFeeAmt = cbGlobalState.stressTestFeeRound * Number(durationMax)
    const amount = cbGlobalState.expectedConsensusRate * Number(stake) * Number(durationMax) + BR_STRESS_TESTING_CONTRACT
    const algo = (stressTestFeeAmt + amount) / 1000000
    if (stake && duration && durationMax) {
      setExpectedTotalAmt(algo)
    } else {
      setExpectedTotalAmt(NaN)
    }
  }, [stake, duration, durationMax])

  async function onCreateTest(data: FormData) {
    setLoading(true)
    const { stake, duration, durationMax } = data

    const res = await createStressTest(
      algorandClient,
      certBoardClient,
      BigInt(stake),
      BigInt(duration),
      BigInt(durationMax),
      activeAddress as string,
      signer,
    )

    setLoading(false)
    if (res.error) return setError({ active: true, message: res.errorMsg as string })

    if (res.appId) callback(res.appId)
  }

  return (
    <>
      <form onSubmit={handleSubmit(onCreateTest)}>
        <div className="mb-5">
          <h1 className="font-bold text-lg">Create Test</h1>
          <p className="text-sm">Fill out the details to create the test.</p>
          <ActiveWalletBadge />
        </div>
        <div className="space-y-4">
          <div className="space-y-1">
            <Label>Requested Stake :</Label>
            <Input
              {...register('stake', { valueAsNumber: true })}
              name="stake"
              placeholder="Enter Stake Amount"
              onChange={(e) => {
                if (e.target.value) {
                  setStake(parseInt(e.target.value))
                } else {
                  setStake(0)
                }
              }}
            />
            <FormFieldError errObj={errors.stake} message={errors.stake?.message as string} />
          </div>
          <div className="space-y-1">
            <Label>Stress Test Duration :</Label>
            <Input
              {...register('duration', { valueAsNumber: true })}
              name="duration"
              placeholder="Enter Stress Duration"
              onChange={(e) => {
                if (e.target.value) {
                  setDuration(parseInt(e.target.value))
                } else {
                  setDuration(0)
                }
              }}
            />
            <FormFieldError errObj={errors.duration} message={errors.duration?.message as string} />
          </div>
          <div className="space-y-1">
            <Label>Maximum Duration :</Label>
            <Input
              {...register('durationMax', { valueAsNumber: true })}
              name="durationMax"
              placeholder="Enter Maximum Duration"
              onChange={(e) => {
                if (e.target.value) {
                  setDurationMax(parseInt(e.target.value))
                } else {
                  setDurationMax(0)
                }
              }}
            />
            <FormFieldError errObj={errors.durationMax} message={errors.durationMax?.message as string} />
          </div>
          <Separator className="h-[2px]" />
          <div className="flex gap-1 items-center flex-wrap">
            <h1 className="text-sm font-semibold">Expected Total Amount :</h1>
            <div className="flex items-center">
              <p className="text-sm">
                {expectedTotalAmt ? `${expectedTotalAmt}` : <span className="font-mono">Please fill all details</span>}
              </p>
              {expectedTotalAmt ? (
                <>
                  <AlgorandUnitLogo size={8} leftOffSet={-8} />
                </>
              ) : (
                ''
              )}
            </div>
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button type="submit" variant={'secondary'} disabled={loading}>
            <Loading visible={loading} />
            <span className="ml-2 flex items-center">
              Create Test <ChevronRight className="w-4 h-4" />
            </span>
          </Button>
        </div>
        <div className="flex mt-4">
          <FormError errState={error.active} errMessage={error.message} />
        </div>
      </form>
    </>
  )
}

export default CreateTestForm
