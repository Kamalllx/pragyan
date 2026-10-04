"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, media, type Job } from "@/lib/api";

const fmt = (s?: number) => (s ? `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}` : "");

export function FilmGrid({ limit, title = "Your films" }: { limit?: number; title?: string }) {
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    let alive = true;
    const load = () =>
      api
        .jobs()
        .then((j) => alive && (setJobs(j), setErr(false)))
        .catch(() => alive && setErr(true));
    load();
    const t = setInterval(load, 6000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const list = limit ? jobs?.slice(0, limit) : jobs;

  return (
    <section aria-labelledby="films-h">
      <div className="mb-5 flex items-baseline justify-between">
        <h2 id="films-h" className="font-display text-2xl font-semibold tracking-[-0.02em]">
          {title}
        </h2>
        {limit && jobs && jobs.length > limit && (
          <Link href="/library" className="text-sm text-dust hover:text-moon">
            See all {jobs.length}
          </Link>
        )}
      </div>
      {err && <p className="text-sm text-dust">The library will appear once the backend is running.</p>}
      {list && list.length === 0 && (
        <p className="max-w-md text-sm text-dust">Nothing here yet. Ask your first question above — Pragyan will storyboard, narrate and render it on this machine.</p>
      )}
      {!list && !err && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="shimmer aspect-video rounded-2xl bg-basalt-2" />
          ))}
        </div>
      )}
      {list && list.length > 0 && (
        <ul className="grid gap-x-5 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
          {list.map((j) => (
            <li key={j.id}>
              <Link href={`/jobs/${j.id}`} className="group block">
                <div className="relative aspect-video overflow-hidden rounded-2xl border border-regolith/70 bg-basalt-2">
                  {j.outputs?.poster ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={media(j.outputs.poster)}
                      alt=""
                      className="size-full object-cover transition-transform duration-700 ease-[var(--ease-out-expo)] group-hover:scale-[1.03]"
                    />
                  ) : (
                    <div className="grid size-full place-items-center">
                      {j.status === "running" || j.status === "queued" ? (
                        <div className="text-center">
                          <div className="mx-auto mb-2 size-2 animate-pulse rounded-full bg-earth" />
                          <span className="text-xs text-dust">{j.stage === "queued" ? "Queued" : `Working · ${j.stage}`}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-dust">{j.status === "failed" ? "Didn't finish" : j.status}</span>
                      )}
                    </div>
                  )}
                  {j.outputs?.duration ? (
                    <span className="absolute right-2.5 bottom-2.5 rounded-md bg-black/60 px-1.5 py-0.5 font-mono text-[11px] text-moon backdrop-blur">
                      {fmt(j.outputs.duration)}
                    </span>
                  ) : null}
                </div>
                <div className="mt-3 flex items-start gap-3">
                  <h3 className="line-clamp-2 flex-1 text-[15px] leading-snug text-moon group-hover:text-white">{j.title}</h3>
                  {j.data?.intent?.intent && (
                    <span className="mt-0.5 shrink-0 rounded-full border border-regolith px-2 py-0.5 text-[11px] text-dust">
                      {String(j.data.intent.intent).replace(/_/g, " ")}
                    </span>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
