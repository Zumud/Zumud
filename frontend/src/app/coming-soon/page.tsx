import { Button } from "@/components/ui/button"
import { ArrowLeft, Wrench, Clock, Star } from "lucide-react"
import Link from "next/link"

export default function ComingSoon() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50/30 dark:from-gray-950 dark:to-blue-950/30 flex items-center justify-center p-4">
      {/* Decorative background elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-48 w-48 md:h-64 md:w-64 rounded-full bg-blue-200/10 blur-3xl dark:bg-blue-900/10"></div>
        <div className="absolute right-1/4 bottom-1/3 h-64 w-64 md:h-96 md:w-96 rounded-full bg-purple-200/10 blur-3xl dark:bg-purple-900/10"></div>
      </div>

      <div className="max-w-md w-full text-center">
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-8">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-full">
              <Wrench className="h-12 w-12 text-white" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent mb-4">
            Coming Soon
          </h1>

          {/* Description */}
          <p className="text-gray-600 dark:text-gray-400 mb-8 leading-relaxed">
            We're working hard to bring you amazing new features! This section will be available soon with exciting functionality to enhance your experience.
          </p>

          {/* Features preview */}
          <div className="space-y-3 mb-8">
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Clock className="h-4 w-4" />
              <span>Enhanced user experience</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Star className="h-4 w-4" />
              <span>Powerful new tools</span>
            </div>
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Wrench className="h-4 w-4" />
              <span>Advanced customization</span>
            </div>
          </div>

          {/* Back button */}
          <Link href="/dashboard">
            <Button className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
} 