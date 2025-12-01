'use client'

import { ThemeProvider } from '../client/components/ThemeProvider' // Reusing ThemeProvider
import { Toaster } from 'react-hot-toast'
import { GlassSidebar, SidebarProvider, useSidebar } from '../client/components/GlassSidebar'
import { BottomNav } from '../client/components/BottomNav'
import { ExpertHeader } from '@/components/ExpertHeader'
import { cn } from '../client/lib/utils'
import { usePathname } from 'next/navigation'

function ExpertAppLayout({ children }: { children: React.ReactNode }) {
  const { isCollapsed, isHovered } = useSidebar()
  const pathname = usePathname()
  const sidebarExpanded = !isCollapsed || (isCollapsed && isHovered)

  return (
    <div className="flex min-h-screen bg-background">
      <GlassSidebar role="expert" />
      <main className={cn(
        "flex-1 flex flex-col transition-all duration-300 ease-in-out",
        // Mobile: no margin (sidebar is overlay)
        // Desktop: Match sidebar width exactly: 256px (w-64) when expanded, 80px (w-20) when collapsed
        sidebarExpanded ? "lg:ml-[256px]" : "lg:ml-[80px]",
        // Add top padding on mobile for menu button
        "pt-16 lg:pt-0"
      )}>
        <ExpertHeader />
        <div className="flex-1 overflow-y-auto safe-top safe-bottom">
          {/* Content starts 10px from sidebar, centered with max-width */}
          <div className="pl-[10px] pr-[10px] sm:px-4 md:px-6 lg:px-8 xl:px-10 py-4 sm:py-6 md:py-8 w-full h-full">
            <div className="max-w-7xl mx-auto w-full">
              {children}
            </div>
          </div>
        </div>
        <BottomNav role="expert" />
      </main>
    </div>
  )
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <SidebarProvider>
        <ExpertAppLayout>
          {children}
        </ExpertAppLayout>
        <Toaster position="bottom-right" />
      </SidebarProvider>
    </ThemeProvider>
  )
}
