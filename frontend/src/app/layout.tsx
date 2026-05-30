import type { Metadata } from "next";
import Script from "next/script";
import { Inter, Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "./providers";
import Link from "next/link";
import Navbar from "./components/Navbar";
import CurrentYear from "./components/CurrentYear";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "EnvForge | ML Environment Provisioning",
  description:
    "Generate intelligent, safe, and deterministic ML/AI environment setup scripts.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            try {
              const storedTheme = localStorage.getItem("theme");
              const theme =
                storedTheme === "dark" ||
                storedTheme === "light" ||
                storedTheme === "system"
                  ? storedTheme
                  : "dark";

              if (theme === "system") {
                const prefersDark =
                  window.matchMedia("(prefers-color-scheme: dark)").matches;

                document.documentElement.setAttribute(
                  "data-theme",
                  prefersDark ? "dark" : "light"
                );
              } else {
                document.documentElement.setAttribute(
                  "data-theme",
                  theme
                );
              }
            } catch {
              document.documentElement.setAttribute("data-theme", "dark");
            }
          `}
        </Script>
      </head>

      <body
        className={`${inter.variable} ${outfit.variable} ${jetbrainsMono.variable}`}
      >
        <ThemeProvider>
          {/* Navigation Bar */}
          <nav
            className="glass-nav"
            style={{
              position: "sticky",
              top: 0,
              zIndex: 50,
              padding: "1rem 0",
            }}
          >
            <div
              className="container"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "2rem",
                }}
              >
                <Link
                  href="/"
                  style={{
                    fontSize: "1.5rem",
                    fontWeight: 700,
                    fontFamily: "var(--font-display)",
                    letterSpacing: "-0.02em",
                  }}
                >
                  Env<span className="text-gradient">Forge</span>
                </Link>

                <div
                  style={{
                    display: "flex",
                    gap: "1.5rem",
                    fontSize: "0.9rem",
                    color: "var(--text-secondary)",
                  }}
                >
                  <Link href="/profiles">Profiles</Link>
                  <Link href="/diagnose">Diagnose</Link>
                  <Link href="/troubleshoot">AI Troubleshoot</Link>
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: "0.5rem",
                  alignItems: "center",
                }}
              >
                <ThemeToggle />
                <a
                  href="https://github.com/rishabh0510rishabh/EnvForage"
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{
                    padding: "0.5rem 1rem",
                    fontSize: "0.9rem",
                  }}
                >
                  GitHub
                </a>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main style={{ minHeight: "calc(100vh - 140px)" }}>
            {children}
          </main>

          {/* Footer */}
          <footer
            style={{
              borderTop: "1px solid var(--border-subtle)",
              padding: "2rem 0",
              marginTop: "4rem",
              color: "var(--text-muted)",
            }}
          >
            <div
              className="container"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: "0.85rem",
              }}
            >
              <p>
                © {new Date().getFullYear()} EnvForge. Open Source Tooling.
              </p>

              <div style={{ display: "flex", gap: "1rem" }}>
                <Link href="/docs">Documentation</Link>
                <Link href="/privacy">Privacy</Link>
              </div>
      <body className={`${inter.variable} ${outfit.variable} ${jetbrainsMono.variable}`} style={{ backgroundColor: "var(--bg-core)" }}>
        <ThemeProvider>
          {/* Navigation Header */}
          <Navbar />

          {/* Main Content */}
          <main style={{ minHeight: "calc(100vh - 140px)" }}>
            {children}
          </main>

          {/* Footer */}
          <footer
            className="glass-footer"
            style={{
              padding: "2.5rem 0",
              marginTop: "5rem",
              color: "var(--text-muted)",
            }}
          >
            <div
              className="container"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: "0.85rem",
              }}
            >
              <p>© <CurrentYear /> EnvForge. Open Source Tooling.</p>

              <div style={{ display: "flex", gap: "1.5rem" }}>
                <Link
                  href="/docs"
                  style={{ transition: "color var(--transition-fast)" }}
                >
                  Documentation
                </Link>

                <Link
                  href="/privacy"
                  style={{ transition: "color var(--transition-fast)" }}
                >
                  Privacy
                </Link>
              </div>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}