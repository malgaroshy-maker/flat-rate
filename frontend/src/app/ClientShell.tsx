"use client";

import { LanguageProvider, useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";
import Link from "next/link";
import { usePathname } from "next/navigation";

/* Lucide-style SVG icons */
const IconSearch = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>);
const IconBook = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>);
const IconBot = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>);
const IconInbox = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>);
const IconSettings = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>);

function Header() {
  const { uiLang, toggleUiLang } = useLanguage();
  const pathname = usePathname();

  const tabs = [
    { href: "/", label: { ar: "بحث", en: "Search" }, icon: IconSearch },
    { href: "/dictionary", label: { ar: "القاموس", en: "Dictionary" }, icon: IconBook },
    { href: "/assistant", label: { ar: "المساعد", en: "Assistant" }, icon: IconBot },
    { href: "/pending", label: { ar: "المراجعة", en: "Review" }, icon: IconInbox },
    { href: "/settings", label: { ar: "الإعدادات", en: "Settings" }, icon: IconSettings },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-sky-600 text-white px-4 py-2 rounded z-50 text-sm">{uiLang === "ar" ? "تخطي إلى المحتوى" : "Skip to content"}</a>
      <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-between px-6">
        <div className="flex items-center gap-6">
          <h1 className="text-base font-bold text-white tracking-tight font-mono">{t("appTitle", uiLang)}</h1>
          <nav className="flex gap-0.5" aria-label={uiLang === "ar" ? "التنقل الرئيسي" : "Main navigation"}>
            {tabs.map((tab) => {
              const active = pathname === tab.href;
              const Icon = tab.icon;
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  aria-current={active ? "page" : undefined}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${
                    active
                      ? "bg-sky-600 text-white"
                      : "text-slate-400 hover:text-white hover:bg-slate-800"
                  }`}
                >
                  <Icon />
                  <span>{tab.label[uiLang]}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        <button
          onClick={toggleUiLang}
          aria-label={uiLang === "ar" ? "Switch to English" : "التبديل إلى العربية"}
          className="rounded-md border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white hover:border-slate-500 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
        >
          {uiLang === "ar" ? "EN" : "العربية"}
        </button>
      </div>
    </header>
  );
}

export function ClientShell({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <Header />
      <main id="main-content" className="flex-1" role="main">{children}</main>
    </LanguageProvider>
  );
}
