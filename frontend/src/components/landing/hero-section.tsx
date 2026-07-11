import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  Clock3,
  Loader2,
  MousePointerClick,
  ShieldCheck,
  Upload,
  X,
  Zap,
} from "lucide-react";
import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { applications } from "@/lib/api";
import ResumeProgress from "@/components/ui/resume-progress";

// Move large constants outside component to prevent recreation on every render
const SAMPLE_RESUME = `John Smith
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

const SAMPLE_JOB_DESCRIPTION = `Senior Frontend Developer - Remote
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

export default function HeroSection() {
  const router = useRouter();
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('That needs to be a PDF.');
      return;
    }

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('That file is over the 5MB limit.');
      return;
    }

    // Store the file and clear any existing text
    setError(null);
    setResumeFile(file);
    setResumeText("");
  };

  const handleUseSampleResume = () => {
    setResumeText(SAMPLE_RESUME);
  };

  const handleUseSampleJob = () => {
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
  };

  const handleGetTailoredResume = async () => {
    // Check if we have either text or file
    const hasResumeContent = resumeText.trim() || resumeFile;
    
    if (!hasResumeContent || !jobDescription.trim()) {
      setError("Add a resume and job post.");
      return;
    }

    // Show progress modal and start generation in background
    setError(null);
    setShowProgress(true);
    setIsGenerating(true);
    
    try {
      // Generate the resume and get the session data
      const result = await applications.generateAnonymousResume(
        resumeText.trim() || null, 
        jobDescription, 
        resumeFile || undefined
      );
      
      // Store the PDF data in sessionStorage for the preview page
      sessionStorage.setItem(`resume_pdf_${result.session_id}`, result.pdf_base64);
      sessionStorage.setItem(`resume_info_${result.session_id}`, JSON.stringify({
        company_name: result.company_name,
        generated_at: result.generated_at,
        filename: result.filename
      }));
      
      // Wait for progress animation to complete before redirecting
      // The progress component will call handleProgressComplete when done
      
    } catch (err) {
      console.error('Error generating resume:', err);
      setShowProgress(false);
      setIsGenerating(false);
      setError('Something went wrong. Please try again.');
    }
  };

  const handleProgressComplete = () => {
    setShowProgress(false);
    setIsGenerating(false);
    
    // Find the stored session data and redirect
    const keys = Object.keys(sessionStorage);
    const resumePdfKey = keys.find(key => key.startsWith('resume_pdf_'));
    if (resumePdfKey) {
      const sessionId = resumePdfKey.replace('resume_pdf_', '');
      router.push(`/resume/${sessionId}`);
    }
  };

  const handleProgressClose = () => {
    setShowProgress(false);
    setIsGenerating(false);
  };

  return (
    <section id="hero" className="ambient-glow relative overflow-hidden pb-16 pt-14 md:pb-24 md:pt-20">
      {/* Subtle grid texture behind the hero */}
      <div className="bg-grid pointer-events-none absolute inset-0 -z-10" aria-hidden="true" />

      <div className="container-page">
        {/* Headline */}
        <div className="mx-auto mb-10 max-w-3xl text-center md:mb-14">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            <span className="text-brand-gradient">Instant job-specific resumes</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-muted-foreground sm:text-lg">
            Our users report 3× more interviews and save 15+ minutes per application.
          </p>
        </div>

        {/* Action form */}
        <div id="hero-form" className="mx-auto max-w-5xl scroll-mt-24">
          <div className="surface p-5 shadow-xl shadow-brand/5 md:p-8">
            {error && (
              <div
                role="alert"
                className="mb-5 flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
              >
                <AlertCircle className="size-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div className="flex flex-col gap-5 lg:flex-row lg:gap-6">
              {/* Resume Input */}
              <div className="flex-1">
                <div className="mb-2.5 flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm font-semibold">
                    <span className="size-2 rounded-full bg-brand" />
                    Your resume
                  </label>
                  <button
                    type="button"
                    onClick={handleUseSampleResume}
                    className="rounded-md px-2 py-1 text-xs font-medium text-brand transition-colors hover:bg-brand/10"
                  >
                    Use sample
                  </button>
                </div>
                <div className="relative">
                  <textarea
                    value={resumeFile ? `📄 ${resumeFile.name} uploaded` : resumeText}
                    onChange={(e) => {
                      setResumeText(e.target.value);
                      setError(null);
                      if (resumeFile) {
                        setResumeFile(null);
                      }
                    }}
                    placeholder="Paste your resume or upload a PDF"
                    rows={6}
                    className="field resize-none pr-14"
                    disabled={!!resumeFile}
                  />
                  {resumeFile ? (
                    <button
                      type="button"
                      onClick={() => {
                        setResumeFile(null);
                        if (fileInputRef.current) {
                          fileInputRef.current.value = "";
                        }
                      }}
                      className="absolute bottom-3 right-3 inline-flex size-9 items-center justify-center rounded-lg bg-destructive text-white shadow-sm transition-transform hover:scale-105"
                      title="Remove PDF and switch to text input"
                      aria-label="Remove uploaded PDF"
                    >
                      <X className="size-4" />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="absolute bottom-3 right-3 inline-flex size-9 items-center justify-center rounded-lg bg-brand-gradient text-white shadow-sm transition-transform hover:scale-105"
                      title="Upload PDF resume"
                      aria-label="Upload PDF resume"
                    >
                      <Upload className="size-4" />
                    </button>
                  )}
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
                <div className="mb-2.5 flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm font-semibold">
                    <span className="size-2 rounded-full bg-[var(--accent2)]" />
                    Job description
                  </label>
                  <button
                    type="button"
                    onClick={handleUseSampleJob}
                    className="rounded-md px-2 py-1 text-xs font-medium text-[var(--accent2)] transition-colors hover:bg-[var(--accent2)]/10"
                  >
                    Use sample
                  </button>
                </div>
                <textarea
                  value={jobDescription}
                  onChange={(e) => {
                    setJobDescription(e.target.value);
                    setError(null);
                  }}
                  placeholder="Paste the job description"
                  rows={6}
                  className="field resize-none"
                />
              </div>
            </div>

            {/* Action Button */}
            <Button
              size="xl"
              variant="brand"
              onClick={handleGetTailoredResume}
              disabled={isGenerating}
              className="mt-5 w-full text-base font-semibold"
            >
              {isGenerating && !showProgress ? (
                <>
                  <Loader2 className="size-5 animate-spin" />
                  Starting…
                </>
              ) : (
                <>
                  <Zap className="size-5" />
                  Build my free resume
                </>
              )}
            </Button>

            {/* Trust indicators */}
            <div className="mt-6 border-t border-border/60 pt-5">
              <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
                <span className="inline-flex items-center gap-1.5">
                  <ShieldCheck className="size-4 text-brand" />
                  ATS-ready
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <Clock3 className="size-4 text-brand" />
                  Ready in 30 seconds
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <MousePointerClick className="size-4 text-brand" />
                  No sign-up
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Modal */}
      <ResumeProgress
        isVisible={showProgress}
        onComplete={handleProgressComplete}
        onClose={handleProgressClose}
      />
    </section>
  );
}
