import { Provider, useWallet } from '@txnlab/use-wallet'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { useEffect, useState } from 'react'

interface ConnectWalletModalInterface {
  openModal: boolean
  closeModal: () => void
}

const ConnectWalletModal = ({ openModal, closeModal }: ConnectWalletModalInterface) => {
  const [loading, setLoading] = useState<boolean>(false)
  const { providers, activeAccount } = useWallet()

  const isKmd = (provider: Provider) => provider.metadata.name.toLowerCase() === 'kmd'

  return (
    <>
      <Dialog open={openModal} onOpenChange={closeModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Select Wallet Provider</DialogTitle>
            <DialogDescription></DialogDescription>
          </DialogHeader>
          <div>
            <form method="dialog">
              <div className="space-y-4"></div>
              <div className="space-y-4">
                {providers?.map((provider) => (
                  <div key={provider.metadata.id}>
                    <h4 className="font-semibold flex items-center space-x-2">
                      {!isKmd(provider) && (
                        <img
                          width={30}
                          height={30}
                          alt={`${provider.metadata.name} icon`}
                          src={provider.metadata.icon}
                          className="inline-block"
                        />
                      )}
                      <span>{provider.metadata.name}</span>
                      {isKmd(provider) && <span>{provider.metadata.name}</span>}
                      {provider.isActive && <span className="text-green-600">[active]</span>}
                    </h4>

                    <div className="mt-2 space-x-2">
                      <Button
                        type="button"
                        onClick={async () => {
                          await provider.connect()
                        }}
                        variant={'outline'}
                        disabled={provider.isConnected}
                      >
                        Connect
                      </Button>
                      <Button
                        type="button"
                        onClick={async () => {
                          setLoading(true)
                          await provider.disconnect()
                          setLoading(false)
                        }}
                        variant={'outline'}
                        disabled={!provider.isConnected}
                      >
                        Disconnect
                      </Button>
                      <Button
                        type="button"
                        onClick={() => {
                          provider.setActiveProvider()
                        }}
                        variant={'outline'}
                        disabled={!provider.isConnected || provider.isActive}
                      >
                        Set Active
                      </Button>
                    </div>
                    {provider.isActive && provider.accounts.length > 0 && !loading && (
                      <div className="mt-4 w-fit">
                        <Select value={activeAccount?.address} onValueChange={(value) => provider.setActiveAccount(value)}>
                          <SelectTrigger>
                            <SelectValue className="w-fit overflow-hidden" placeholder="Select Address" />
                          </SelectTrigger>
                          <SelectContent>
                            {provider.accounts.map((account) => (
                              <SelectItem key={account.address} value={account.address}>
                                {`${account.address.substring(0, 10)}...${account.address.substring(account.address.length - 10)}`}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* <div className="flex gap-2 mt-4">
                <Button
                  data-test-id="close-wallet-modal"
                  variant={'outline'}
                  onClick={() => {
                    closeModal()
                  }}
                >
                  Close
                </Button>
                {activeAddress && (
                  <Button
                    data-test-id="logout"
                    onClick={() => {
                      if (providers) {
                        const activeProvider = providers.find((p) => p.isActive)
                        if (activeProvider) {
                          activeProvider.disconnect()
                        } else {
                          // Required for logout/cleanup of inactive providers
                          // For instance, when you login to localnet wallet and switch network
                          // to testnet/mainnet or vice verse.
                          localStorage.removeItem('txnlab-use-wallet')
                          window.location.reload()
                        }
                        navigate('/')
                      }
                    }}
                  >
                    Logout
                  </Button>
                )}
              </div> */}
            </form>
          </div>
        </DialogContent>
      </Dialog>

      {/* <dialog id="connect_wallet_modal" className={`modal ${openModal ? 'modal-open' : ''}`}>

      </dialog> */}
    </>
  )
}

export default ConnectWalletModal
