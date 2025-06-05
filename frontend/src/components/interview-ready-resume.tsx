"use client"

import type React from "react"
import { useState } from "react"
import { Check, Upload, Star, Users, TrendingUp, FileText, Zap, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

export default function InterviewReadyResume() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const features = [
    {
      icon: <FileText className="h-12 w-12 text-blue-600" />,
      title: "ATS-Specific Resumes",
      description: "Our AI creates resumes that are optimized for Application Tracking Systems, ensuring your resume gets past the initial screening."
    },
    {
      icon: <Zap className="h-12 w-12 text-blue-600" />,
      title: "ATS Optimization",
      description: "Get ATS-scan ready resumes that increase your chances of getting noticed by hiring managers and recruiters."
    },
    {
      icon: <Shield className="h-12 w-12 text-blue-600" />,
      title: "Perfect Guarantee",
      description: "Quality AI-scan ready in minutes that stand out from the competition and get you more interviews."
    }
  ]

  const steps = [
    "Start with personal info and work experience",
    "Add achievements and skills with precision",
    "AI tailors content with job-specific keywords",
    "Download your professional, ATS-ready resume"
  ]

  const faqItems = [
    {
      question: "How long does it take to create a resume?",
      answer: "With Zumud, you can create a professional, ATS-optimized resume in just 5-10 minutes. Our AI handles the formatting and optimization automatically."
    },
    {
      question: "Can I customize my resume for different jobs?",
      answer: "Absolutely! Zumud allows you to create multiple versions of your resume, each tailored to specific job descriptions and industries."
    },
    {
      question: "Is my personal information secure?",
      answer: "Yes, we take data security seriously. All your personal information is encrypted and stored securely. We never share your data with third parties."
    },
    {
      question: "What formats can I download my resume in?",
      answer: "You can download your resume in PDF format, which is the most widely accepted format by employers and ATS systems."
    },
    {
      question: "Do you offer a money-back guarantee?",
      answer: "Yes, we offer a 30-day money-back guarantee. If you're not satisfied with your resume, we'll refund your purchase."
    }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-purple-50 to-blue-50 pt-20 pb-32">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                AI-Powered Resumes, Job-Specific Results
        </h1>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Create job-specific resumes in minutes with our advanced AI technology. 
                Stand out from the competition and land more interviews with resumes that 
                are tailored to each position and optimized for ATS systems.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button 
                  size="lg" 
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all"
                  onClick={() => setShowAuthModal(true)}
                >
                  Build My Resume
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  className="border-2 border-gray-300 text-gray-700 px-8 py-6 text-lg font-semibold rounded-lg hover:bg-gray-50"
                >
                  See Examples
                </Button>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <div className="space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-blue-200 rounded w-5/6"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                  <div className="h-4 bg-gray-200 rounded w-4/5"></div>
                  <div className="h-4 bg-blue-200 rounded w-1/2"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              For job seekers who want to stand out
            </h2>
            <p className="text-xl text-gray-600">
              Our advanced AI technology creates resumes that not only look professional 
              but are specifically optimized for the job you're applying to.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <div key={index} className="text-center group hover:transform hover:scale-105 transition-all duration-300">
                <div className="mb-6 flex justify-center">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
                How Zumud transforms your job search
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Our AI analyzes job descriptions and optimizes your resume to match exactly 
                what employers are looking for, giving you a competitive edge.
              </p>
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-start space-x-4">
                    <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-semibold text-sm">
                      {index + 1}
                    </div>
                    <p className="text-gray-700 pt-1">{step}</p>
                  </div>
                ))}
              </div>
              <Button 
                className="mt-8 bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg font-semibold rounded-lg"
                onClick={() => setShowAuthModal(true)}
              >
                Get Started Now
              </Button>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <Upload className="h-8 w-8 text-blue-600" />
                    <div>
                      <div className="h-3 bg-blue-200 rounded w-32 mb-2"></div>
                      <div className="h-2 bg-gray-200 rounded w-24"></div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="h-3 bg-gray-200 rounded w-full"></div>
                    <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                    <div className="h-3 bg-blue-200 rounded w-4/5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>
        </section>

      {/* Simple Creation Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              Create your perfect resume in a really simple way
            </h2>
            <p className="text-xl text-gray-600">
              No design skills needed. Our AI handles everything from formatting to content optimization.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto text-center">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Upload your existing resume</h3>
              <p className="text-gray-600">Simply upload your current resume or start from scratch with our guided form.</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Paste the job description</h3>
              <p className="text-gray-600">Add the job posting you're applying to and our AI will analyze the requirements.</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Get your optimized resume</h3>
              <p className="text-gray-600">Download your tailored, ATS-optimized resume in minutes, not hours.</p>
            </div>
          </div>
          <div className="text-center mt-12">
            <Button
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg font-semibold rounded-lg"
              onClick={() => setShowAuthModal(true)}
            >
              See Zumud in action
            </Button>
          </div>
        </div>
      </section>



      {/* Proven Results Section */}
      <section className="py-20 bg-blue-600">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
              Proven Results
            </h2>
            <p className="text-xl text-blue-100">
              Our users see real results with Zumud-optimized resumes.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto text-center">
            <div>
              <div className="text-4xl lg:text-5xl font-bold text-white mb-2">92%</div>
              <p className="text-blue-100">Higher interview rate with ATS-optimized resumes</p>
            </div>
            <div>
              <div className="text-4xl lg:text-5xl font-bold text-white mb-2">3x</div>
              <p className="text-blue-100">More job interviews compared to standard resumes</p>
            </div>
            <div>
              <div className="text-4xl lg:text-5xl font-bold text-white mb-2">85%</div>
              <p className="text-blue-100">Job seekers land offers within 30 days</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              Choose the Plan That Fits Your Needs
            </h2>
            <p className="text-xl text-gray-600">
              Start with our free plan or unlock premium features for the best results.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Plan */}
            <div className="border-2 border-gray-200 rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Free</h3>
              <div className="text-4xl font-bold text-gray-900 mb-6">$0</div>
              <ul className="space-y-3 mb-8 text-left">
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>1 resume download</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Basic ATS optimization</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Standard templates</span>
                </li>
              </ul>
              <Button
                variant="outline" 
                className="w-full py-3 text-lg border-2 border-gray-300"
                onClick={() => setShowAuthModal(true)}
              >
                Get Started
              </Button>
            </div>

            {/* Pro Plan */}
            <div className="border-2 border-blue-600 rounded-2xl p-8 text-center relative bg-blue-50">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                Popular
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Pro</h3>
              <div className="text-4xl font-bold text-gray-900 mb-6">$19.99</div>
              <ul className="space-y-3 mb-8 text-left">
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Unlimited resume downloads</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Advanced ATS optimization</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Premium templates</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Cover letter generation</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>LinkedIn optimization</span>
                </li>
              </ul>
              <Button 
                className="w-full py-3 text-lg bg-blue-600 hover:bg-blue-700"
                onClick={() => setShowAuthModal(true)}
              >
                Start Pro Trial
              </Button>
            </div>

            {/* Premium Plan */}
            <div className="border-2 border-gray-200 rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Premium</h3>
              <div className="text-4xl font-bold text-gray-900 mb-6">$49.99</div>
              <ul className="space-y-3 mb-8 text-left">
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Everything in Pro</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>1-on-1 resume review</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Interview preparation</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Job search strategy</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-5 w-5 text-green-500 mr-3" />
                  <span>Priority support</span>
                </li>
              </ul>
              <Button 
                variant="outline" 
                className="w-full py-3 text-lg border-2 border-gray-300"
                onClick={() => setShowAuthModal(true)}
              >
                Choose Premium
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about Zumud and our AI-powered resume builder.
            </p>
          </div>
          <div className="max-w-3xl mx-auto space-y-4">
            {faqItems.map((item, index) => (
              <div key={index} className="bg-white rounded-lg shadow-sm">
                <button
                  className="w-full text-left p-6 flex justify-between items-center hover:bg-gray-50"
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                >
                  <span className="font-semibold text-gray-900">{item.question}</span>
                  <span className="text-2xl text-gray-400">
                    {openFaq === index ? '−' : '+'}
                  </span>
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-6">
                    <p className="text-gray-600">{item.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
                </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
              Ready to land your dream job?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of successful job seekers who have transformed their careers with Zumud.
            </p>
                <Button 
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-6 text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all"
              onClick={() => setShowAuthModal(true)}
            >
              Get Started Free
                </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-2xl font-bold mb-4">Zumud</div>
              <p className="text-gray-400 mb-4">
                AI-powered resume builder that helps you land more interviews.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white">Twitter</a>
                <a href="#" className="text-gray-400 hover:text-white">LinkedIn</a>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Templates</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Career Tips</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Zumud. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Auth Modal Placeholder */}
      <Dialog open={showAuthModal} onOpenChange={setShowAuthModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Sign Up / Login</DialogTitle>
          </DialogHeader>
          <div className="p-6 text-center">
            <p className="text-gray-600 mb-4">Authentication modal would go here</p>
            <Button onClick={() => setShowAuthModal(false)}>Close</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
} 