import { TESTIMONIALS } from "@/data/testimonials-data";
import { StarIcon } from "lucide-react";

export default function TestimonialsSection() {
  return (
    <section id="testimonials" className="py-20 bg-gradient-to-b from-blue-50 to-white dark:from-blue-950 dark:to-gray-950">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            What Our Users Say
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Join thousands of job seekers who have transformed their careers with
            Zumud.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {TESTIMONIALS.map((testimonial, index) => (
            <div
              key={index}
              className="group relative p-6 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm hover:shadow-lg transition-all duration-300 hover:border-blue-200 dark:hover:border-blue-800"
            >
              <div className="flex items-center mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <StarIcon
                    key={i}
                    className="h-5 w-5 text-yellow-400 fill-current"
                  />
                ))}
              </div>
              <blockquote className="text-muted-foreground mb-4 leading-relaxed">
                &quot;{testimonial.quote}&quot;
              </blockquote>
              <div className="flex items-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-violet-600 text-white font-medium text-sm">
                  {testimonial.author.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="ml-3">
                  <div className="font-medium text-sm">{testimonial.author}</div>
                  <div className="text-xs text-muted-foreground">
                    {testimonial.role} at {testimonial.company}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex items-center rounded-full bg-green-50 dark:bg-green-900/20 px-6 py-2 text-sm text-green-600 dark:text-green-300 mb-4">
            <StarIcon className="h-4 w-4 mr-2 fill-current" />
            Rated 4.9/5 from 10,000+ job seekers and interviews at top companies worldwide
          </div>
          <div className="flex justify-center items-center space-x-8 mt-8 opacity-60">
            <div className="text-2xl font-bold text-gray-400">Google</div>
            <div className="text-2xl font-bold text-gray-400">Microsoft</div>
            <div className="text-2xl font-bold text-gray-400">Amazon</div>
            <div className="text-2xl font-bold text-gray-400">Meta</div>
            <div className="text-2xl font-bold text-gray-400">Apple</div>
          </div>
        </div>
      </div>
    </section>
  );
} 