import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Your tailored resume",
  description: "Preview and download your AI-tailored, ATS-optimized resume.",
  robots: { index: false, follow: false },
};

export default function ResumeLayout({ children }: { children: React.ReactNode }) {
  return children;
}
