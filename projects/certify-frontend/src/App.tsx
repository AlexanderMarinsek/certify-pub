import { DeflyWalletConnect } from '@blockshake/defly-connect'
import { DaffiWalletConnect } from '@daffiwallet/connect'
import { PeraWalletConnect } from '@perawallet/connect'
import { PROVIDER_ID, ProvidersArray, WalletProvider, useInitializeProviders } from '@txnlab/use-wallet'
import algosdk from 'algosdk'
import { SnackbarProvider } from 'notistack'
import Home from './Home'
import { getAlgodConfigFromViteEnvironment, getKmdConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import VerifyPage from './pages/verify/VerifyPage'
import AttestPage from './pages/attest/AttestPage'
import StressTestPage from './pages/stresstest/StressTestPage'
import { NavBar } from './components/NavBar'
import LearnPage from './pages/learn/LearnPage'
import { DappStateProvider } from './providers/DappStateProvider'
import { Toaster } from '@/components/ui/sonner'
import { ThemeProvider } from './providers/ThemeProvider'

let providersArray: ProvidersArray
if (import.meta.env.VITE_ALGOD_NETWORK === '') {
  const kmdConfig = getKmdConfigFromViteEnvironment()
  providersArray = [
    {
      id: PROVIDER_ID.KMD,
      clientOptions: {
        wallet: kmdConfig.wallet,
        password: kmdConfig.password,
        host: kmdConfig.server,
        token: String(kmdConfig.token),
        port: String(kmdConfig.port),
      },
    },
  ]
} else {
  providersArray = [
    { id: PROVIDER_ID.DEFLY, clientStatic: DeflyWalletConnect },
    { id: PROVIDER_ID.PERA, clientStatic: PeraWalletConnect },
    { id: PROVIDER_ID.DAFFI, clientStatic: DaffiWalletConnect },
    { id: PROVIDER_ID.EXODUS },
    // If you are interested in WalletConnect v2 provider
    // refer to https://github.com/TxnLab/use-wallet for detailed integration instructions
  ]
}

export default function App() {
  const algodConfig = getAlgodConfigFromViteEnvironment()

  const walletProviders = useInitializeProviders({
    providers: providersArray,
    nodeConfig: {
      network: algodConfig.network,
      nodeServer: algodConfig.server,
      nodePort: String(algodConfig.port),
      nodeToken: String(algodConfig.token),
    },
    algosdkStatic: algosdk,
  })

  return (
    <SnackbarProvider maxSnack={3}>
      <WalletProvider value={walletProviders}>
        <DappStateProvider>
          <ThemeProvider>
            <Router>
              <NavBar />
              <div className="mt-20 p-2">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/verify/:id?/:validatorAddress?" element={<VerifyPage />} />
                  <Route path="/attest" element={<AttestPage />} />
                  <Route path="/test" element={<StressTestPage />} />
                  <Route path="/learn" element={<LearnPage />} />
                </Routes>
                <Toaster />
              </div>
            </Router>
          </ThemeProvider>
        </DappStateProvider>
      </WalletProvider>
    </SnackbarProvider>
  )
}
