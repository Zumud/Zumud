import type { MetadataRoute } from "next";

// AI answer engines (ChatGPT, Perplexity, Claude, Gemini) only recommend
// what their crawlers can read — keep them explicitly allowed alongside
// classic search bots.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: [
          "Googlebot",
          "Bingbot",
          "GPTBot",
          "OAI-SearchBot",
          "ChatGPT-User",
          "ClaudeBot",
          "PerplexityBot",
          "Google-Extended",
        ],
        allow: "/",
      },
      { userAgent: "*", allow: "/" },
    ],
    sitemap: "https://zumud.com/sitemap.xml",
  };
}
