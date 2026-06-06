import React from 'react';
import Link from 'next/link';

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-[var(--bg-core)]">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[var(--border-subtle)] h-screen sticky top-0 overflow-y-auto p-6 hidden md:block">
        <h2 className="text-lg font-black tracking-widest uppercase mb-6 text-[var(--brand-secondary)]">Documentation</h2>
        <nav className="flex flex-col gap-3 text-[var(--text-secondary)]">
          <Link href="/docs/getting-started" className="hover:text-[var(--text-primary)] transition-colors">Getting Started</Link>
          <Link href="/docs/architecture" className="hover:text-[var(--text-primary)] transition-colors">Architecture</Link>
          <Link href="/docs/api" className="hover:text-[var(--text-primary)] transition-colors">API Schema</Link>
        </nav>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 p-8 md:p-16 max-w-4xl">
        {children}
      </main>
    </div>
  );
}
