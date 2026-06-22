import type { Metadata } from "next";
import LegalPage from "@/components/legal/legal-page";

export const metadata: Metadata = {
  title: "Cookie Policy",
  description:
    "How Zumud uses cookies and similar technologies, and how you can control them.",
  alternates: { canonical: "https://zumud.com/cookies" },
};

export default function CookiesPage() {
  return (
    <LegalPage
      title="Cookie Policy"
      lastUpdated="June 2026"
      intro="This Cookie Policy explains how Zumud uses cookies and similar technologies to run the service, remember your preferences, and understand how the product is used."
      sections={[
        {
          heading: "What cookies we use",
          paragraphs: [
            "Essential cookies that keep you signed in and keep the service secure. These are required for Zumud to work.",
            "Preference cookies that remember choices such as your light or dark theme.",
            "Analytics cookies that help us understand usage so we can improve the product.",
          ],
        },
        {
          heading: "Managing cookies",
          paragraphs: [
            "You can control or delete cookies through your browser settings. Note that disabling essential cookies may prevent parts of Zumud from working correctly.",
          ],
        },
        {
          heading: "Third-party cookies",
          paragraphs: [
            "Some cookies are set by trusted third parties we use for analytics, support chat, and payments. Their use of cookies is governed by their own policies.",
          ],
        },
      ]}
    />
  );
}
