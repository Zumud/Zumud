import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeScript } from "@/components/theme/theme-script";

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
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0c1018" },
  ],
};

const SITE_DESCRIPTION =
  "Zumud tailors your resume and cover letter to any job description in seconds. Beat the ATS, get 3× more interviews, and save 15+ minutes per application — your first 10 generations are free.";

export const metadata: Metadata = {
  metadataBase: new URL("https://zumud.com"),
  title: {
    default: "Zumud — Instant Job-Specific Resumes & Cover Letters",
    template: "%s | Zumud",
  },
  description: SITE_DESCRIPTION,
  keywords: [
    "AI resume builder",
    "job-specific resume",
    "tailored resume",
    "ATS-optimized resume",
    "cover letter generator",
    "more interviews",
    "resume tailoring",
    "job application tool",
  ],
  authors: [{ name: "Zumud" }],
  generator: "Next.js",
  applicationName: "Zumud",
  referrer: "origin-when-cross-origin",
  creator: "Zumud Team",
  publisher: "Zumud",
  category: "technology",
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
      "max-image-preview": "large",
      "max-video-preview": -1,
      "max-snippet": -1,
    },
  },
  openGraph: {
    title: "Zumud — Instant Job-Specific Resumes & Cover Letters",
    description: SITE_DESCRIPTION,
    url: "https://zumud.com",
    siteName: "Zumud",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/og-image.svg",
        width: 1200,
        height: 630,
        alt: "Zumud — AI resume builder for instant job-specific resumes",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Zumud — Instant Job-Specific Resumes & Cover Letters",
    description: SITE_DESCRIPTION,
    images: ["/twitter-image.svg"],
    creator: "@zumudapp",
  },
  alternates: {
    canonical: "https://zumud.com",
  },
};

// Organization + product structured data for richer search results.
const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://zumud.com/#organization",
      name: "Zumud",
      url: "https://zumud.com",
      logo: "https://zumud.com/logos/zumud/combined.svg",
      sameAs: ["https://twitter.com/zumudapp"],
    },
    {
      "@type": "WebSite",
      "@id": "https://zumud.com/#website",
      url: "https://zumud.com",
      name: "Zumud",
      description: SITE_DESCRIPTION,
      publisher: { "@id": "https://zumud.com/#organization" },
    },
    {
      "@type": "SoftwareApplication",
      name: "Zumud AI Resume Builder",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      description: SITE_DESCRIPTION,
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "USD",
        description: "10 free resume generations, then pay-as-you-go.",
      },
      aggregateRating: {
        "@type": "AggregateRating",
        ratingValue: "4.8",
        ratingCount: "1200",
      },
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />

        {/* Favicon and App Icons */}
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="icon" href="/favicon-16x16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32x32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" />
        <link rel="manifest" href="/site.webmanifest" />

        {/* Structured data for SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />

        {/* Crisp Chat Integration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.$crisp=[];
              window.CRISP_WEBSITE_ID="${process.env.NEXT_PUBLIC_CRISP_WEBSITE_ID || ''}";
              (function(){
                if (!window.CRISP_WEBSITE_ID) return;
                var d=document;
                var s=d.createElement("script");
                s.src="https://client.crisp.chat/l.js";
                s.async=1;
                d.getElementsByTagName("head")[0].appendChild(s);
              })();
            `,
          }}
        />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
