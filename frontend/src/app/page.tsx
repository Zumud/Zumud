"use client"

import { useState, Suspense, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import AuthModal from "@/components/auth/auth-modal"
import Navbar from "@/components/landing/navbar"
import HeroSection from "@/components/landing/hero-section"
import ProblemSection from "@/components/landing/problem-section"
import SolutionSection from "@/components/landing/solution-section"
import LatexSection from "@/components/landing/latex-section"
import PricingSection from "@/components/landing/pricing-section"
import FaqSection from "@/components/landing/faq-section"
import OpenSourceSection from "@/components/landing/open-source-section"
import CallToActionSection from "@/components/landing/call-to-action-section"
import Footer from "@/components/landing/footer"

function LandingPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const signupRequested = searchParams.get('signup') === 'true'
  const [showAuthModal, setShowAuthModal] = useState(signupRequested)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>(
    signupRequested ? 'signup' : 'login'
  )

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
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <LatexSection />
        <OpenSourceSection />
        <PricingSection onAuthModalOpen={handleAuthModalOpen} />
        <FaqSection />
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
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <div className="size-10 animate-spin rounded-full border-2 border-border border-t-brand" />
        </div>
      }
    >
      <LandingPageContent />
    </Suspense>
  )
}
