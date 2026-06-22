import React from "react";
import { Plus } from "lucide-react";

const FAQ_ITEMS = [
  {
    question: "How long does it take to tailor a resume?",
    answer:
      "About 30 seconds. Paste your resume and a job description, then download an ATS-ready PDF.",
  },
  {
    question: "Do I need to sign up to try it?",
    answer:
      "No. Generate your first resume right from the homepage. Sign up free to remove the watermark, save your work, and unlock cover letters.",
  },
  {
    question: "Is my resume optimized for ATS?",
    answer:
      "Yes. Clean formatting plus the job's own keywords get you past the bots to a human.",
  },
  {
    question: "Can I tailor a resume for different jobs?",
    answer:
      "That's the whole idea. Paste a new job description any time and we rewrite your resume for it. As often as you like.",
  },
  {
    question: "How much does it cost?",
    answer:
      "Your first 10 are free, no card required. After that it's €0.10 each. No subscriptions, no hidden fees.",
  },
  {
    question: "What can I download?",
    answer:
      "Download a polished PDF, export the LaTeX source, or open it straight in Overleaf.",
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
