import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profile settings",
  description: "Manage your saved resume and account settings on Zumud.",
  robots: { index: false, follow: false },
};

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children;
}
