"use client";

import { createContext, useContext, useEffect, useState, type ReactNode, useCallback } from "react";
import type { Lang } from "@/lib/i18n";

interface LanguageContextType {
  uiLang: Lang;
  responseLang: Lang;
  setUiLang: (lang: Lang) => void;
  setResponseLang: (lang: Lang) => void;
  toggleUiLang: () => void;
}

const LanguageContext = createContext<LanguageContextType>({
  uiLang: "ar",
  responseLang: "ar",
  setUiLang: () => {},
  setResponseLang: () => {},
  toggleUiLang: () => {},
});

const UI_LANG_KEY = "labor_ui_lang";
const RESPONSE_LANG_KEY = "labor_response_lang";

function getStored(key: string, fallback: Lang): Lang {
  if (typeof window === "undefined") return fallback;
  const v = localStorage.getItem(key);
  return v === "ar" || v === "en" ? v : fallback;
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [uiLang, setUiLangState] = useState<Lang>(() => getStored(UI_LANG_KEY, "ar"));
  const [responseLang, setResponseLangState] = useState<Lang>(() => getStored(RESPONSE_LANG_KEY, "ar"));

  useEffect(() => {
    document.documentElement.lang = uiLang;
    document.documentElement.dir = uiLang === "ar" ? "rtl" : "ltr";
  }, [uiLang]);

  const setUiLang = useCallback((lang: Lang) => {
    setUiLangState(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem(UI_LANG_KEY, lang);
      document.documentElement.lang = lang;
      document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    }
  }, []);

  const setResponseLang = useCallback((lang: Lang) => {
    setResponseLangState(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem(RESPONSE_LANG_KEY, lang);
    }
  }, []);

  const toggleUiLang = useCallback(() => {
    setUiLang(uiLang === "ar" ? "en" : "ar");
  }, [uiLang, setUiLang]);

  return (
    <LanguageContext.Provider value={{ uiLang, responseLang, setUiLang, setResponseLang, toggleUiLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  return useContext(LanguageContext);
}
