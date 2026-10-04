import type { Metadata } from "next";
import { Bricolage_Grotesque, IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";
import { TopBar } from "@/components/TopBar";

const bricolage = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-bricolage", display: "swap" });
const plex = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-plex", display: "swap" });
const plexMono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-plex-mono", display: "swap" });

export const metadata: Metadata = {
  title: "Pragyan AI",
  description: "Turn a question, concept, document or image into an explained, animated video — fully on your machine.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${bricolage.variable} ${plex.variable} ${plexMono.variable}`}>
      <body className="min-h-dvh">
        <div className="relative z-10 flex min-h-dvh flex-col">
          <TopBar />
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
