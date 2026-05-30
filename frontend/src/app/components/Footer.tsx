import Link from "next/link";
import CurrentYear from "./CurrentYear";

export default function Footer() {
  return (
    <footer
      className="glass-footer"
      style={{
        marginTop: "4rem",
        padding: "5rem 0 2rem",
        borderTop: "1px solid rgba(255,255,255,0.08)",
        background: "linear-gradient(to bottom, rgba(255,255,255,0.02), rgba(255,255,255,0.01))",
      }}
    >
      <div
        className="container"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "3rem",
        }}
      >
        {/* Brand */}
        <div style={{ gridColumn: "1 / -1", '@media (min-width: 768px)': { gridColumn: "span 2" } } as any}>
          <h2
            style={{
              fontSize: "1.8rem",
              marginBottom: "1rem",
              background: "linear-gradient(to right,#22c55e,#06b6d4,#3b82f6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: 800,
            }}
          >
            EnvForge ⚡
          </h2>

          <p
            style={{
              color: "var(--text-secondary)",
              lineHeight: "1.8",
              maxWidth: "350px",
            }}
          >
            Build, diagnose and optimize AI/ML environments with confidence.
            Designed for developers who want faster setup, fewer errors and
            smarter workflows.
          </p>

          <div
            style={{
              marginTop: "1.5rem",
              display: "flex",
              gap: "0.8rem",
            }}
          >
            <span
              style={{
                padding: "6px 12px",
                borderRadius: "999px",
                background: "rgba(34,197,94,0.15)",
                border: "1px solid rgba(34,197,94,0.25)",
                fontSize: "0.85rem",
                color: "#22c55e",
              }}
            >
              Open Source
            </span>
            <span
              style={{
                padding: "6px 12px",
                borderRadius: "999px",
                background: "rgba(59,130,246,0.15)",
                border: "1px solid rgba(59,130,246,0.25)",
                fontSize: "0.85rem",
                color: "#3b82f6",
              }}
            >
              AI Powered
            </span>
          </div>
        </div>

        {/* Product */}
        <div>
          <h4 style={{ marginBottom: "1.5rem", fontWeight: 600, color: "var(--text-primary)" }}>
            Product
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
            <Link href="/profiles" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Profiles</Link>
            <Link href="/diagnose" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Diagnose</Link>
            <Link href="/troubleshoot" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Troubleshoot</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Script Generator</Link>
          </div>
        </div>

        {/* Resources */}
        <div>
          <h4 style={{ marginBottom: "1.5rem", fontWeight: 600, color: "var(--text-primary)" }}>
            Resources
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Documentation</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Guides</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>API Reference</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>FAQ</Link>
          </div>
        </div>

        {/* Community */}
        <div>
          <h4 style={{ marginBottom: "1.5rem", fontWeight: 600, color: "var(--text-primary)" }}>
            Community
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Contribute</Link>
            <Link href="https://github.com" target="_blank" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>GitHub</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Report Issues</Link>
            <Link href="/coming-soon" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>Discussions</Link>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div
        style={{
          marginTop: "4rem",
          paddingTop: "2rem",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          textAlign: "center",
          color: "var(--text-muted)",
          fontSize: "0.9rem"
        }}
      >
        <p>
          © <CurrentYear /> EnvForge. Built for Developers ❤️ • Powered by AI ⚡
        </p>
      </div>
    </footer>
  );
}
