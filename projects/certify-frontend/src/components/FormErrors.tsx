import React from 'react'
import { FieldError, FieldErrorsImpl, Merge } from 'react-hook-form'
import { AlertCircle } from 'lucide-react'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export const FormFieldError = ({
  errObj,
  message,
}: {
  errObj: FieldError | Merge<FieldError, FieldErrorsImpl<any>> | undefined
  message: string
}) => {
  return errObj && <p className="text-sm text-red-500">{message}</p>
}

export const FormError = ({ errState, errMessage }: { errState: boolean; errMessage: string }) => {
  return (
    errState && (
      <Alert variant="destructive" className="w-auto">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error :</AlertTitle>
        <AlertDescription>{errMessage}</AlertDescription>
      </Alert>
    )
  )
}
