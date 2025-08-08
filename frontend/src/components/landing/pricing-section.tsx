import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckIcon, DollarSignIcon, ZapIcon, GiftIcon } from "lucide-react";
import { PRICING_PLANS } from "@/data/pricing-data";

interface PricingSectionProps {
  onAuthModalOpen?: (mode?: 'login' | 'signup') => void;
}

export default function PricingSection({ onAuthModalOpen }: PricingSectionProps) {
  const freePlan = PRICING_PLANS.find(plan => plan.id === "free");
  const paygPlan = PRICING_PLANS.find(plan => plan.id === "payg");

  return (
    <section id="pricing" className="py-24 bg-gradient-to-b from-white to-gray-50 dark:from-gray-950 dark:to-gray-900">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        {/* Header */}
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Start with <span className="font-semibold text-blue-600">10 FREE generations</span>, 
            then just €0.50 per generation. No subscriptions, no hidden fees.
          </p>
        </div>

        {/* Main Pricing Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
          {/* Free Trial - Featured */}
          {freePlan && (
            <Card className="relative border-2 border-blue-500 shadow-xl">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-gradient-to-r from-blue-600 to-violet-600 text-white px-6 py-2 rounded-full text-sm font-medium flex items-center gap-1">
                  <GiftIcon className="h-4 w-4" />
                  {freePlan.highlight}
                </span>
              </div>
              <CardHeader className="text-center pb-6 pt-8">
                <CardTitle className="text-2xl">{freePlan.name}</CardTitle>
                <CardDescription className="text-base">{freePlan.description}</CardDescription>
                <div className="mt-6">
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                      FREE
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    {freePlan.generations} generations
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    No credit card required
                  </p>
                </div>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-lg font-medium text-blue-600 mb-2">
                  Perfect for trying Zumud
                </p>
                <p className="text-sm text-muted-foreground">
                  Experience all features with 10 generations to see the difference Zumud makes.
                </p>
              </CardContent>
              <CardFooter className="pt-6">
                <Button 
                  className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-lg py-6"
                  onClick={() => onAuthModalOpen?.('signup')}
                >
                  {freePlan.cta}
                </Button>
              </CardFooter>
            </Card>
          )}

          {/* Pay As You Go */}
          {paygPlan && (
            <Card className="relative border border-gray-200 dark:border-gray-800">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-6 py-2 rounded-full text-sm font-medium">
                  {paygPlan.highlight}
                </span>
              </div>
              <CardHeader className="text-center pb-6 pt-8">
                <CardTitle className="text-2xl">{paygPlan.name}</CardTitle>
                <CardDescription className="text-base">{paygPlan.description}</CardDescription>
                <div className="mt-6">
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-5xl font-bold">
                      ${paygPlan.price}
                    </span>
                    <span className="text-lg text-muted-foreground">
                      per generation
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Each resume, cover letter, or edit
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Pay only when you generate
                  </p>
                </div>
              </CardHeader>
              <CardContent className="text-center">
                <p className="text-lg font-medium text-violet-600 mb-2">
                  Use when you need it
                </p>
                <p className="text-sm text-muted-foreground">
                  Generate resumes, cover letters, and job answers individually.
                </p>
              </CardContent>
              <CardFooter className="pt-6">
                <Button 
                  variant="outline"
                  className="w-full text-lg py-6 border-2 border-blue-200 hover:border-blue-300 dark:border-blue-800 dark:hover:border-blue-700"
                  onClick={() => onAuthModalOpen?.('signup')}
                >
                  {paygPlan.cta}
                </Button>
              </CardFooter>
            </Card>
          )}
        </div>

        {/* Value Proposition */}
        <div className="text-center max-w-4xl mx-auto">
          <div className="bg-blue-50 dark:bg-blue-950/30 rounded-2xl p-8 mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <GiftIcon className="h-6 w-6 text-blue-600" />
              <h3 className="text-xl font-semibold">Why start with 10 free generations?</h3>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              We're confident you'll love Zumud's results. Try it completely free with 10 generations 
              to see how much better your resumes can be. No credit card required, no strings attached.
            </p>
          </div>
          
          {/* Trust indicators */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">100% Free Trial</div>
              <p className="text-sm text-muted-foreground">10 generations, no credit card</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-violet-600 mb-1">Fair Pricing</div>
              <p className="text-sm text-muted-foreground">Just 10¢ after your free trial</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">No Subscriptions</div>
              <p className="text-sm text-muted-foreground">Pay only when you generate</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 