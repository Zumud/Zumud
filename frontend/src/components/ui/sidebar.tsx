"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  History,
  BarChart3,
  User,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  CreditCard
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePathname, useRouter } from "next/navigation";
import { billing } from "@/lib/api";
import { ThemeToggle } from "@/components/theme/theme-toggle";

interface SidebarProps {
  onLogout: () => void;
  className?: string;
}

interface SidebarItem {
  icon: React.ElementType;
  label: string;
  href?: string;
  onClick?: () => void;
}

export default function Sidebar({ onLogout, className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(true); // Default to collapsed
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isLoadingPortal, setIsLoadingPortal] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const handleManageSubscription = async () => {
    try {
      setIsLoadingPortal(true);
      const response = await billing.createCustomerPortalSession();
      
      if (response && response.portal_url) {
        // Redirect to Stripe Customer Portal
        window.location.assign(response.portal_url);
      } else {
        console.error('No portal URL received from API');
        alert('Unable to open billing portal. Please try again.');
      }
    } catch (error) {
      console.error('Failed to create customer portal session:', error);
      alert('Unable to open billing portal. Please try again.');
    } finally {
      setIsLoadingPortal(false);
    }
  };

  const sidebarItems: SidebarItem[] = [
    {
      icon: BarChart3,
      label: "Dashboard",
      href: "/dashboard",
    },
    {
      icon: History,
      label: "History",
      href: "/history",
    },
    {
      icon: User,
      label: "Profile",
      href: "/profile",
    },
    {
      icon: CreditCard,
      label: "Manage Subscription",
      onClick: handleManageSubscription,
    },
  ];

  const handleItemClick = (item: SidebarItem) => {
    if (item.onClick) {
      item.onClick();
    } else if (item.href) {
      router.push(item.href);
    }
    // Close mobile menu after clicking
    setIsMobileOpen(false);
  };

  const isItemActive = (item: SidebarItem) =>
    Boolean(item.href && (pathname === item.href || pathname.startsWith(`${item.href}/`)));

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="outline"
        size="icon"
        className="md:hidden fixed top-4 left-4 z-50 bg-background/90 backdrop-blur-sm shadow-lg"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        aria-label="Toggle navigation menu"
      >
        {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-full border-r border-sidebar-border bg-sidebar/95 shadow-sm backdrop-blur-sm transition-all duration-300",
          isCollapsed ? "w-16" : "w-64",
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          className
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className={cn(
            "flex h-16 items-center border-b border-sidebar-border px-3",
            isCollapsed ? "justify-center" : "justify-between"
          )}>
            {!isCollapsed && (
              <div className="flex min-w-0 items-center">
                <img
                  src="/logos/zumud/combined.svg"
                  alt="Zumud"
                  className="h-7 w-auto"
                />
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="hidden rounded-xl text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground md:flex"
              onClick={() => setIsCollapsed(!isCollapsed)}
              aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Appearance */}
          <div className="border-b border-sidebar-border p-3">
            {!isCollapsed && (
              <p className="mb-2 px-2 text-[11px] font-semibold uppercase text-muted-foreground">
                Appearance
              </p>
            )}
            <ThemeToggle
              showLabel={!isCollapsed}
              className={cn(
                "h-10 rounded-xl border-transparent bg-sidebar-accent/60 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                isCollapsed ? "mx-auto w-10" : "justify-start"
              )}
            />
          </div>

          {/* Navigation items */}
          <nav className="flex-1 space-y-1.5 p-3">
            {sidebarItems.map((item) => {
              const isActive = isItemActive(item);

              return (
                <Button
                  key={item.label}
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "h-10 w-full justify-start gap-3 rounded-xl px-3 text-left font-medium text-sidebar-foreground/75 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    isCollapsed && "justify-center px-2",
                    isActive && "bg-sidebar-primary/10 text-sidebar-primary shadow-sm dark:bg-sidebar-primary/15"
                  )}
                  onClick={() => handleItemClick(item)}
                  disabled={item.label === "Manage Subscription" && isLoadingPortal}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="truncate">
                      {item.label === "Manage Subscription" && isLoadingPortal ? "Opening..." : item.label}
                    </span>
                  )}
                </Button>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-sidebar-border p-3">
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                "h-10 w-full justify-start gap-3 rounded-xl px-3 font-medium text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/20 dark:hover:text-red-300",
                isCollapsed && "justify-center px-2"
              )}
              onClick={onLogout}
            >
              <LogOut className="h-4 w-4 flex-shrink-0" />
              {!isCollapsed && <span>Logout</span>}
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content offset */}
      <div className={cn("transition-all duration-300", isCollapsed ? "md:ml-16" : "md:ml-64")} />
    </>
  );
} 
