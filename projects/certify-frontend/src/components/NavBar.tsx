import React, { useState } from 'react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { ellipseAddress } from '@/utils/ellipseAddress'
import { useWallet } from '@txnlab/use-wallet'
import { ChevronDown, FlaskConical, IdCard, MountainIcon, ShieldCheck, UserCheck, Wallet, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from './ui/button'
import ConnectWalletModal from './ConnectWalletModal'
import { ThemeToggle } from './ThemeToggle'
import { Drawer, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle } from './ui/drawer'
import { GitHubLogoIcon, TwitterLogoIcon } from '@radix-ui/react-icons'
import CertifyLogo from './CertifyLogo'
import { ThemeDropdown } from './ThemeDropdown'
import { Separator } from './ui/separator'

interface NavBarProps {}

export const NavBar: React.FC<NavBarProps> = () => {
  const navigate = useNavigate()
  const { activeAddress } = useWallet()
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  const [openMenuDrawer, setOpenMenuDrawer] = useState<boolean>(false)
  const [openMenuPopover, setOpenMenuPopover] = useState<boolean>(false)

  // console.log({ addr: activeAddress })

  const toggleMenuDrawer = () => {
    setOpenMenuDrawer(!openMenuDrawer)
  }

  return (
    <>
      <div className="z-50 pt-2 flex justify-center relative top-0 w-full  border-b bg-white dark:bg-black/30 backdrop-blur-0">
        <div className="w-full lg:w-[850px] flex justify-between items-center pb-2 px-2">
          <Button className="font-bold lg:hidden" variant={'outline'} onClick={() => setOpenMenuDrawer(!openMenuDrawer)}>
            ☰
          </Button>
          <MenuDrawer open={openMenuDrawer} onOpenChange={toggleMenuDrawer} />
          <div className="flex gap-1 items-center">
            <div className="flex items-center gap-1 cursor-pointer" onClick={() => navigate('/')}>
              {/* <MountainIcon fill="black" className="h-6 w-6" /> */}
              <h1 className="mt-1 font-bold text-lg">Certify</h1>
              <div className="w-5">
                <CertifyLogo />
              </div>
            </div>
            <Popover open={openMenuPopover} onOpenChange={setOpenMenuPopover}>
              <PopoverTrigger className="hidden lg:flex" asChild>
                <div className="ml-2 flex gap-1 items-center px-2 py-1 rounded-md bg-gray-200  hover:bg-gray-100 dark:bg-gray-900 dark:hover:bg-gray-800 cursor-pointer">
                  <span className="text-sm font-medium">Services</span>
                  <ChevronDown className="w-4" />
                </div>
              </PopoverTrigger>
              <PopoverContent className="w-44 p-1 border-none">
                <div className="flex flex-col gap-1">
                  <div
                    onClick={() => {
                      navigate('/test')
                      setOpenMenuPopover(false)
                    }}
                    className="block select-none space-y-1 p-3 transition-colors rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer"
                  >
                    <div className="flex gap-1 items-center text-sm  font-semibold leading-none">
                      {' '}
                      <Zap className="w-4" /> Stress Test
                    </div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">Stress Test your Node</p>
                  </div>
                  <div
                    onClick={() => {
                      navigate('/verify')
                      setOpenMenuPopover(false)
                    }}
                    className="block select-none space-y-1 p-3 transition-colors rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer"
                  >
                    <div className="flex gap-1 items-center text-sm font-semibold leading-none">
                      {' '}
                      <ShieldCheck className="w-4" /> Verify
                    </div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">Verify test certificate for validators</p>
                  </div>
                  <div
                    onClick={() => {
                      navigate('/attest')
                      setOpenMenuPopover(false)
                    }}
                    className="block select-none space-y-1 rounded-md p-3 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground cursor-pointer"
                  >
                    <div className="flex gap-1 items-center text-sm text-sm font-semibold leading-none">
                      {' '}
                      <UserCheck className="w-4" /> Attest
                    </div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">Review Validators on chain</p>
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size={'sm'}
              className={`${activeAddress ? 'rounded-xl' : 'rounded-xl'}`}
              variant={activeAddress ? 'outline' : 'secondary'}
              onClick={() => {
                setOpenWalletModal(!openWalletModal)
              }}
            >
              <Wallet className="h-4 w-4 mr-2" />
              <p className="text-xm hidden lg:block">{activeAddress ? ellipseAddress(activeAddress) : 'Connect'}</p>
            </Button>
            <div className="hidden lg:block">
              <ThemeDropdown />
            </div>
            <div className="gap-3 text-gray-700 dark:text-gray-100 cursor-pointer hidden lg:flex">
              <GitHubLogoIcon
                onClick={() => window.open('https://github.com/AlexanderMarinsek/certify-pub', '_blank')}
                style={{ width: '20px', height: '20px' }}
              />
              <TwitterLogoIcon
                onClick={() => window.open('https://x.com/CertifyPlatform', '_blank')}
                style={{ width: '20px', height: '20px' }}
              />
            </div>
          </div>
        </div>
      </div>
      <ConnectWalletModal
        openModal={openWalletModal}
        closeModal={() => {
          setOpenWalletModal(!openWalletModal)
        }}
      />
    </>
  )
}

interface MenuDrawerProps {
  open: boolean
  onOpenChange: () => void
}

const MenuDrawer: React.FC<MenuDrawerProps> = ({ open, onOpenChange }) => {
  const navigate = useNavigate()
  return (
    <>
      <Drawer open={open} onOpenChange={onOpenChange} direction="left">
        <DrawerContent className="h-full w-1/2 md:max-w-[250px] rounded-none">
          <DrawerHeader>
            <DrawerTitle className="flex justify-center">
              <MountainIcon fill="black" className="h-6 w-6" />
            </DrawerTitle>
            <DrawerDescription></DrawerDescription>
          </DrawerHeader>
          <div className="flex flex-col px-2 gap-2">
            <div
              onClick={() => navigate('/test')}
              className="ml-2 flex items-center gap-x-3.5 py-2 px-2.5 bg-gray-50 text-sm text-gray-700 dark:bg-background dark:border dark:text-white rounded-lg hover:bg-gray-100 cursor-pointer"
            >
              <FlaskConical className="w-4" />
              Stress Test
            </div>
            <div
              onClick={() => navigate('/attest')}
              className="ml-2 flex items-center gap-x-3.5 py-2 px-2.5 bg-gray-50 text-sm text-gray-700 rounded-lg dark:bg-background dark:border dark:text-white hover:bg-gray-100 cursor-pointer"
            >
              <IdCard className="w-4" />
              Attest Validator
            </div>
            <div
              onClick={() => navigate('/verify')}
              className="ml-2 flex items-center gap-x-3.5 py-2 px-2.5 bg-gray-50 text-sm text-gray-700 rounded-lg dark:bg-background dark:border dark:text-white hover:bg-gray-100 cursor-pointer"
            >
              <ShieldCheck className="w-4" />
              Verify
            </div>
            <Separator className="m-2 w-auto" />
            <div
              onClick={() => window.open('https://github.com/AlexanderMarinsek/certify-pub', '_blank')}
              className="ml-2 flex items-center gap-x-3.5 py-2 px-2.5 bg-white text-sm text-gray-700 rounded-lg dark:bg-background dark:border dark:text-white hover:bg-gray-100 cursor-pointer"
            >
              <GitHubLogoIcon className="w-4" />
              Github
            </div>
            <div
              onClick={() => window.open('https://x.com/CertifyPlatform', '_blank')}
              className="ml-2 flex items-center gap-x-3.5 py-2 px-2.5 bg-white text-sm text-gray-700 rounded-lg dark:bg-background dark:border dark:text-white hover:bg-gray-100 cursor-pointer"
            >
              <TwitterLogoIcon className="w-4" />
              Socials
            </div>
          </div>
          <DrawerFooter>
            {/* <Button size={'sm'} onClick={toggleWalletModal}>
                {activeAddress ? ellipseAddress(activeAddress) : 'Connect Wallet'}
              </Button> */}
            <div className="flex justify-center mt-4">
              <ThemeToggle />
            </div>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </>
  )
}
