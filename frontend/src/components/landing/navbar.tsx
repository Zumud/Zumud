"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Menu, X } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

interface NavbarProps {
  onAuthModalOpen?: (mode?: "login" | "signup") => void;
}

const NAV_LINKS = [
  { href: "#ats-friendly", label: "ATS friendly" },
  { href: "#latex", label: "LaTeX" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
];

export default function Navbar({ onAuthModalOpen }: NavbarProps) {
  const [userAuthenticated, setUserAuthenticated] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  // Reflect Supabase auth state on mount and whenever it changes.
  React.useEffect(() => {
    const supabase = createClient();

    supabase.auth.getSession().then(({ data }) => {
      setUserAuthenticated(!!data.session);
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setUserAuthenticated(!!session);
    });

    return () => {
      sub.subscription.unsubscribe();
    };
  }, []);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleSignup = React.useCallback(() => {
    onAuthModalOpen?.("signup");
  }, [onAuthModalOpen]);

  const handleLogin = React.useCallback(() => {
    onAuthModalOpen?.("login");
  }, [onAuthModalOpen]);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-300",
        scrolled
          ? "border-b border-border/60 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/65"
          : "border-b border-transparent bg-background/0"
      )}
    >
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center" aria-label="Zumud home">
            <img
              src="/logos/zumud/combined.svg"
              alt="Zumud"
              className="h-7 w-auto transition-opacity duration-200 hover:opacity-90"
            />
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <ThemeToggle />

          {userAuthenticated ? (
            <Button asChild variant="brand" className="hidden sm:inline-flex">
              <Link href="/dashboard">Dashboard</Link>
            </Button>
          ) : (
            <>
              <Button
                variant="ghost"
                onClick={handleLogin}
                className="hidden sm:inline-flex"
              >
                Sign in
              </Button>
              <Button variant="brand" onClick={handleSignup} className="hidden sm:inline-flex">
                Get started free
              </Button>
            </>
          )}

          {/* Mobile menu toggle */}
          <button
            type="button"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((v) => !v)}
            className="inline-flex size-9 items-center justify-center rounded-full border border-border/70 bg-background/60 text-foreground/80 backdrop-blur transition-colors hover:bg-accent hover:text-accent-foreground md:hidden"
          >
            {mobileOpen ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu panel */}
      <div
        className={cn(
          "overflow-hidden border-t border-border/60 bg-background/95 backdrop-blur-xl transition-[max-height,opacity] duration-300 md:hidden",
          mobileOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="container-page flex flex-col gap-1 py-4">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="rounded-lg px-3 py-2.5 text-sm font-medium text-foreground/90 transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              {link.label}
            </Link>
          ))}
          <div className="mt-2 flex flex-col gap-2">
            {userAuthenticated ? (
              <Button asChild variant="brand" className="w-full">
                <Link href="/dashboard">Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setMobileOpen(false);
                    handleLogin();
                  }}
                >
                  Sign in
                </Button>
                <Button
                  variant="brand"
                  className="w-full"
                  onClick={() => {
                    setMobileOpen(false);
                    handleSignup();
                  }}
                >
                  Get started free
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
