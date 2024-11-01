import { certBoardAppID } from '@/certBoardAppID'
import { CertBoardClient } from '@/contracts/CertBoard'
import { getAlgodConfigFromViteEnvironment } from '@/utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'
import { createContext, ReactNode, useContext, useState } from 'react'

type DappStateType = {
  algorandClient: AlgorandClient
  setAlgorandClient: React.Dispatch<React.SetStateAction<AlgorandClient>>
  certBoardClient: CertBoardClient
  setCertBoardClient: React.Dispatch<React.SetStateAction<CertBoardClient>>
}

const DappStateContext = createContext<DappStateType | undefined>(undefined)

export const DappStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const algodConfig = getAlgodConfigFromViteEnvironment()
  const defaultAlgorandClient = AlgorandClient.fromConfig({ algodConfig })

  const defaultCertBoardClient = new CertBoardClient(
    {
      resolveBy: 'id',
      id: certBoardAppID,
    },
    defaultAlgorandClient.client.algod,
  )

  const [algorandClient, setAlgorandClient] = useState<AlgorandClient>(defaultAlgorandClient)
  const [certBoardClient, setCertBoardClient] = useState<CertBoardClient>(defaultCertBoardClient)
  return (
    <DappStateContext.Provider value={{ algorandClient, setAlgorandClient, certBoardClient, setCertBoardClient }}>
      {children}
    </DappStateContext.Provider>
  )
}

export const useDappState = (): DappStateType => {
  const context = useContext(DappStateContext)
  if (context === undefined) {
    throw new Error('useGlobalState must be used within a GlobalStateProvider')
  }
  return context
}
