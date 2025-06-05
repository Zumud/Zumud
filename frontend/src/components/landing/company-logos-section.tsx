import { BriefcaseIcon } from "lucide-react";

export default function CompanyLogosSection() {
  return (
    <section className="py-16 bg-white dark:bg-gray-950 border-b border-gray-100 dark:border-gray-800">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent mb-12">
            Your next interview could be at one of these
          </h2>
          
          <div className="flex justify-center items-center space-x-8 md:space-x-12 opacity-70 flex-wrap gap-y-6">
            
            {/* Google */}
            <img 
              src="/logos/google.svg" 
              alt="Google" 
              className="h-8 w-auto hover:opacity-100 transition-opacity duration-300"
            />

            {/* Microsoft */}
            <img 
              src="/logos/microsoft.svg" 
              alt="Microsoft" 
              className="h-8 w-auto hover:opacity-100 transition-opacity duration-300"
            />

            {/* Amazon */}
            <img 
              src="/logos/amazon.svg" 
              alt="Amazon" 
              className="h-8 w-auto hover:opacity-100 transition-opacity duration-300"
            />

            {/* Meta */}
            <img 
              src="/logos/meta.svg" 
              alt="Meta" 
              className="h-8 w-auto hover:opacity-100 transition-opacity duration-300"
            />

            {/* Apple */}
            <img 
              src="/logos/apple.svg" 
              alt="Apple" 
              className="h-10 w-auto hover:opacity-100 transition-opacity duration-300"
            />

          </div>
        </div>
      </div>
    </section>
  );
} 