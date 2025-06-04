import { 
  BrainIcon, 
  FileTextIcon, 
  TargetIcon, 
  TrendingUpIcon, 
  ShieldCheckIcon, 
  ClockIcon 
} from "lucide-react";

export default function FeaturesSection() {
  const features = [
    {
      icon: <BrainIcon className="h-8 w-8 text-blue-500" />,
      title: "AI-Powered Tailoring",
      description:
        "Our advanced AI analyzes job descriptions and optimizes your resume to match specific requirements and keywords.",
    },
    {
      icon: <FileTextIcon className="h-8 w-8 text-violet-500" />,
      title: "ATS Optimization",
      description:
        "Get past Applicant Tracking Systems with resumes formatted and optimized for maximum compatibility.",
    },
    {
      icon: <TargetIcon className="h-8 w-8 text-indigo-500" />,
      title: "Job Match Scoring",
      description:
        "See exactly how well your resume matches each job posting with our detailed compatibility scoring system.",
    },
    {
      icon: <TrendingUpIcon className="h-8 w-8 text-green-500" />,
      title: "Performance Analytics",
      description:
        "Track your application success rate and get insights on how to improve your resume performance.",
    },
    {
      icon: <ShieldCheckIcon className="h-8 w-8 text-orange-500" />,
      title: "Quality Assurance",
      description:
        "Every generated resume goes through quality checks to ensure professional formatting and content accuracy.",
    },
    {
      icon: <ClockIcon className="h-8 w-8 text-red-500" />,
      title: "Lightning Fast",
      description:
        "Generate a perfectly tailored resume in under 2 minutes. No more hours spent customizing applications.",
    },
  ];

  return (
    <section id="features" className="py-20 bg-white dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Features That Get You Hired
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            All the tools you need to create compelling resumes that stand out
            from the crowd and land you more interviews.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative p-6 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 hover:shadow-lg transition-all duration-300 hover:border-blue-200 dark:hover:border-blue-800"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-900/20 mb-4 group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex items-center rounded-full bg-blue-50 dark:bg-blue-900/20 px-6 py-2 text-sm text-blue-600 dark:text-blue-300 mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4 w-4 mr-2"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
            </svg>
            Trusted by 10,000+ job seekers
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Join thousands of professionals who have successfully landed their dream jobs
            using our AI-powered resume optimization platform.
          </p>
        </div>
      </div>
    </section>
  );
} 