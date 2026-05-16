import type { Metadata, Viewport } from "next";
import { Fira_Code, Fira_Sans } from "next/font/google";
import { ClientShell } from "./ClientShell";
import "./globals.css";

const firaSans = Fira_Sans({ variable: "--font-fira-sans", subsets: ["latin"], weight: ["300", "400", "500", "600", "700"] });
const firaCode = Fira_Code({ variable: "--font-fira-code", subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "Labor Cost Estimator",
  description: "Smart AI-powered labor cost estimation for automotive workshops",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="ar"
      dir="rtl"
      suppressHydrationWarning
      className={`${firaSans.variable} ${firaCode.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">
        <ClientShell>{children}</ClientShell>
      </body>
    </html>
  );
}
