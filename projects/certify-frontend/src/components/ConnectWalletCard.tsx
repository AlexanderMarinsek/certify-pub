import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from './ui/button'
import { Wallet } from 'lucide-react'
import ConnectWalletModal from './ConnectWalletModal'
import { useState } from 'react'

const ConnectWalletCard = () => {
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  return (
    <>
      <Card>

        <CardContent>
          <div className="mt-8">
            <h1 className="font-bold text-lg">Connect Wallet</h1>
            <p className="text-sm">Please connect your wallet to proceed.</p>
            <Button onClick={(e) => setOpenWalletModal(true)} className='mt-6'>
              {' '}
              <Wallet className="h-4 w-4 mr-2" /> Connect
            </Button>
          </div>
        </CardContent>
      </Card>
      <ConnectWalletModal
        openModal={openWalletModal}
        closeModal={() => {
          setOpenWalletModal(!openWalletModal)
        }}
      />
    </>
  )
}

export default ConnectWalletCard
