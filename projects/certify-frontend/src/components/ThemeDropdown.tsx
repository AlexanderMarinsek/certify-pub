import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { useTheme } from '@/providers/ThemeProvider'
import { useEffect, useState } from 'react'

export function ThemeDropdown() {
  const { setTheme } = useTheme()

  const [dark, setDark] = useState<boolean>(true)

  useEffect(() => {
    setTheme(dark ? 'dark' : 'light')
  }, [dark])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={'link'} size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setDark(false)}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setDark(true)}>Dark</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
