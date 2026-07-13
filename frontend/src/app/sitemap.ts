import type { MetadataRoute } from "next";
import { getGuides } from "@/lib/guides";

const BASE_URL = "https://zumud.com";

// Public, indexable routes only. App pages (/dashboard, /profile, /history,
// /resume/*) are noindex and must stay out. Guides are included
// automatically; other new public pages get added here in the same PR that
// creates them.
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE_URL}/`,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/guides`,
      changeFrequency: "weekly",
      priority: 0.8,
    },
    ...getGuides().map((guide) => ({
      url: `${BASE_URL}/guides/${guide.slug}`,
      lastModified: new Date(guide.dateModified),
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
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
