import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRightIcon, PlayIcon, Upload, FileText } from "lucide-react";
import { useState, useRef } from "react";

interface HeroSectionProps {
  onAuthModalOpen?: (mode?: 'login' | 'signup') => void;
}

export default function HeroSection({ onAuthModalOpen }: HeroSectionProps) {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sampleResume = `John Smith
Software Developer | john.smith@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith

EXPERIENCE
Senior Software Developer | TechCorp Inc. | 2021 - Present
• Developed and maintained web applications using React, Node.js, and PostgreSQL
• Led a team of 4 developers on a customer portal project, improving user engagement by 35%
• Implemented CI/CD pipelines using Docker and AWS, reducing deployment time by 50%
• Collaborated with product managers and designers to deliver features on time

Software Developer | StartupXYZ | 2019 - 2021
• Built responsive web applications using JavaScript, HTML5, and CSS3
• Integrated third-party APIs and payment systems (Stripe, PayPal)
• Optimized database queries resulting in 40% faster page load times
• Participated in agile development processes and code reviews

TECHNICAL SKILLS
• Languages: JavaScript, Python, TypeScript, Java
• Frontend: React, Vue.js, HTML5, CSS3, Tailwind CSS
• Backend: Node.js, Express, Django, Spring Boot
• Databases: PostgreSQL, MongoDB, MySQL
• Tools: Git, Docker, AWS, Jenkins, Jira

EDUCATION
Bachelor of Science in Computer Science | State University | 2019
• GPA: 3.7/4.0, Dean's List (3 semesters)
• Relevant coursework: Data Structures, Algorithms, Software Engineering`;

  const sampleJobDescription = `Senior Frontend Developer - Remote
TechForward Solutions | $90,000 - $120,000

We're looking for a Senior Frontend Developer to join our growing team and help build the next generation of our SaaS platform.

RESPONSIBILITIES:
• Develop and maintain responsive web applications using React and TypeScript
• Collaborate with designers to implement pixel-perfect UI components
• Optimize application performance and ensure cross-browser compatibility
• Mentor junior developers and conduct code reviews
• Work closely with backend engineers to integrate APIs
• Participate in agile development processes and sprint planning

REQUIRED QUALIFICATIONS:
• 4+ years of experience in frontend development
• Strong proficiency in React, JavaScript, and TypeScript
• Experience with modern CSS frameworks (Tailwind CSS, Styled Components)
• Knowledge of state management libraries (Redux, Zustand)
• Experience with testing frameworks (Jest, React Testing Library)
• Familiarity with version control systems (Git)
• Strong problem-solving skills and attention to detail

PREFERRED QUALIFICATIONS:
• Experience with Next.js or other React frameworks
• Knowledge of backend technologies (Node.js, Python)
• Experience with cloud platforms (AWS, Azure, GCP)
• Familiarity with CI/CD pipelines
• Previous experience in a SaaS environment

BENEFITS:
• Competitive salary and equity package
• Comprehensive health, dental, and vision insurance
• Flexible work arrangements and unlimited PTO
• Professional development budget
• Latest MacBook Pro and equipment budget`;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      // For now, just set a placeholder text
      setResumeText(`${file.name} uploaded`);
    }
  };

  const handleUseSampleResume = () => {
    setResumeText(sampleResume);
  };

  const handleUseSampleJob = () => {
    setJobDescription(sampleJobDescription);
  };

  const handleGetTailoredResume = () => {
    if (!resumeText.trim() && !jobDescription.trim()) {
      alert("Please provide your resume and job description");
      return;
    }
    // For now, redirect to signup
    onAuthModalOpen?.('signup');
  };

  return (
    <section className="relative overflow-hidden py-16 md:py-24 lg:py-32 bg-gradient-to-b from-white to-blue-50 dark:from-gray-950 dark:to-blue-950">
      {/* Decorative elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-48 w-48 md:h-64 md:w-64 rounded-full bg-blue-200/30 blur-3xl dark:bg-blue-900/30"></div>
        <div className="absolute right-1/4 bottom-1/3 h-64 w-64 md:h-96 md:w-96 rounded-full bg-purple-200/30 blur-3xl dark:bg-purple-900/30"></div>
      </div>

      <div className="mx-auto max-w-7xl px-4 md:px-6">
        {/* Centered headline and subheadline */}
        <div className="text-center space-y-6 lg:space-y-8 mb-12">
          <div className="space-y-4 lg:space-y-6">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent leading-tight">
              Instant job-specific resumes
            </h1>
            <p className="text-base md:text-lg lg:text-xl text-gray-500 dark:text-gray-400 max-w-[800px] mx-auto">
              Our users report 3× more interviews — and save 15+ minutes per application
            </p>
          </div>
        </div>

                {/* Action form */}
        <div className="max-w-5xl mx-auto">
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/50 dark:border-gray-700/50 p-8 md:p-10">
            <div className="flex flex-col lg:flex-row gap-8">
              {/* Resume Input */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-sm font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    Your Resume
                  </label>
                  <button
                    type="button"
                    onClick={handleUseSampleResume}
                    className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 bg-blue-50 dark:bg-blue-900/30 px-3 py-1.5 rounded-lg transition-colors hover:bg-blue-100 dark:hover:bg-blue-900/50"
                  >
                    Use Sample
                  </button>
                </div>
                <div className="relative group">
                  <textarea
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    placeholder="Paste / upload your resume"
                    rows={5}
                    className="w-full px-6 py-5 text-base border-2 border-gray-200/60 dark:border-gray-700/60 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:bg-gray-800/50 dark:text-white dark:placeholder-gray-500 resize-none transition-all duration-300 shadow-sm hover:shadow-md group-hover:border-blue-300 dark:group-hover:border-blue-700"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute bottom-5 right-5 p-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 rounded-xl transition-all duration-200 hover:scale-110 shadow-lg hover:shadow-xl"
                    title="Upload PDF Resume"
                  >
                    <Upload className="h-5 w-5" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={handleFileUpload}
                  />
                </div>
              </div>

              {/* Job Description Input */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-sm font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <div className="w-2 h-2 bg-violet-500 rounded-full"></div>
                    Job Description
                  </label>
                  <button
                    type="button"
                    onClick={handleUseSampleJob}
                    className="text-xs font-medium text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 bg-violet-50 dark:bg-violet-900/30 px-3 py-1.5 rounded-lg transition-colors hover:bg-violet-100 dark:hover:bg-violet-900/50"
                  >
                    Use Sample
                  </button>
                </div>
                <div className="relative group">
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description"
                    rows={5}
                    className="w-full px-6 py-5 text-base border-2 border-gray-200/60 dark:border-gray-700/60 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:bg-gray-800/50 dark:text-white dark:placeholder-gray-500 resize-none transition-all duration-300 shadow-sm hover:shadow-md group-hover:border-blue-300 dark:group-hover:border-blue-700"
                  />
                </div>
              </div>

              {/* Action Button */}
              <div className="lg:w-auto w-full flex flex-col">
                {/* Match exact label structure and spacing */}
                <div className="flex items-center justify-between mb-4">
                  <div className="h-6"></div> {/* Invisible spacer matching label height */}
                </div>
                {/* Center button in textarea area */}
                <div className="relative flex items-center justify-center" style={{height: '165px'}}>
                  <Button
                    size="lg"
                    onClick={handleGetTailoredResume}
                    className="bg-gradient-to-r from-blue-600 via-blue-700 to-violet-600 hover:from-blue-700 hover:via-blue-800 hover:to-violet-700 hover:scale-105 active:scale-95 shadow-xl hover:shadow-2xl h-auto py-6 px-10 text-lg font-bold w-full lg:w-auto transition-all duration-300 rounded-2xl border border-white/20"
                  >
                    Free Tailored Resume
                  </Button>
                </div>
              </div>
            </div>
            
            {/* Trust indicators */}
            <div className="mt-8 pt-6 border-t border-gray-200/30 dark:border-gray-700/30">
              <div className="flex flex-wrap justify-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Instant results</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span>ATS-friendly</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                  <span>No signup required</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 