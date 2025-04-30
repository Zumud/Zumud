import type { Metadata, Viewport } from "next";
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

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL("https://zumud.com"),
  title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
  description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application with our AI-powered resume tool.",
  keywords: "tailored resume, AI resume builder, more interviews, custom cover letter, ATS-optimized resume, job application, time-saving",
  authors: [{ name: "Zumud" }],
  generator: "Next.js",
  applicationName: "Zumud AI Resume Builder",
  referrer: "origin-when-cross-origin",
  creator: "Zumud Team",
  publisher: "Zumud",
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
    title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
    description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application with our AI-powered resume tool.",
    url: "https://zumud.com",
    siteName: "Zumud",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Zumud AI Resume Builder - Get 3× More Interviews"
      }
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Get 3× More Interviews with AI-Tailored Resumes | Zumud",
    description: "Create custom resumes and cover letters in seconds. Our users report 3× more callbacks and save 15+ minutes per application.",
    images: ["/images/twitter-image.jpg"],
    creator: "@zumudapp",
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
