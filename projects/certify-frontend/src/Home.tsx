// src/components/Home.tsx
import React, { useEffect, useState } from 'react'
import { GraduationCap, ShieldCheck, UserCheck, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { BackgroundBeams } from './components/ui/background-beams'
import algorandFullLogoBlack from '@/assets/algorand_full_logo_black.svg'
import algorandFullLogoWhite from '@/assets/algorand_full_logo_white.svg'
import CertifyLogo from './components/CertifyLogo'
import { useTheme } from './providers/ThemeProvider'
import DotPattern from './components/ui/dot-pattern'
import { cn } from './lib/utils'

interface HomeProps {}

const Home: React.FC<HomeProps> = () => {
  const navigate = useNavigate()
  const { theme } = useTheme()

  return (
    <>
      <div className="flex justify-center items-center ">
        <div className="mt-20 flex flex-col justify-center items-center backdrop-blur-0 p-10">
          <div className="flex flex-col items-center">
            <div className="flex gap-2 items-center justify-center">
              <h1 className="text-6xl lg:text-8xl font-bold">Certify</h1>
              <div className="w-14 lg:w-20">
                <CertifyLogo />
              </div>
            </div>
            <p className="mt-4 text-lg text-center">Blockchain Infrastructure - Performant, Reliable, Transperant</p>
          </div>
          <div className="mt-10 flex gap-4 flex-wrap">
            <div
              onClick={() => navigate('/test')}
              className="cursor-pointer w-full lg:max-w-[200px] hover:scale-110 transition-all backdrop-blur-3xl bg-slate-200/10 dark:bg-white/5 border-2  p-4 rounded-lg space-y-2"
            >
              <div className="flex gap-1">
                <Zap className="w-5" />
                <h1 className="font-semibold">Stress Test</h1>
              </div>
              <p className="text-sm">Prove that you are an excellent node runner.</p>
            </div>
            <div
              onClick={() => navigate('/attest')}
              className="cursor-pointer w-full lg:max-w-[200px] hover:scale-110 transition-all backdrop-blur-3xl bg-slate-200/10 dark:bg-white/5 border-2  p-4 rounded-lg space-y-2"
            >
              <div className="flex gap-1 cursor-pointer">
                <UserCheck className="w-5" />
                <h1 className="font-semibold">Attest</h1>
              </div>
              <p className="text-sm whitespace-wrap">Review a validator on&#8209;chain.</p>
            </div>
            <div
              onClick={() => navigate('/verify')}
              className="cursor-pointer w-full lg:max-w-[200px] hover:scale-110 transition-all backdrop-blur-3xl bg-slate-200/10 dark:bg-white/5 border-2  p-4 rounded-lg space-y-2"
            >
              <div className="flex gap-1">
                <ShieldCheck className="w-5" />
                <h1 className="font-semibold">Verify</h1>
              </div>
              <p className="text-sm">Check the legitimicy of a validator's certificate.</p>
            </div>
            <div className="cursor-pointer w-full lg:max-w-[200px] hover:scale-110 transition-all backdrop-blur-3xl bg-slate-200/10 dark:bg-white/5 border-2  p-4 rounded-lg space-y-2">
              <div className="flex gap-1 cursor-pointer">
                <GraduationCap className="w-5" />
                <h1 className="font-semibold">Learn</h1>
              </div>
              <p className="text-sm">Learn how to run node as a Validator.</p>
            </div>
          </div>
          <div className="mt-20">
            <div className="flex justify-center items-center w-48">
              <p className="">Powered by</p>
              <img src={algorandFullLogoBlack} className="ml-[-5px] block dark:hidden w-24" />
              <img src={algorandFullLogoWhite} className="ml-[-5px] hidden dark:block w-24" />
            </div>
          </div>
        </div>
      </div>
      {theme === 'light' && (
        <DotPattern
          width={20}
          height={20}
          cx={1}
          cy={1}
          cr={1}
          className={cn('[mask-image:radial-gradient(1000px_circle_at_center,transparent,white)]')}
        />
      )}
      {theme === 'dark' && <BackgroundBeams className="-z-50" />}
    </>
  )
}

export default Home
