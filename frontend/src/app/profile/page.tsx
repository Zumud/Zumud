"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { isAuthenticated } from "@/lib/utils"
import ProfileSettingsPage from "@/components/profile/profile-settings-page"

export default function ProfilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    )
  }

  return <ProfileSettingsPage />
} 