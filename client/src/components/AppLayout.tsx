import { NavLink } from "react-router-dom";
import type { PropsWithChildren } from "react";

const navItems = [
  { to: "/notes", label: "筆記" },
  { to: "/search", label: "AI 搜尋" },
  { to: "/chat", label: "AI 對話" },
];

export function AppLayout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <div className="grain" />
      <header className="hero">
        <div className="hero__copy">
          <p className="eyebrow">AI 工程筆記 MVP</p>
          <h1>AI 工程筆記</h1>
          <p className="hero__body">
            Markdown 筆記管理、語意搜尋與 AI 問答。
          </p>
        </div>
        <div className="hero__meta">
          <div className="hero__card hero__card--tilt">
            <span>規格覆蓋</span>
            <strong>筆記 CRUD、預覽、搜尋、對話與引用來源</strong>
          </div>
          <div className="hero__card">
            <span>自動標籤</span>
            <strong>未手動輸入時，自動產生 3 到 6 個小寫標籤</strong>
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
