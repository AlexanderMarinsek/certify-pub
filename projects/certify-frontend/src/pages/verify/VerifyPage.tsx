import { FormFieldError } from '@/components/FormErrors'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'
import { useDappState } from '@/providers/DappStateProvider'
import { certBoard_VerifyByIssuer, certBoard_VerifyByTestId } from '@/utils/method'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import Loading from '@/components/Loading'
import { useParams } from 'react-router-dom'

const formSchema = z.object({
  testId: z.number({ message: 'Invalid Test Id' }),
  validator: z.string(),
  issuer: z.string(),
})

type FormData = z.infer<typeof formSchema>

type FormType = {
  testId: number
  validator: string
  issuer: string
}

const VerifyPage = () => {
  const { id, validatorAddress } = useParams()
  const { algorandClient } = useDappState()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormType>()

  const [loading, setLoading] = useState<boolean>(false)
  const [verifyType, setVerifyType] = useState<'testId' | 'issuer'>('testId')
  const [response, setResponse] = useState<string>('')

  async function onVerify(data: FormData) {
    const { issuer, validator, testId } = data
    setLoading(true)
    let res
    if (verifyType === 'issuer') {
      res = await certBoard_VerifyByIssuer(algorandClient, issuer as string, validator as string)
    } else {
      res = await certBoard_VerifyByTestId(algorandClient, Number(testId), validator as string)
    }
    setResponse(res)
    setLoading(false)
  }

  return (
    <>
      <div className="flex justify-center ">
        <div className="w-full lg:w-[850px]">
          <div className="mb-6">
            <h1 className="text-xl font-bold">Verify Validator</h1>
            <p>Find Certificates for a Node Runner</p>
          </div>
          <Card>
            <CardHeader></CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onVerify)}>
                <div className="flex gap-2 items-center mb-4">
                  <Label>Verify by:</Label>
                  <Select
                    name="searchType"
                    defaultValue="testId"
                    onValueChange={(value) => setVerifyType(value === 'testId' ? 'testId' : 'issuer')}
                  >
                    <SelectTrigger className="w-fit">
                      <SelectValue placeholder="Select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={'testId'}>Test ID</SelectItem>
                      <SelectItem value={'issuer'}>Issuer Address</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-4">
                  {verifyType === 'issuer' && (
                    <div className="space-y-1">
                      <Label>Issuer's Address :</Label>
                      <Input
                        {...register('issuer', {
                          required: verifyType === 'issuer',
                        })}
                        name="issuer"
                        placeholder="Enter Issuer's Address"
                      />
                      <FormFieldError errObj={errors.issuer} message={'Invalid Address' as string} />
                    </div>
                  )}
                  {verifyType === 'testId' && (
                    <div className="space-y-1">
                      <Label>Test Id :</Label>
                      <Input
                        {...register('testId', {
                          valueAsNumber: true,
                          required: verifyType === 'testId',
                        })}
                        name="testId"
                        type="number"
                        defaultValue={id ? Number(id) : ''}
                        placeholder="Enter Stress Test Id"
                      />
                      <FormFieldError errObj={errors.testId} message={'Invalid Test-Id' as string} />
                    </div>
                  )}
                  <div className="space-y-1">
                    <Label>Validator's Address :</Label>
                    <Input
                      {...register('validator', {
                        required: true,
                      })}
                      name="validator"
                      defaultValue={validatorAddress ? validatorAddress : ''}
                      placeholder="Enter Validator's Address"
                    />
                    <FormFieldError errObj={errors.validator} message={'Invalid Address' as string} />
                  </div>
                </div>
                <Button disabled={loading} className="mt-6" type="submit">
                  <Loading visible={loading} />
                  <span className="ml-2">{loading ? 'Waiting for Response' : 'Verify'}</span>
                </Button>
              </form>
              <Separator className="my-4" />
              <div className="space-y-1">
                <Label>Response :</Label>
                <Textarea spellCheck={false} disabled={response === ''} value={response} className="h-64" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}

export default VerifyPage
