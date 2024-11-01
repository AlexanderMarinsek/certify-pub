import React from 'react'
import algorandBlackLogo from '@/assets/algorand_logo_black.svg'
import algorandWhiteLogo from '@/assets/algorand_logo_white.svg'


const AlgorandUnitLogo = ({ size, leftOffSet }: { size: number; leftOffSet: number }) => {
  const lightCss = `w-8 ml-[${leftOffSet}px] block dark:hidden`
  const darkCSS = `w-8 ml-[${leftOffSet}px] hidden dark:block`
  return (
    <>
      <img src={algorandBlackLogo} className={lightCss} />
      <img src={algorandWhiteLogo} className={darkCSS} />
    </>
  )
}

export default AlgorandUnitLogo
