import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
  description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers.",
  keywords: ["resume improver", "AI resume", "resume builder", "job application", "ATS-friendly resume"],
  authors: [{ name: "TailorMade Team" }],
  creator: "TailorMade",
  publisher: "TailorMade",
  openGraph: {
    title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
    description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers.",
    url: "https://zumud.com",
    siteName: "TailorMade",
    images: [
      {
        url: "https://zumud.com/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "TailorMade Resume Improver",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
    description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers.",
    creator: "@tailormadeapp",
    images: ["https://zumud.com/twitter-image.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
} 