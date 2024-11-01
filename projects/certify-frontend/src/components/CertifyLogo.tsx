import certifyBlack from '@/assets/CertifyBlack.svg'
import certifyWhite from '@/assets/CertifyWhite.svg'

const CertifyLogo = () => {
  return (
    <>
      <img src={certifyWhite} className="hidden dark:block" />
      <img src={certifyBlack} className="block dark:hidden" />
    </>
  )
}

export default CertifyLogo
