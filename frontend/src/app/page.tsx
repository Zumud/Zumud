"use client"

import { useState, Suspense, useCallback, useEffect } from "react"
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
import { createClient } from "@/lib/supabase/client"

function LandingPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const signupRequested = searchParams.get('signup') === 'true'
  const [showAuthModal, setShowAuthModal] = useState(signupRequested)
  const [userAuthenticated, setUserAuthenticated] = useState(false)

  // Keep one auth state for every landing-page CTA so the header and the rest
  // of the page cannot disagree about whether the visitor is signed in.
  useEffect(() => {
    const supabase = createClient()
    let active = true

    supabase.auth.getSession().then(({ data }) => {
      if (!active) return

      const authenticated = !!data.session
      setUserAuthenticated(authenticated)
      if (authenticated) setShowAuthModal(false)
    })

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, session) => {
      const authenticated = !!session
      setUserAuthenticated(authenticated)
      if (authenticated) setShowAuthModal(false)
    })

    return () => {
      active = false
      subscription.subscription.unsubscribe()
    }
  }, [])

  const handleAuthSuccess = useCallback(() => {
    setShowAuthModal(false)
    router.push('/dashboard')
  }, [router])

  const handleAuthModalOpen = useCallback(() => {
    if (userAuthenticated) {
      router.push('/dashboard')
      return
    }

    setShowAuthModal(true)
  }, [router, userAuthenticated])

  const handleAuthModalClose = useCallback(() => {
    setShowAuthModal(false)
  }, [])

  return (
    <div className="flex min-h-screen flex-col overflow-x-clip pt-16">
      <Navbar
        userAuthenticated={userAuthenticated}
        onAuthModalOpen={handleAuthModalOpen}
      />
      <main className="flex-1">
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <LatexSection />
        <OpenSourceSection />
        <PricingSection
          userAuthenticated={userAuthenticated}
          onAuthModalOpen={handleAuthModalOpen}
        />
        <FaqSection />
        <CallToActionSection
          userAuthenticated={userAuthenticated}
          onAuthModalOpen={handleAuthModalOpen}
        />
      </main>
      <Footer />

      <AuthModal
        isOpen={showAuthModal}
        onClose={handleAuthModalClose}
        onSuccess={handleAuthSuccess}
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
