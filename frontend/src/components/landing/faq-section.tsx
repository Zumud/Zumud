import React from "react";
import { Plus } from "lucide-react";

const FAQ_ITEMS = [
  {
    question: "How long does it take?",
    answer: "About 30 seconds.",
  },
  {
    question: "Do I need an account?",
    answer: "No. Try it here. Sign up only to save your work.",
  },
  {
    question: "Is the resume ATS friendly?",
    answer: "Yes. It uses clean structure and job-matched keywords.",
  },
  {
    question: "Can I use it for different jobs?",
    answer: "Yes. Paste a new job post and generate again.",
  },
  {
    question: "Can it write cover letters?",
    answer: "Yes. It uses your resume and the job post.",
  },
  {
    question: "What can I download?",
    answer: "PDF, LaTeX, or Overleaf.",
  },
  {
    question: "How much does it cost?",
    answer: "10 free. Then €0.10 each.",
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
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Common questions
          </h2>
          <p className="mt-3 text-lg text-muted-foreground">
            Quick answers.
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
