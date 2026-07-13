import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { MDXRemote } from "next-mdx-remote-client/rsc";
import remarkGfm from "remark-gfm";
import { ArrowLeft } from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import Footer from "@/components/landing/footer";
import { getGuide, getGuides } from "@/lib/guides";

interface GuidePageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return getGuides().map(({ slug }) => ({ slug }));
}

export async function generateMetadata({
  params,
}: GuidePageProps): Promise<Metadata> {
  const { slug } = await params;
  const guide = getGuide(slug);
  if (!guide) return {};
  const { meta } = guide;
  const url = `https://zumud.com/guides/${meta.slug}`;
  return {
    title: meta.title,
    description: meta.description,
    alternates: { canonical: url },
    openGraph: {
      title: meta.title,
      description: meta.description,
      url,
      type: "article",
      publishedTime: meta.datePublished,
      modifiedTime: meta.dateModified,
    },
  };
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default async function GuidePage({ params }: GuidePageProps) {
  const { slug } = await params;
  const guide = getGuide(slug);
  if (!guide) notFound();
  const { meta, source } = guide;
  const url = `https://zumud.com/guides/${meta.slug}`;

  const structuredData: object[] = [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: meta.title,
      description: meta.description,
      url,
      datePublished: meta.datePublished,
      dateModified: meta.dateModified,
      author: { "@type": "Organization", name: "Zumud", url: "https://zumud.com" },
      publisher: { "@id": "https://zumud.com/#organization" },
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: "https://zumud.com" },
        { "@type": "ListItem", position: 2, name: "Guides", item: "https://zumud.com/guides" },
        { "@type": "ListItem", position: 3, name: meta.title, item: url },
      ],
    },
  ];
  if (meta.faq?.length) {
    structuredData.push({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: meta.faq.map((item) => ({
        "@type": "Question",
        name: item.q,
        acceptedAnswer: { "@type": "Answer", text: item.a },
      })),
    });
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="container-page flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center" aria-label="Zumud home">
            <img src="/logos/zumud/combined.svg" alt="Zumud" className="h-7 w-auto" />
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="flex-1">
        <article className="container-page max-w-3xl py-12 md:py-16">
          <Link
            href="/guides"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            All guides
          </Link>

          <h1 className="mt-6 text-3xl font-bold tracking-tight sm:text-4xl">
            {meta.title}
          </h1>
          <p className="mt-3 text-sm text-muted-foreground">
            By the Zumud Team · Published {formatDate(meta.datePublished)} ·
            Updated {formatDate(meta.dateModified)}
          </p>

          <div className="prose prose-neutral dark:prose-invert mt-8 max-w-none">
            <MDXRemote
              source={source}
              options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }}
            />
          </div>

          {meta.faq && meta.faq.length > 0 && (
            <section className="mt-12">
              <h2 className="text-2xl font-bold tracking-tight">
                Frequently asked questions
              </h2>
              <div className="mt-4 space-y-3">
                {meta.faq.map((item) => (
                  <details
                    key={item.q}
                    className="surface group overflow-hidden [&_summary::-webkit-details-marker]:hidden"
                  >
                    <summary className="cursor-pointer list-none p-5 font-medium">
                      {item.q}
                    </summary>
                    <div className="px-5 pb-5 text-muted-foreground">{item.a}</div>
                  </details>
                ))}
              </div>
            </section>
          )}

          <div className="mt-12 rounded-2xl border border-border/60 bg-muted/40 p-6 text-sm text-muted-foreground">
            Want this done for you?{" "}
            <Link href="/" className="font-medium text-brand hover:underline">
              Zumud tailors your resume to any job post
            </Link>{" "}
            in about 30 seconds — first 10 generations are free.
          </div>
        </article>
      </main>

      <Footer />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
    </div>
  );
}
