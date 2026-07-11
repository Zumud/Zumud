"use client";

import * as React from "react";
import { MoonIcon, SunIcon } from "lucide-react";
import { cn } from "@/lib/utils";

type Theme = "light" | "dark";

function getInitialTheme(): Theme {
  if (typeof document === "undefined") return "light";
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

interface ThemeToggleProps {
  className?: string;
}

/**
 * Persistent, system-aware theme toggle. Reads the current theme from the
 * <html> class (set pre-paint by ThemeScript), writes the choice to
 * localStorage, and keeps `color-scheme` in sync so native controls match.
 */
export function ThemeToggle({ className }: ThemeToggleProps) {
  const [theme, setTheme] = React.useState<Theme>("light");
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: hydration mount-gate pattern
    setMounted(true);
    setTheme(getInitialTheme());
  }, []);

  const toggle = React.useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === "dark" ? "light" : "dark";
      const isDark = next === "dark";
      document.documentElement.classList.toggle("dark", isDark);
      document.documentElement.style.colorScheme = next;
      try {
        localStorage.setItem("theme", next);
      } catch {
        /* ignore */
      }
      return next;
    });
  }, []);

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      className={cn(
        "inline-flex size-9 items-center justify-center rounded-full border border-border/70 bg-background/60 text-foreground/80 shadow-xs backdrop-blur transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40",
        className
      )}
    >
      {/* Avoid hydration mismatch: render a stable icon until mounted */}
      {mounted && theme === "dark" ? (
        <SunIcon className="size-[1.15rem]" />
      ) : (
        <MoonIcon className="size-[1.15rem]" />
      )}
    </button>
  );
}

