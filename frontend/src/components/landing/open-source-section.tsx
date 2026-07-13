import { GithubIcon } from "@/components/icons/github-icon";
import { Button } from "@/components/ui/button";

const GITHUB_URL = "https://github.com/Zumud/Zumud";

export default function OpenSourceSection() {
  return (
    <section id="open-source" className="section scroll-mt-20">
      <div className="container-page">
        <div className="surface mx-auto max-w-3xl px-6 py-14 text-center md:px-12 md:py-16">
          <span className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-background px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand">
            <GithubIcon className="size-3.5" />
            Open source
          </span>

          <h2 className="mt-6 text-3xl font-bold tracking-tight sm:text-4xl">
            Trust shouldn&apos;t require faith.
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-muted-foreground">
            The same engine our users credit for{" "}
            <span className="font-semibold text-foreground">3× more interviews</span>{" "}
            is fully open — every line auditable, your data yours, self-hostable
            whenever you want. No hidden logic, no lock-in.
          </p>

          <Button asChild variant="brand" size="xl" className="mt-8 w-full font-semibold sm:w-auto">
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
              <GithubIcon className="size-5" />
              Star us on GitHub
            </a>
          </Button>

          <p className="mt-5 text-sm text-muted-foreground">
            AGPL-3.0 · Self-host it · Own your data
          </p>
        </div>
      </div>
    </section>
  );
}
