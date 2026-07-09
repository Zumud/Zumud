import type { Metadata } from "next";
import LegalPage from "@/components/legal/legal-page";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "How Zumud collects, uses, and protects your personal data when you create AI-tailored resumes and cover letters.",
  alternates: { canonical: "https://zumud.com/privacy" },
};

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy Policy"
      lastUpdated="June 2026"
      intro="This Privacy Policy explains what information Zumud collects, how we use it, and the choices you have. We built Zumud to help you create better job applications, and we treat the data you share with care."
      sections={[
        {
          heading: "Information we collect",
          paragraphs: [
            "Account information such as your email address when you sign up, and authentication details when you sign in with Google.",
            "Content you provide, including resume text or PDFs and the job descriptions you paste in, which we use to generate your tailored documents.",
            "Usage data such as device and browser information and product analytics, used to improve the service.",
          ],
        },
        {
          heading: "How we use your information",
          paragraphs: [
            "To generate, store, and deliver the resumes, cover letters, and answers you request.",
            "To operate, secure, and improve Zumud, and to provide customer support.",
            "To process payments for pay-as-you-go usage through our payment provider.",
          ],
        },
        {
          heading: "How we share information",
          paragraphs: [
            "We do not sell your personal data. We share information only with service providers that help us run Zumud (for example, hosting, authentication, analytics, and payments), and only as needed to provide the service.",
          ],
        },
        {
          heading: "Data retention and your rights",
          paragraphs: [
            "You can request access to, correction of, or deletion of your personal data at any time by contacting us.",
            "We retain your content for as long as your account is active or as needed to provide the service, unless you ask us to delete it.",
          ],
        },
      ]}
    />
  );
}
