import React from "react";
import { Plus } from "lucide-react";

const FAQ_ITEMS = [
  {
    question: "How long does it take to tailor a resume?",
    answer:
      "About 30 seconds. Paste your resume and a job description, and Zumud returns an ATS-optimized, job-specific resume you can download as a PDF right away.",
  },
  {
    question: "Do I need to sign up to try it?",
    answer:
      "No. You can generate your first tailored resume from the homepage without an account. Create a free account to remove the watermark, save your documents, and unlock cover letters and application answers.",
  },
  {
    question: "Is my resume optimized for ATS?",
    answer:
      "Yes. Every resume uses clean, parseable formatting and the keywords from the job description, so it gets through Applicant Tracking Systems and in front of a human.",
  },
  {
    question: "Can I tailor a resume for different jobs?",
    answer:
      "That's the whole idea. Paste a different job description each time and Zumud rewrites your resume for that specific role — as many times as you need.",
  },
  {
    question: "How much does it cost?",
    answer:
      "Your first 10 generations are completely free, with no credit card required. After that it's pay-as-you-go at €0.10 per generation — no subscriptions and no hidden fees.",
  },
  {
    question: "What can I download?",
    answer:
      "You can download your resume as a polished PDF, export the LaTeX (TeX) source, or open it directly in Overleaf to fine-tune the design.",
  },
];

const faqStructuredData = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: FAQ_ITEMS.map((item) => ({
    "@type": "Question",
    name: item.question,
    acceptedAnswer: {
      "@type": "Answer",
      text: item.answer,
    },
  })),
};

function FaqSection() {
  return (
    <section id="faq" className="section scroll-mt-20 bg-muted/30">
      <div className="container-page max-w-3xl">
        <div className="mb-12 text-center">
          <span className="badge-soft mb-4">FAQ</span>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know about tailoring resumes with Zumud.
          </p>
        </div>

        <div className="space-y-3">
          {FAQ_ITEMS.map((item, index) => (
            <details
              key={index}
              className="surface group overflow-hidden [&_summary::-webkit-details-marker]:hidden"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5 font-medium">
                <span>{item.question}</span>
                <Plus className="size-5 shrink-0 text-brand transition-transform duration-300 group-open:rotate-45" />
              </summary>
              <div className="px-5 pb-5 text-muted-foreground">{item.answer}</div>
            </details>
          ))}
        </div>
      </div>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqStructuredData) }}
      />
    </section>
  );
}

export default React.memo(FaqSection);
