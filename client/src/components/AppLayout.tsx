import { NavLink } from "react-router-dom";
import type { PropsWithChildren } from "react";

const navItems = [
  { to: "/notes", label: "筆記" },
  { to: "/search", label: "AI 搜尋" },
  { to: "/chat", label: "AI 對話" },
];

type AppLayoutProps = PropsWithChildren<{
  noteCount: number;
}>;

export function AppLayout({ children, noteCount }: AppLayoutProps) {
  return (
    <div className="app-shell">
      <div className="grain" />
      <header className="hero">
        <div className="hero__copy">
          <h1>AI 工程筆記</h1>
          <p className="hero__body">
            Markdown 筆記管理、語意搜尋與 AI 問答。
          </p>
        </div>
        <div className="hero__meta">
          <div className="hero__card hero__card--tilt">
            <span>筆記數量</span>
            <strong>{noteCount} 篇筆記</strong>
          </div>
        </div>
      </header>

      <nav className="top-nav" aria-label="Primary">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <main className="page-wrap">{children}</main>
    </div>
  );
}
