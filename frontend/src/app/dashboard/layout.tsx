import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard",
  description:
    "Generate tailored resumes, cover letters, and application answers with Zumud's AI tools.",
  robots: { index: false, follow: false },
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return children;
}
