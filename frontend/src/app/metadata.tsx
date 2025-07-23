import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
  description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application with our AI-powered resume tool.",
  keywords: ["AI resume", "tailored resume", "more interviews", "custom cover letter", "ATS-optimized resume", "job application", "resume builder"],
  authors: [{ name: "Zumud Team" }],
  creator: "Zumud",
  publisher: "Zumud",
  openGraph: {
    title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
    description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application with our AI-powered resume tool.",
    url: "https://zumud.com",
    siteName: "Zumud",
    images: [
      {
        url: "https://zumud.com/og-image.svg",
        width: 1200,
        height: 630,
        alt: "Zumud AI Resume Builder - Get 3× More Interviews",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
    description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application with our AI-powered resume tool.",
    creator: "@zumudapp",
    images: ["https://zumud.com/twitter-image.svg"],
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