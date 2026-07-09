"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Dashboard from "@/components/dashboard/dashboard"
import { isAuthenticated } from "@/lib/utils"

export default function DashboardPage() {
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
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="size-12 animate-spin rounded-full border-[3px] border-border border-t-brand"></div>
      </div>
    )
  }

  return <Dashboard />
} 