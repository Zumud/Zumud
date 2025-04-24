"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import ResumeImprover from "@/components/resume-improver"
import AuthModal from "@/components/auth/auth-modal"
import { isAuthenticated } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export default function Home() {
  const router = useRouter()
  const [showAuthModal, setShowAuthModal] = useState(false)
  
  useEffect(() => {
    if (isAuthenticated()) {
      router.push("/dashboard")
    }
  }, [router])
  
  const handleLoginSuccess = () => {
    setShowAuthModal(false)
    router.push("/dashboard")
  }
  
  // We define the structured data directly without schema-dts to avoid type issues
  const websiteSchema = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "TailorMade Resume Improver",
    "url": "https://zumud.com",
    "potentialAction": {
      "@type": "SearchAction",
      "target": "https://zumud.com/search?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  };

  const applicationSchema = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "TailorMade Resume Improver",
    "applicationCategory": "BusinessApplication",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "operatingSystem": "Web Browser"
  };

  const organizationSchema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "TailorMade",
    "url": "https://zumud.com",
    "logo": "https://zumud.com/logo.png",
    "sameAs": [
      "https://twitter.com/tailormadeapp",
      "https://linkedin.com/company/tailormade"
    ]
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(applicationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
        <header className="container mx-auto py-4 px-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-emerald-600">TailorMade</div>
          <div className="space-x-2">
            <Button 
              variant="outline"
              onClick={() => setShowAuthModal(true)}
            >
              Login / Sign Up
            </Button>
          </div>
        </header>
        
        <ResumeImprover />
        
        <AuthModal 
          isOpen={showAuthModal} 
          onClose={() => setShowAuthModal(false)} 
          onSuccess={handleLoginSuccess}
        />
      </main>
    </>
  )
}
