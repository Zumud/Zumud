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
        <div className="mx-auto mb-14 max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple pricing
          </h2>
          <p className="mt-3 text-lg text-muted-foreground">
            Start free. Pay only when it helps.
          </p>
        </div>

        <div className="mx-auto grid max-w-4xl grid-cols-1 items-stretch gap-6 md:grid-cols-2">
          {/* Free trial (featured) */}
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
                  <span className="ml-2 text-sm text-muted-foreground">per generation</span>
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

        <div className="mx-auto mt-10 flex max-w-4xl items-center justify-center gap-2 rounded-2xl border border-brand/15 bg-brand/5 px-5 py-4 text-center">
          <SparklesIcon className="size-5 shrink-0 text-brand" />
          <p className="font-medium">Try it first. Pay only when it helps.</p>
        </div>
      </div>
    </section>
  );
}
