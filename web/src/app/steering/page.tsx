"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";

type Pack = {
  id: string;
  name: string;
  kind: "core" | "pack" | "overlay";
  source?: string;
  description?: string;
  priority?: number;
  match?: { intents?: string[]; domains?: string[]; audiences?: string[]; keywords?: string[] };
  settings?: Record<string, any>;
  arc?: string[];
  visuals?: { prefer?: string[]; avoid?: string[] };
  narration?: { tone?: string; rules?: string[] };
  rules?: { do?: string[]; dont?: string[] };
  learned_from?: string;
  rating?: number;
};

const KIND_LABEL = { core: "Always on", pack: "Video styles", overlay: "Overlays" } as const;

export default function SteeringPage() {
  const [packs, setPacks] = useState<Pack[] | null>(null);
  const [sel, setSel] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [preview, setPreview] = useState<any>(null);
  const [previewing, setPreviewing] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [err, setErr] = useState("");

  const load = () => api.steering().then((p) => setPacks(p)).catch(() => setPacks([]));
  useEffect(() => {
    load();
  }, []);

  const groups = useMemo(() => {
    const g: Record<string, Pack[]> = { core: [], pack: [], overlay: [] };
    (packs ?? []).forEach((p) => (g[p.kind ?? "pack"] ??= []).push(p));
    return g;
  }, [packs]);
  const active = packs?.find((p) => p.id === sel) ?? packs?.find((p) => p.kind === "pack");
  const applied = new Set<string>((preview?.steering?.packs ?? []).map((p: any) => p.id));

  const runPreview = async () => {
    if (!q.trim()) return;
    setPreviewing(true);
    try {
      setPreview(await api.previewSteering(q));
    } finally {
      setPreviewing(false);
    }
  };

  const startEdit = (p: Pack) => {
    setEditing(p.id);
    const { ...rest } = p as any;
    delete rest.path;
    delete rest._id;
    delete rest.updated_at;
    setDraft(JSON.stringify(rest, null, 2));
    setErr("");
  };

  const save = async () => {
    try {
      const obj = JSON.parse(draft);
      await api.saveSteering(obj);
      setEditing(null);
      load();
    } catch (e: any) {
      setErr(e instanceof SyntaxError ? `That isn't valid JSON: ${e.message}` : `Couldn't save: ${e.message}`);
    }
  };

  return (
    <div className="mx-auto max-w-[1280px] px-4 py-14 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-[-0.03em]">Steering</h1>
      <p className="mt-3 max-w-[68ch] text-ash">
        Steering packs are reusable direction, not prompts: the arc a kind of video should follow, which visuals suit it, the narration voice, the look. Pragyan
        picks the best match for every request and stacks overlays on top. Rate a finished video 4 or 5 and it learns a new pack from it.
      </p>

      {/* dry run */}
      <div className="mt-8 rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
        <label htmlFor="pv" className="text-sm font-medium">
          Test a request
        </label>
        <p className="mt-1 text-xs text-dust">See what Pragyan would understand and which packs would steer it — nothing is rendered.</p>
        <div className="mt-3 flex flex-col gap-2 sm:flex-row">
          <input
            id="pv"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runPreview()}
            placeholder="e.g. Explain photosynthesis to a 10 year old"
            className="flex-1 rounded-xl border border-regolith bg-basalt px-4 py-2.5 text-sm text-moon focus:border-regolith-2 focus:outline-none"
          />
          <button onClick={runPreview} disabled={previewing || !q.trim()} className="rounded-full bg-saffron px-5 py-2.5 text-sm font-semibold text-basalt disabled:opacity-50">
            {previewing ? "Analysing…" : "Analyse"}
          </button>
        </div>
        {preview && (
          <div className="mt-4 grid gap-4 text-sm md:grid-cols-[1fr_1.2fr]">
            <div>
              <div className="text-xs text-dust">Understood as</div>
              <div className="mt-1 text-moon capitalize">
                {preview.intent.intent.replace(/_/g, " ")} · {preview.intent.domain.replace(/_/g, " ")} · {preview.intent.audience_level}
              </div>
              <p className="mt-2 text-ash">{preview.intent.reasoning}</p>
            </div>
            <div>
              <div className="text-xs text-dust">Would apply</div>
              <ul className="mt-1 space-y-1">
                {preview.steering.packs.map((p: any) => (
                  <li key={p.id} className="flex items-center gap-2">
                    <span className="text-moon">{p.name}</span>
                    <span className="text-xs text-dust">{p.kind === "core" ? "always on" : `match ${p.score}`}</span>
                  </li>
                ))}
              </ul>
              {preview.steering.arc?.length > 0 && (
                <ol className="mt-3 space-y-0.5 text-[13px] text-ash">
                  {preview.steering.arc.map((a: string, i: number) => (
                    <li key={i}>
                      <span className="font-mono text-xs text-dust">{i + 1}</span> {a}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-[340px_minmax(0,1fr)]">
        <nav aria-label="Steering packs" className="space-y-7">
          {(["pack", "overlay", "core"] as const).map((k) => (
            <div key={k}>
              <h2 className="mb-2 text-xs text-dust">{KIND_LABEL[k]}</h2>
              <ul className="space-y-1">
                {(groups[k] ?? []).map((p) => (
                  <li key={p.id}>
                    <button
                      onClick={() => {
                        setSel(p.id);
                        setEditing(null);
                      }}
                      aria-current={active?.id === p.id}
                      className={`flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm transition-colors ${active?.id === p.id ? "bg-basalt-3 text-moon" : "text-ash hover:bg-basalt-2"}`}
                    >
                      <span className="flex-1 truncate">{p.name}</span>
                      {p.source === "learned" && <span className="rounded-full border border-ok/40 px-2 text-[11px] text-ok">learned</span>}
                      {applied.has(p.id) && <span className="size-1.5 rounded-full bg-saffron" title="Would apply to the tested request" />}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {packs && packs.length === 0 && <p className="text-sm text-dust">Start the backend to load steering packs.</p>}
        </nav>

        {active && (
          <article className="rounded-2xl border border-regolith/70 bg-basalt-2 p-6">
            <div className="flex flex-wrap items-start gap-3">
              <div className="flex-1">
                <h2 className="font-display text-2xl font-semibold tracking-[-0.02em]">{active.name}</h2>
                <p className="mt-2 max-w-[65ch] text-sm text-ash">{active.description}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => startEdit(active)} className="rounded-full border border-regolith px-3.5 py-1.5 text-sm text-ash hover:text-moon">
                  Edit
                </button>
                <button
                  onClick={() => startEdit({ ...active, id: `${active.id}-copy`, name: `${active.name} (copy)`, source: "user" })}
                  className="rounded-full border border-regolith px-3.5 py-1.5 text-sm text-ash hover:text-moon"
                >
                  Duplicate
                </button>
                {active.source !== "core" && active.kind !== "core" && (
                  <button
                    onClick={async () => {
                      if (confirm(`Delete “${active.name}”?`)) {
                        await api.deleteSteering(active.id);
                        setSel(null);
                        load();
                      }
                    }}
                    className="rounded-full border border-regolith px-3.5 py-1.5 text-sm text-dust hover:border-err/60 hover:text-err"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>

            {editing === active.id || (editing && editing.endsWith("-copy")) ? (
              <div className="mt-6">
                <textarea
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  rows={24}
                  spellCheck={false}
                  aria-label="Pack JSON"
                  className="scrollbar-thin w-full rounded-xl border border-regolith bg-basalt p-4 font-mono text-[12.5px] leading-relaxed text-ash focus:border-regolith-2 focus:outline-none"
                />
                {err && <p className="mt-2 text-sm text-err">{err}</p>}
                <div className="mt-3 flex gap-2">
                  <button onClick={save} className="rounded-full bg-saffron px-5 py-2 text-sm font-semibold text-basalt">
                    Save pack
                  </button>
                  <button onClick={() => setEditing(null)} className="rounded-full border border-regolith px-4 py-2 text-sm text-ash">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="mt-6 grid gap-8 md:grid-cols-2">
                {active.arc && (
                  <section>
                    <h3 className="text-sm font-medium">Arc</h3>
                    <ol className="mt-3 space-y-2">
                      {active.arc.map((a, i) => {
                        const [beat, rest] = a.split(/:(.+)/);
                        return (
                          <li key={i} className="flex gap-3 text-sm">
                            <span className="mt-0.5 font-mono text-xs text-dust">{i + 1}</span>
                            <span>
                              <span className="text-moon capitalize">{beat}</span>
                              {rest && <span className="text-dust"> — {rest.trim()}</span>}
                            </span>
                          </li>
                        );
                      })}
                    </ol>
                  </section>
                )}
                <section className="space-y-5 text-sm">
                  {active.match && (
                    <div>
                      <h3 className="font-medium">Matches</h3>
                      <p className="mt-2 text-ash">
                        {[...(active.match.intents ?? []), ...(active.match.domains ?? []), ...(active.match.audiences ?? [])].map((x) => x.replace(/_/g, " ")).join(", ") || "—"}
                      </p>
                      {active.match.keywords?.length ? <p className="mt-1 text-dust">Keywords: {active.match.keywords.join(", ")}</p> : null}
                    </div>
                  )}
                  {active.settings && (
                    <div>
                      <h3 className="font-medium">Settings</h3>
                      <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1">
                        {Object.entries(active.settings).map(([k, v]) => (
                          <div key={k} className="flex gap-2">
                            <dt className="text-dust">{k.replace(/_/g, " ")}</dt>
                            <dd className="text-ash">{String(v)}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  )}
                  {active.visuals && (
                    <div>
                      <h3 className="font-medium">Visuals</h3>
                      {active.visuals.prefer?.length ? <p className="mt-2 text-ash">Prefer {active.visuals.prefer.join(", ")}</p> : null}
                      {active.visuals.avoid?.length ? <p className="mt-1 text-dust">Avoid {active.visuals.avoid.join(", ")}</p> : null}
                    </div>
                  )}
                  {active.narration && (
                    <div>
                      <h3 className="font-medium">Narration</h3>
                      {active.narration.tone && <p className="mt-2 text-ash">{active.narration.tone}</p>}
                      <ul className="mt-1 list-disc space-y-1 pl-4 text-dust">
                        {active.narration.rules?.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>
                  )}
                  {active.rules && (
                    <div>
                      <h3 className="font-medium">Rules</h3>
                      <ul className="mt-2 space-y-1">
                        {active.rules.do?.map((r, i) => (
                          <li key={`d${i}`} className="text-ash">
                            <span className="text-ok">Do</span> {r}
                          </li>
                        ))}
                        {active.rules.dont?.map((r, i) => (
                          <li key={`n${i}`} className="text-ash">
                            <span className="text-err">Don&apos;t</span> {r.replace(/^Don'?t\s+/i, "")}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </section>
              </div>
            )}
          </article>
        )}
      </div>
    </div>
  );
}
