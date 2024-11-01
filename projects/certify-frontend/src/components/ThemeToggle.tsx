import { Moon, Sun } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import { useTheme } from '@/providers/ThemeProvider'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const { setTheme } = useTheme()
  const [dark, setDark] = useState<boolean>(true)

  useEffect(() => {
    setTheme(dark ? 'dark' : 'light')
  }, [dark])

  return (
    <>
      <div className="flex gap-1">
        <Sun className="w-5 text-gray-600" />
        <Switch defaultChecked={dark} onClick={() => setDark(!dark)}>
          Swtich
        </Switch>
        <Moon className="w-5 text-gray-600" />
      </div>
    </>
  )
}
