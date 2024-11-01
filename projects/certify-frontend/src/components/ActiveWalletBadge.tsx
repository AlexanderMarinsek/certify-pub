import { Badge } from './ui/badge'
import { useWallet } from '@txnlab/use-wallet'

const ActiveWalletBadge = () => {
  const { activeAddress } = useWallet()
  return (
    <>
      <Badge className="mt-4 w-full md:w-auto" variant={'secondary'}>
        <p className="overflow-hidden break-words">Active Address : {activeAddress}</p>
      </Badge>
    </>
  )
}

export default ActiveWalletBadge
