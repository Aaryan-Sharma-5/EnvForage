"use client";

import { usePathname } from "next/navigation";

/**
 * CanonicalURL — dynamically injects a <link rel="canonical"> tag for the
 * current route, preventing duplicate-content indexing across:
 *   • trailing-slash variants  (/generate vs /generate/)
 *   • query-string variants    (/generate?tab=cuda)
 *   • www vs. non-www          (handled at DNS/CDN level; belt-and-suspenders)
 *
 * Mounted once in the root layout's <head> so every page gets a correct
 * canonical automatically — no per-page boilerplate required.
 */
export default function CanonicalURL() {
  const pathname = usePathname();

  // Normalise base URL (mirrors logic in layout.tsx and sitemap.ts)
  let rawBase = process.env.NEXT_PUBLIC_BASE_URL?.trim() ?? "";
  if (!rawBase) rawBase = "http://localhost:3000";
  if (rawBase.endsWith("/")) rawBase = rawBase.slice(0, -1);
  if (!rawBase.startsWith("http")) rawBase = `https://${rawBase}`;

  // Strip trailing slash from path (canonical = no trailing slash),
  // but keep "/" itself so the homepage canonical resolves to the base URL.
  const normalisedPath =
    pathname !== "/" && pathname.endsWith("/")
      ? pathname.slice(0, -1)
      : pathname;

  const canonicalUrl = `${rawBase}${normalisedPath === "/" ? "" : normalisedPath}`;

  return <link rel="canonical" href={canonicalUrl} />;
}
