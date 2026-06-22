import { Button } from "@/components/ui/button";
import { CheckIcon, GiftIcon, SparklesIcon } from "lucide-react";
import { PRICING_PLANS } from "@/data/pricing-data";

interface PricingSectionProps {
  onAuthModalOpen?: (mode?: "login" | "signup") => void;
}

export default function PricingSection({ onAuthModalOpen }: PricingSectionProps) {
  const freePlan = PRICING_PLANS.find((plan) => plan.id === "free");
  const paygPlan = PRICING_PLANS.find((plan) => plan.id === "payg");

  return (
    <section id="pricing" className="section scroll-mt-20">
      <div className="container-page">
        {/* Header */}
        <div className="mx-auto mb-14 max-w-2xl text-center">
          <span className="badge-soft mb-4">Pricing</span>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start with{" "}
            <span className="font-semibold text-foreground">10 free generations</span>
            , then just €0.10 each. No subscriptions, no hidden fees.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="mx-auto grid max-w-4xl grid-cols-1 items-stretch gap-6 lg:grid-cols-2">
          {/* Free Trial — featured */}
          {freePlan && (
            <div className="surface relative flex flex-col p-7 ring-2 ring-brand md:p-8">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-gradient px-4 py-1.5 text-xs font-semibold text-white shadow-sm">
                  <GiftIcon className="size-3.5" />
                  {freePlan.highlight}
                </span>
              </div>

              <div className="mt-3 text-center">
                <h3 className="text-xl font-semibold">{freePlan.name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {freePlan.description}
                </p>
                <div className="mt-6">
                  <span className="text-5xl font-bold tracking-tight text-brand-gradient">
                    Free
                  </span>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {freePlan.generations} generations · no credit card
                  </p>
                </div>
              </div>

              <ul className="mt-7 space-y-3">
                {freePlan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm">
                    <CheckIcon className="mt-0.5 size-4 shrink-0 text-brand" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant="brand"
                size="lg"
                className="mt-7 w-full"
                onClick={() => onAuthModalOpen?.("signup")}
              >
                {freePlan.cta}
              </Button>
            </div>
          )}

          {/* Pay As You Go */}
          {paygPlan && (
            <div className="surface relative flex flex-col p-7 md:p-8">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-4 py-1.5 text-xs font-semibold text-secondary-foreground">
                  {paygPlan.highlight}
                </span>
              </div>

              <div className="mt-3 text-center">
                <h3 className="text-xl font-semibold">{paygPlan.name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {paygPlan.description}
                </p>
                <div className="mt-6">
                  <span className="text-5xl font-bold tracking-tight">
                    €{paygPlan.price.toFixed(2)}
                  </span>
                  <p className="mt-2 text-sm text-muted-foreground">
                    per generation · pay only when you use it
                  </p>
                </div>
              </div>

              <ul className="mt-7 space-y-3">
                {paygPlan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm">
                    <CheckIcon className="mt-0.5 size-4 shrink-0 text-[var(--accent2)]" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant="outline"
                size="lg"
                className="mt-7 w-full"
                onClick={() => onAuthModalOpen?.("signup")}
              >
                {paygPlan.cta}
              </Button>
            </div>
          )}
        </div>

        {/* Value proposition */}
        <div className="mx-auto mt-12 max-w-4xl">
          <div className="bg-brand-gradient-soft rounded-2xl border border-border/60 p-8 text-center">
            <div className="mb-3 flex items-center justify-center gap-2">
              <SparklesIcon className="size-5 text-brand" />
              <h3 className="text-lg font-semibold">
                Why start with 10 free generations?
              </h3>
            </div>
            <p className="mx-auto max-w-2xl leading-relaxed text-muted-foreground">
              We&apos;re confident you&apos;ll love the results. Try Zumud completely free
              with 10 generations to see how much stronger your applications can be —
              no credit card, no strings attached.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-6 text-center sm:grid-cols-3">
            <div>
              <div className="text-2xl font-bold text-brand-gradient">100% free trial</div>
              <p className="mt-1 text-sm text-muted-foreground">
                10 generations, no card
              </p>
            </div>
            <div>
              <div className="text-2xl font-bold text-brand-gradient">Fair pricing</div>
              <p className="mt-1 text-sm text-muted-foreground">
                Just €0.10 after your trial
              </p>
            </div>
            <div>
              <div className="text-2xl font-bold text-brand-gradient">No subscriptions</div>
              <p className="mt-1 text-sm text-muted-foreground">
                Pay only when you generate
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
