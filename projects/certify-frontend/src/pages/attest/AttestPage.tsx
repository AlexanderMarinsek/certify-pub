import ActiveWalletBadge from '@/components/ActiveWalletBadge'
import ConnectWalletCard from '@/components/ConnectWalletCard'
import { FormError, FormFieldError } from '@/components/FormErrors'
import Loading from '@/components/Loading'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useDappState } from '@/providers/DappStateProvider'
import { certBoard_Attest } from '@/utils/method'
import { zodResolver } from '@hookform/resolvers/zod'
import { useWallet } from '@txnlab/use-wallet'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import * as z from 'zod'

const formSchema = z.object({
  validator: z.string().min(22, { message: 'Invalid Address' }),
  info: z.string().min(1, { message: 'Required' }),
})

type FormData = z.infer<typeof formSchema>

const AttestPage = () => {
  const { activeAddress, signer } = useWallet()
  const { algorandClient, certBoardClient } = useDappState()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(formSchema) })

  const [loading, setLoading] = useState<boolean>(false)
  const [charCount, setCharCount] = useState(0)
  const [error, setError] = useState<{ active: boolean; message: string }>({ active: false, message: '' })

  async function onAttest(data: FormData) {
    setLoading(true)
    const { validator, info } = data

    const infoStr = info.length < 1024 ? info.padEnd(1024, ' ') : info
    const infoUInt = new TextEncoder().encode(infoStr)

    //Calling the Function
    const res = await certBoard_Attest(algorandClient, certBoardClient, activeAddress as string, validator, infoUInt, signer)

    setLoading(false)
    if (res.error) return setError({ active: true, message: res.errorMsg as string })

    toast('Validator Attested.', {
      description: 'Validator attested successfully.',
      action: {
        label: 'Close',
        onClick: () => {},
      },
    })
  }

  return (
    <>
      <div className="flex justify-center ">
        <div className="w-full lg:w-[850px]">
          <div className="mb-6">
            <h1 className="text-xl font-bold">Attest Validator</h1>
            <p>Review a Node Runner on chain.</p>
          </div>
          {!activeAddress ? (
            <ConnectWalletCard />
          ) : (
            <Card>
              <CardContent>
                <form onSubmit={handleSubmit(onAttest)} className="mt-8">
                  <div className="mb-5">
                    {/* <h1 className="font-bold text-lg">Create Certificate</h1>
                    <p className="text-sm">Fill out the details to create the test.</p> */}
                    <ActiveWalletBadge />
                  </div>
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <Label>Validator's Address :</Label>
                      <Input {...register('validator')} name="validator" placeholder="Enter Validator's Address" />
                      <FormFieldError errObj={errors.validator} message={errors.validator?.message as string} />
                    </div>
                    <div className="space-y-1">
                      <Label>Certificate :</Label>
                      <Textarea
                        {...register('info')}
                        name="info"
                        maxLength={1024}
                        placeholder="Enter Comments"
                        className="h-64"
                        onChange={(e) => setCharCount(e.target.value.length)}
                      />
                      <div className="grid grid-cols-2 mt-2">
                        <FormFieldError errObj={errors.info} message={errors.info?.message as string} />
                        <p className="text-sm col-start-2 justify-self-end  text-gray-500">{charCount}/1024</p>
                      </div>
                    </div>
                  </div>
                  <Button disabled={loading} className="mt-6" type="submit">
                    <Loading visible={loading} />
                    <span className="ml-2">{loading ? 'Waiting for Approval' : 'Submit'}</span>
                  </Button>
                  <div className="flex justify-end">
                    <FormError errState={error.active} errMessage={error.message} />
                  </div>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </>
  )
}

export default AttestPage
