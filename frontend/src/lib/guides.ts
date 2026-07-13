import fs from "node:fs";
import path from "node:path";
import { getFrontmatter } from "next-mdx-remote-client/utils";

interface GuideFaqItem {
  q: string;
  a: string;
}

export interface GuideMeta {
  slug: string;
  title: string;
  description: string;
  datePublished: string;
  dateModified: string;
  faq?: GuideFaqItem[];
}

interface GuideFrontmatter extends Record<string, unknown> {
  title?: string;
  description?: string;
  datePublished?: string;
  dateModified?: string;
  faq?: GuideFaqItem[];
}

const GUIDES_DIR = path.join(process.cwd(), "content", "guides");
const REQUIRED_FIELDS = [
  "title",
  "description",
  "datePublished",
  "dateModified",
] as const;

// URL-safe slug contract for guide filenames; also a sanitizer barrier so
// filesystem-derived slugs are provably inert in hrefs (CodeQL js/stored-xss).
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function parseGuide(file: string): { meta: GuideMeta; source: string } {
  const slug = file.replace(/\.mdx$/, "");
  if (!SLUG_RE.test(slug)) {
    throw new Error(
      `Guide filename "${file}" must be a lowercase-hyphen slug (.mdx)`,
    );
  }
  const raw = fs.readFileSync(path.join(GUIDES_DIR, file), "utf8");
  const { frontmatter, strippedSource } = getFrontmatter<GuideFrontmatter>(raw);
  for (const field of REQUIRED_FIELDS) {
    // Fail the build rather than ship a guide violating docs/seo-guidelines.md.
    if (!frontmatter[field]) {
      throw new Error(`Guide ${file} is missing frontmatter field "${field}"`);
    }
  }
  return {
    meta: {
      slug,
      title: frontmatter.title!,
      description: frontmatter.description!,
      datePublished: frontmatter.datePublished!,
      dateModified: frontmatter.dateModified!,
      faq: frontmatter.faq,
    },
    source: strippedSource,
  };
}

export function getGuides(): GuideMeta[] {
  return fs
    .readdirSync(GUIDES_DIR)
    .filter((file) => file.endsWith(".mdx"))
    .map((file) => parseGuide(file).meta)
    .sort((a, b) => (a.datePublished < b.datePublished ? 1 : -1));
}

export function getGuide(
  slug: string,
): { meta: GuideMeta; source: string } | null {
  const file = `${slug}.mdx`;
  if (!fs.existsSync(path.join(GUIDES_DIR, file))) return null;
  return parseGuide(file);
}
