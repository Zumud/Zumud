"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import InterviewReadyResume from "@/components/interview-ready-resume"
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

export default function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')
  const router = useRouter()

  const handleAuthSuccess = () => {
    setShowAuthModal(false)
    router.push('/dashboard')
  }

  const handleAuthModalOpen = (mode: 'login' | 'signup' = 'login') => {
    setAuthMode(mode)
    setShowAuthModal(true)
  }

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
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
        defaultTab={authMode}
      />
    </div>
  )
}
