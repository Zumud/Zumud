"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { MoonIcon, SunIcon } from "lucide-react";
import { isAuthenticated } from "@/lib/utils";

interface NavbarProps {
  onAuthModalOpen?: (mode?: 'login' | 'signup') => void;
}

export default function Navbar({ onAuthModalOpen }: NavbarProps) {
  const [theme, setTheme] = React.useState<"light" | "dark">("light");
  const [userAuthenticated, setUserAuthenticated] = React.useState(false);

  // Check authentication status on mount and when localStorage changes
  React.useEffect(() => {
    const checkAuthStatus = () => {
      setUserAuthenticated(isAuthenticated());
    };
    
    checkAuthStatus();
    
    // Listen for storage changes to update auth state
    window.addEventListener('storage', checkAuthStatus);
    
    return () => {
      window.removeEventListener('storage', checkAuthStatus);
    };
  }, []);

  const toggleTheme = React.useCallback(() => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.documentElement.classList.toggle("dark");
  }, [theme]);

  const handleLogin = React.useCallback(() => {
    onAuthModalOpen?.('login');
  }, [onAuthModalOpen]);

  const handleSignup = React.useCallback(() => {
    onAuthModalOpen?.('signup');
  }, [onAuthModalOpen]);

  return (
    <div className="border-b bg-background sticky top-0 z-50 shadow-sm">
      <div className="mx-auto max-w-7xl flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-6 md:gap-10">
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-2xl bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
              Zumud
            </span>
          </Link>
          <NavigationMenu className="hidden md:flex">
            <NavigationMenuList>
              <NavigationMenuItem>
                <NavigationMenuTrigger>Features</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <ul className="grid gap-3 p-6 md:w-[400px] lg:w-[500px] lg:grid-cols-2">
                    <li className="row-span-3">
                      <NavigationMenuLink asChild>
                        <Link
                          className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-blue-50 to-violet-100 p-6 no-underline outline-none focus:shadow-md dark:from-blue-950 dark:to-violet-900"
                          href="#features"
                        >
                          <div className="mb-2 mt-4 text-lg font-medium text-blue-600 dark:text-blue-300">
                            AI-Powered Resume Builder
                          </div>
                          <p className="text-sm leading-tight text-blue-700/90 dark:text-blue-300/90">
                            Tailor your resume for every job application with
                            our advanced AI technology
                          </p>
                        </Link>
                      </NavigationMenuLink>
                    </li>
                    <ListItem href="#features" title="ATS Optimization">
                      Get past applicant tracking systems with optimized
                      keywords
                    </ListItem>
                    <ListItem href="#how-it-works" title="Resume Analysis">
                      Detailed feedback on how to improve your resume
                    </ListItem>
                    <ListItem href="#features" title="Job Match Score">
                      See how well your resume matches the job description
                    </ListItem>
                  </ul>
                </NavigationMenuContent>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink className={navigationMenuTriggerStyle()} asChild>
                  <Link href="#pricing">
                    Pricing
                  </Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink className={navigationMenuTriggerStyle()} asChild>
                  <Link href="#how-it-works">
                    How It Works
                  </Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Toggle theme"
            className="mr-2"
            onClick={toggleTheme}
          >
            {theme === "dark" ? (
              <SunIcon className="h-5 w-5" />
            ) : (
              <MoonIcon className="h-5 w-5" />
            )}
          </Button>
          {userAuthenticated ? (
            <Button asChild>
              <Link href="/dashboard">
                Dashboard
              </Link>
            </Button>
          ) : (
            <Button onClick={handleSignup}>
              Get Started Free
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

const ListItem = React.memo(React.forwardRef<
  React.ElementRef<typeof Link>,
  React.ComponentPropsWithoutRef<typeof Link> & {
    title: string;
  }
>(({ className, title, children, ...props }, ref) => {
  return (
    <li>
      <NavigationMenuLink asChild>
        <Link
          ref={ref}
          className={cn(
            "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
            className
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none">{title}</div>
          <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
            {children}
          </p>
        </Link>
      </NavigationMenuLink>
    </li>
  );
}));
ListItem.displayName = "ListItem"; 