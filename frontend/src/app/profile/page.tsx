"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/ui/sidebar"
import { isAuthenticated, signOut } from "@/lib/utils"
import ProfileSettingsPage from "@/components/profile/profile-settings-page"

export default function ProfilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true)

  useEffect(() => {
    let active = true
    isAuthenticated().then((ok) => {
      if (!active) return
      if (!ok) {
        router.push("/")
      } else {
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [router])

  const handleLogout = async () => {
    await signOut()
    router.push("/")
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="size-12 animate-spin rounded-full border-[3px] border-border border-t-brand"></div>
      </div>
    )
  }

  return (
    <div className="ambient-glow relative min-h-screen bg-background">
      <Sidebar
        onLogout={handleLogout}
        onCollapsedChange={setIsSidebarCollapsed}
      />
      <main
        className={`pt-16 transition-[margin] duration-300 ease-in-out md:pt-0 ${
          isSidebarCollapsed ? "md:ml-16" : "md:ml-64"
        }`}
      >
        <ProfileSettingsPage />
      </main>
    </div>
  )
}
