import { useEffect, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { FormError, FormFieldError } from '@/components/FormErrors'
import Loading from '@/components/Loading'
import { useWallet } from '@txnlab/use-wallet'
import { useDappState } from '@/providers/DappStateProvider'
import { StressTestingClient } from '@/contracts/StressTesting'
import { startStressTest } from '@/utils/method'
import { toast } from 'sonner'
import { getApplicationAddress } from 'algosdk'
import { getStressTestGlobalState } from '@/utils/blockclainUtils'
import { StressTestGlobalStateType } from '@/types/types'

const formSchema = z.object({
  votePk: z.string().min(44, { message: 'Invalid Vote Key' }),
  selectionPk: z.string().min(44, { message: 'Invalid Selection Key' }),
  stateProofPk: z.string().max(88).min(44, { message: 'Invalid State-Proof Key' }),
  voteKeyDilution: z.number({ message: 'Invalid Vote Key Dilution' }),
})

type FormData = z.infer<typeof formSchema>

const StartTestForm = ({ stressTestingId, callback }: { stressTestingId: number; callback: () => void }) => {
  const { activeAddress, signer } = useWallet()
  const { algorandClient, certBoardClient } = useDappState()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(formSchema) })
  const testAppAddress = getApplicationAddress(stressTestingId)
  const [error, setError] = useState<{ active: boolean; message: string }>({ active: false, message: '' })
  const [loading, setLoading] = useState<boolean>(false)
  const [fetching, setFetching] = useState<boolean>(false)
  const [stGlobalState, setSTGlobalState] = useState<StressTestGlobalStateType>()

  //Creating StressTingClient
  const stressTestingClient = new StressTestingClient(
    {
      resolveBy: 'id',
      id: Number(stressTestingId),
    },
    algorandClient.client.algod,
  )

  useEffect(() => {
    const fetchGS = async () => {
      setFetching(true)
      const stressTestGlobalState = await getStressTestGlobalState(stressTestingClient)
      setSTGlobalState(stressTestGlobalState)
      setFetching(false)
    }

    fetchGS()
  }, [])

  async function onStartTest(data: FormData) {
    setLoading(true)

    const { votePk, selectionPk, stateProofPk, voteKeyDilution } = data

    if (stressTestingClient === undefined) {
      setLoading(false)
      return setError({ active: true, message: `Couldn't find Stress Test App Id.` })
    }

    const votePkB64 = Buffer.from(votePk, 'base64')
    const selectionPkB64 = Buffer.from(selectionPk, 'base64')
    const stateProofPkB64 = Buffer.from(stateProofPk, 'base64')

    const res = await startStressTest(
      algorandClient,
      certBoardClient,
      stressTestingClient,
      activeAddress as string,
      BigInt(stressTestingId),
      BigInt(voteKeyDilution),
      votePkB64,
      selectionPkB64,
      stateProofPkB64,
      signer,
    )

    setLoading(false)
    if (res.error) return setError({ active: true, message: res.errorMsg as string })

    console.log('Test Started')

    toast('Test Started', {
      description: 'Stress Test started successfully.',
      action: {
        label: 'Close',
        onClick: () => {},
      },
    })

    callback()
  }

  return (
    <>
      {fetching ? (
        <div>
          <div className="ml-2 flex gap-4 items-center">
            <Loading visible={true} />
            <div>
              <h1 className="font-bold">Creating Stress Test</h1>
              <p>Please wait</p>
            </div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onStartTest)}>
          <div className="mb-5">
            <h1 className="font-bold text-lg">Start Test</h1>
            <p className="text-sm">Fill out the Key-Info to start the test.</p>
            <div className="flex flex-col items-start">
              {/* <Badge variant={'secondary'} className="mt-4">
              Test ID : {stressTestingId ? stressTestingId : 'N/A'}
            </Badge> */}
              <Badge variant={'secondary'} className="mt-4">
                Contract Address : {stressTestingId ? testAppAddress : 'N/A'}
              </Badge>
              {/* <Badge>First Valid Round: {stGlobalState?.roundCreated}</Badge>
            <Badge>Last Valid Round: {stGlobalState?.roundEndMax}</Badge> */}
              <div className="w-full max-w-lg flex justify-between mt-4">
                <div>
                  <h1 className="font-semibold text-sm">Test ID :</h1>
                  <p className="text-sm">{stressTestingId ? stressTestingId : 'N/A'}</p>
                </div>
                <div>
                  <h1 className="font-semibold text-sm">First Round :</h1>
                  <p className="text-sm">{stGlobalState?.roundCreated ? stGlobalState.roundCreated : 'N/A'}</p>
                </div>
                <div>
                  <h1 className="font-semibold text-sm">Last Round :</h1>
                  <p className="text-sm">{stGlobalState?.roundEndMax ? stGlobalState.roundEndMax : 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Vote Key :</Label>
              <Input {...register('votePk')} name="votePk" placeholder="Enter Vote Key" />
              <FormFieldError errObj={errors.votePk} message={errors.votePk?.message as string} />
            </div>
            <div className="space-y-1">
              <Label>Selection Key :</Label>
              <Input {...register('selectionPk')} name="selectionPk" placeholder="Enter Selection Key" />
              <FormFieldError errObj={errors.selectionPk} message={errors.selectionPk?.message as string} />
            </div>
            <div className="space-y-1">
              <Label>State Proof Key :</Label>
              <Input {...register('stateProofPk')} name="stateProofPk" placeholder="Enter State Proof Key" />
              <FormFieldError errObj={errors.stateProofPk} message={errors.stateProofPk?.message as string} />
            </div>
            <div className="space-y-1">
              <Label>Vote Key Dilution :</Label>
              <Input
                {...register('voteKeyDilution', { valueAsNumber: true })}
                type="number"
                name="voteKeyDilution"
                placeholder="Enter Vote Key Dilution"
              />
              <FormFieldError errObj={errors.voteKeyDilution} message={errors.voteKeyDilution?.message as string} />
            </div>

            {/* <Collapsible className="space-y-2">
            <div className="flex items-center bg-gray-50 dark:bg-gray-800 rounded-lg py-1 px-1">
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm" className="w-9 p-0">
                  <ChevronsUpDown className="h-4 w-4" />
                </Button>
              </CollapsibleTrigger>
              <h4 className="text-sm font-semibold">Additional Options</h4>
              <Separator className="w-fit flex-grow mx-4 h-[2px] dark:bg-white dark:h-[1px]" />
            </div>
            <CollapsibleContent className="flex gap-4 px-1">
              <div className="w-full space-y-1">
                <Label>Vote First :</Label>
                <Input
                  {...register('voteFirst', { valueAsNumber: true })}
                  defaultValue={0}
                  name="voteFirst"
                  placeholder="Enter Vote First Round"
                />
                <FormFieldError errObj={errors.voteFirst} message={errors.voteFirst?.message as string} />
              </div>
              <div className="w-full space-y-1">
                <Label>Vote Last :</Label>
                <Input
                  {...register('voteLast', { valueAsNumber: true })}
                  defaultValue={0}
                  name="voteLast"
                  placeholder="Enter Vote Last Round"
                />
                <FormFieldError errObj={errors.voteLast} message={errors.voteLast?.message as string} />
              </div>
            </CollapsibleContent>
          </Collapsible> */}
          </div>
          <div className="flex justify-end mt-4">
            <Button type="submit" disabled={loading}>
              <Loading visible={loading} />
              <span className="ml-2 flex items-center">Start Test</span>
            </Button>
          </div>
          <div className="flex mt-4">
            <FormError errState={error.active} errMessage={error.message} />
          </div>
        </form>
      )}
    </>
  )
}

export default StartTestForm
