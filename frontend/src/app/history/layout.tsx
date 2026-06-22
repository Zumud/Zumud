import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Document history",
  description: "Access your generated resumes and cover letters synced to Google Drive.",
  robots: { index: false, follow: false },
};

export default function HistoryLayout({ children }: { children: React.ReactNode }) {
  return children;
}
