import type { Metadata } from "next"
import ResumeImprover from "@/components/resume-improver"

export const metadata: Metadata = {
  title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
  description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers."
}

export default function Home() {
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
        <ResumeImprover />
      </main>
    </>
  )
}
