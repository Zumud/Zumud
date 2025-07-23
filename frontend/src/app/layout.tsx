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
  title: "Instant job-specific resumes | Zumud",
  description: "Tailored resume and cover letter for any job in seconds. Our users report 3× more interviews — and save 15+ minutes per application.",
  keywords: "job-specific resume, tailored resume, AI resume builder, more interviews, cover letter, ATS-optimized resume, job application, time-saving",
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
    title: "Instant job-specific resumes | Zumud",
    description: "Tailored resume and cover letter for any job in seconds. Our users report 3× more interviews — and save 15+ minutes per application.",
    url: "https://zumud.com",
    siteName: "Zumud",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/og-image.svg",
        width: 1200,
        height: 630,
        alt: "Zumud AI Resume Builder - Instant job-specific resumes"
      }
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Instant job-specific resumes | Zumud",
    description: "Tailored resume and cover letter for any job in seconds. Our users report 3× more interviews — and save 15+ minutes per application.",
    images: ["/twitter-image.svg"],
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
      <head>
        {/* Favicon and App Icons */}
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="icon" href="/favicon-16x16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32x32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" />
        <link rel="manifest" href="/site.webmanifest" />
        
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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
