"use client"

import { useState, useEffect, Suspense, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import AuthModal from "@/components/auth/auth-modal"
import { isAuthenticated } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/landing/navbar"
import HeroSection from "@/components/landing/hero-section"
import CompanyLogosSection from "@/components/landing/company-logos-section"
import HowItWorksSection from "@/components/landing/how-it-works-section"
import FeaturesSection from "@/components/landing/features-section"
import PricingSection from "@/components/landing/pricing-section"
import CallToActionSection from "@/components/landing/call-to-action-section"
import Footer from "@/components/landing/footer"

function LandingPageContent() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    // Check if we should open the signup modal from query params
    if (searchParams.get('signup') === 'true') {
      setAuthMode('signup')
      setShowAuthModal(true)
    }
  }, [searchParams])

  const handleAuthSuccess = useCallback(() => {
    setShowAuthModal(false)
    router.push('/dashboard')
  }, [router])

  const handleAuthModalOpen = useCallback((mode: 'login' | 'signup' = 'login') => {
    setAuthMode(mode)
    setShowAuthModal(true)
  }, [])

  const handleAuthModalClose = useCallback(() => {
    setShowAuthModal(false)
  }, [])

  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden">
      <Navbar onAuthModalOpen={handleAuthModalOpen} />
      <main className="flex-1">
        <HeroSection onAuthModalOpen={handleAuthModalOpen} />
        <CompanyLogosSection />
        <HowItWorksSection />
        <FeaturesSection />
        <PricingSection onAuthModalOpen={handleAuthModalOpen} />
        <CallToActionSection onAuthModalOpen={handleAuthModalOpen} />
      </main>
      <Footer />
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={handleAuthModalClose}
        onSuccess={handleAuthSuccess}
        defaultTab={authMode}
      />
    </div>
  )
}

export default function LandingPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LandingPageContent />
    </Suspense>
  )
}
