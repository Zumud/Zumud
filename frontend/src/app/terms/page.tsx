import type { Metadata } from "next";
import LegalPage from "@/components/legal/legal-page";

export const metadata: Metadata = {
  title: "Terms of Service",
  description:
    "The terms and conditions for using Zumud's AI resume and cover letter generation service.",
  alternates: { canonical: "https://zumud.com/terms" },
};

export default function TermsPage() {
  return (
    <LegalPage
      title="Terms of Service"
      lastUpdated="June 2026"
      intro="These Terms of Service govern your use of Zumud. By creating an account or using the service, you agree to these terms."
      sections={[
        {
          heading: "Using Zumud",
          paragraphs: [
            "You must provide accurate information and be responsible for the content you submit. You agree not to misuse the service or attempt to disrupt it.",
            "New accounts include a number of free generations. Additional usage is billed on a pay-as-you-go basis at the rate shown at checkout.",
          ],
        },
        {
          heading: "Your content",
          paragraphs: [
            "You retain ownership of the resume content and job descriptions you provide, and of the documents Zumud generates for you.",
            "You grant us the limited rights needed to process your content and deliver the service.",
          ],
        },
        {
          heading: "AI-generated output",
          paragraphs: [
            "Zumud uses AI to generate documents. While we aim for high quality, you are responsible for reviewing all output for accuracy before using it in an application.",
          ],
        },
        {
          heading: "Billing and refunds",
          paragraphs: [
            "Paid usage is charged through our payment provider. Pricing is shown before you generate. Contact us if you believe you were charged in error.",
          ],
        },
        {
          heading: "Changes and termination",
          paragraphs: [
            "We may update these terms or the service over time. We may suspend or terminate accounts that violate these terms. You can stop using Zumud at any time.",
          ],
        },
      ]}
    />
  );
}
