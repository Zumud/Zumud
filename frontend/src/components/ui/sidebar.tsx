import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  History,
  BarChart3,
  User,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface SidebarProps {
  onLogout: () => void;
  className?: string;
}

interface SidebarItem {
  icon: React.ElementType;
  label: string;
  href?: string;
  onClick?: () => void;
  variant?: "default" | "destructive";
}

export default function Sidebar({ onLogout, className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(true); // Default to collapsed
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const router = useRouter();

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
      icon: LogOut,
      label: "Logout",
      onClick: onLogout,
      variant: "destructive",
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

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden fixed top-4 left-4 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm shadow-lg"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
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
          "fixed left-0 top-0 h-full bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-r border-gray-200/50 dark:border-gray-700/50 transition-all duration-300 z-50",
          isCollapsed ? "w-16" : "w-64",
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          className
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200/50 dark:border-gray-700/50">
            {!isCollapsed && (
              <div className="flex items-center space-x-2">
                <img 
                  src="/logos/zumud/combined.svg" 
                  alt="Zumud" 
                  className="h-6 w-auto"
                />
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="hidden md:flex"
              onClick={() => setIsCollapsed(!isCollapsed)}
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Navigation items */}
          <nav className="flex-1 p-4 space-y-2">
            {sidebarItems.map((item, index) => (
              <Button
                key={index}
                variant={item.variant === "destructive" ? "ghost" : "ghost"}
                size="sm"
                className={cn(
                  "w-full justify-start gap-3 h-10 px-3 text-left font-medium transition-colors",
                  isCollapsed && "justify-center px-2",
                  item.variant === "destructive" && "text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
                )}
                onClick={() => handleItemClick(item)}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {!isCollapsed && (
                  <span className="truncate">{item.label}</span>
                )}
              </Button>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50">
            {!isCollapsed && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Ready to create your next tailored document
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main content offset */}
      <div className={cn("transition-all duration-300", isCollapsed ? "md:ml-16" : "md:ml-64")} />
    </>
  );
} 