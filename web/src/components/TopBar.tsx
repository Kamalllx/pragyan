"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function Mark({ size = 26, spin = false }: { size?: number; spin?: boolean }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden className={spin ? "animate-[spin_9s_linear_infinite]" : ""}>
      <circle cx="16" cy="16" r="13.5" fill="none" stroke="currentColor" strokeOpacity="0.45" strokeWidth="1.4" />
      <circle cx="16" cy="16" r="8.5" fill="none" stroke="var(--color-saffron)" strokeOpacity="0.6" strokeWidth="1.2" strokeDasharray="38 16" />
      <circle cx="16" cy="16" r="3.6" fill="var(--color-saffron)" />
      <circle cx="29.5" cy="16" r="1.7" fill="currentColor" />
    </svg>
  );
}

type Sys = { db: string; ollama: boolean; roles: Record<string, string>; engines: Record<string, boolean>; running: string[] };

export function TopBar() {
  const path = usePathname();
  const [sys, setSys] = useState<Sys | null>(null);
  const [down, setDown] = useState(false);

  useEffect(() => {
    let alive = true;
    const tick = () =>
      api
        .system()
        .then((s) => alive && (setSys(s), setDown(false)))
        .catch(() => alive && setDown(true));
    tick();
    const t = setInterval(tick, 8000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const nav = [
    { href: "/", label: "Studio" },
    { href: "/library", label: "Library" },
    { href: "/steering", label: "Steering" },
  ];
  const active = (h: string) => (h === "/" ? path === "/" : path.startsWith(h));

  return (
    <header className="sticky top-0 z-40 border-b border-regolith/60 bg-basalt/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1440px] items-center gap-6 px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 text-moon">
          <Mark />
          <span className="font-display text-[19px] font-semibold tracking-[-0.02em]">Pragyan</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {nav.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={`rounded-full px-3 py-1.5 transition-colors ${active(n.href) ? "bg-basalt-3 text-moon" : "text-dust hover:text-moon"}`}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-3 text-xs text-dust">
          {down ? (
            <span className="flex items-center gap-2 text-err">
              <Dot ok={false} /> Backend offline — run <code className="font-mono text-ash">start.ps1</code>
            </span>
          ) : sys ? (
            <>
              <span className="hidden items-center gap-1.5 md:flex" title={`Ollama · ${sys.roles.reason}`}>
                <Dot ok={sys.ollama} /> {sys.roles.reason}
              </span>
              <span className="hidden items-center gap-1.5 lg:flex" title="Database">
                <Dot ok={!sys.db.startsWith("local")} /> {sys.db.startsWith("mongodb") ? "MongoDB" : "Local store"}
              </span>
              <span className="hidden items-center gap-1.5 lg:flex" title="Narration engine">
                <Dot ok={sys.engines.kokoro} /> Kokoro voice
              </span>
              {sys.running.length > 0 && (
                <span className="flex items-center gap-1.5 text-earth">
                  <span className="relative flex size-2">
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-earth opacity-60" />
                    <span className="relative inline-flex size-2 rounded-full bg-earth" />
                  </span>
                  {sys.running.length} rendering
                </span>
              )}
            </>
          ) : (
            <span className="shimmer h-3 w-40 rounded" />
          )}
        </div>
      </div>
    </header>
  );
}

function Dot({ ok }: { ok: boolean }) {
  return <span className={`inline-block size-1.5 rounded-full ${ok ? "bg-ok" : "bg-err"}`} />;
}
