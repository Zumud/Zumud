import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
  description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers.",
  keywords: "resume improver, resume enhancement, professional resume, ATS-friendly resume, resume builder, career tools",
  authors: [{ name: "TailorMade" }],
  generator: "Next.js",
  applicationName: "TailorMade Resume Improver",
  referrer: "origin-when-cross-origin",
  creator: "TailorMade Team",
  publisher: "TailorMade",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-video-preview': -1,
      'max-snippet': -1,
    },
  },
  openGraph: {
    title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
    description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out to recruiters and hiring managers.",
    url: "https://zumud.com",
    siteName: "TailorMade",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "TailorMade Resume Improver"
      }
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Resume Improver | Instantly Enhance Your Resume - TailorMade",
    description: "Transform your resume instantly with our AI-powered resume improver. Get a professional, ATS-friendly resume that stands out.",
    images: ["/images/twitter-image.jpg"],
    creator: "@tailormadeapp",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
  },
  alternates: {
    canonical: "https://zumud.com",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
