import type { MetadataRoute } from "next";

const BASE_URL = "https://zumud.com";

// Public, indexable routes only. App pages (/dashboard, /profile, /history,
// /resume/*) are noindex and must stay out. New public pages (e.g. guides)
// get added here in the same PR that creates them.
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE_URL}/`,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/privacy`,
      changeFrequency: "yearly",
      priority: 0.4,
    },
    {
      url: `${BASE_URL}/terms`,
      changeFrequency: "yearly",
      priority: 0.4,
    },
    {
      url: `${BASE_URL}/cookies`,
      changeFrequency: "yearly",
      priority: 0.4,
    },
  ];
}
