"use client";

import { motion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { STAGES, VISUAL_LABEL, api, media, type AgentNode, type LogLine, type Outputs, type SceneState } from "@/lib/api";

/* ------------------------------------------------------------------ */
/* Stage rail                                                          */
/* ------------------------------------------------------------------ */
export function StageRail({ stage, progress, label, status }: { stage: string; progress: number; label: string; status: string }) {
  const idx = STAGES.findIndex((s) => s.id === stage);
  const done = status === "done" || stage === "done";
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className={status === "failed" ? "text-err" : "text-ash"}>{done ? "Finished" : status === "failed" ? "Stopped" : label}</span>
        <span className="font-mono text-xs text-dust">{Math.round(progress * 100)}%</span>
      </div>
      <div className="relative mt-2 h-1 overflow-hidden rounded-full bg-regolith/60">
        <motion.div
          className={`absolute inset-y-0 left-0 rounded-full ${status === "failed" ? "bg-err" : "bg-saffron"}`}
          animate={{ width: `${Math.max(2, progress * 100)}%` }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <ol className="mt-3 hidden grid-cols-8 gap-1 text-[11px] sm:grid" aria-label="Pipeline stages">
        {STAGES.map((s, i) => {
          const state = done || i < idx ? "done" : i === idx ? "now" : "next";
          return (
            <li key={s.id} className={state === "now" ? "text-earth" : state === "done" ? "text-ash" : "text-dust/60"} aria-current={state === "now" ? "step" : undefined}>
              {s.label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Activity log — real machine output, hence mono                       */
/* ------------------------------------------------------------------ */
export function ActivityLog({ logs, agents, filter, onClear }: { logs: LogLine[]; agents: Record<string, AgentNode>; filter: string | null; onClear: () => void }) {
  const box = useRef<HTMLDivElement>(null);
  const [stick, setStick] = useState(true);
  const shown = filter ? logs.filter((l) => l.agent === filter || agents[l.agent]?.parent === filter) : logs;
  useEffect(() => {
    if (stick && box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [shown.length, stick]);
  return (
    <div className="flex h-full min-h-[420px] flex-col rounded-2xl border border-regolith/70 bg-basalt-2">
      <div className="flex items-center justify-between border-b border-regolith/70 px-4 py-2.5">
        <h3 className="text-sm font-medium">Activity</h3>
        {filter ? (
          <button onClick={onClear} className="rounded-full bg-basalt-3 px-2.5 py-1 text-xs text-ash hover:text-moon">
            {agents[filter]?.label} · show all
          </button>
        ) : (
          <span className="text-xs text-dust">{logs.length} events</span>
        )}
      </div>
      <div
        ref={box}
        onScroll={(e) => {
          const el = e.currentTarget;
          setStick(el.scrollHeight - el.scrollTop - el.clientHeight < 40);
        }}
        className="scrollbar-thin flex-1 overflow-y-auto px-4 py-3 font-mono text-[12px] leading-[1.65]"
        aria-live="polite"
      >
        {shown.map((l) => {
          const a = agents[l.agent];
          const t = new Date(l.ts * 1000).toLocaleTimeString([], { hour12: false });
          const tone =
            l.level === "error" ? "text-err" : l.level === "warn" ? "text-saffron" : l.level === "spawn" ? "text-earth" : l.level === "done" ? "text-ok/90" : "text-ash";
          return (
            <div key={l.seq + l.agent + l.text.slice(0, 8)} className="flex gap-3">
              <span className="shrink-0 text-dust/60">{t}</span>
              <span className="w-[150px] shrink-0 truncate text-dust">{a?.label ?? l.agent}</span>
              <span className={`min-w-0 break-words whitespace-pre-wrap ${tone}`}>{l.text}</span>
            </div>
          );
        })}
        {shown.length === 0 && <p className="text-dust">Waiting for the first agent…</p>}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Video                                                               */
/* ------------------------------------------------------------------ */
export function VideoPanel({ outputs, version }: { outputs: Outputs; version: number }) {
  const v = useRef<HTMLVideoElement>(null);
  const [t, setT] = useState(0);
  const src = `${media(outputs.video)}?v=${version}`;
  const chapters = outputs.chapters ?? [];
  const cur = chapters.reduce((acc, c, i) => (t >= c.t ? i : acc), 0);
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
      <div className="overflow-hidden rounded-2xl border border-regolith/70 bg-black shadow-[0_40px_120px_-50px_rgba(0,0,0,0.9)]">
        <video ref={v} key={src} src={src} poster={media(outputs.poster)} controls playsInline className="aspect-video w-full" onTimeUpdate={(e) => setT(e.currentTarget.currentTime)}>
          <track kind="captions" src={media(outputs.vtt)} srcLang="en" label="English" />
        </video>
      </div>
      <div className="flex flex-col gap-5">
        <div>
          <h3 className="mb-2 text-sm font-medium text-ash">Chapters</h3>
          <ol className="space-y-0.5">
            {chapters.map((c, i) => (
              <li key={i}>
                <button
                  onClick={() => {
                    if (v.current) {
                      v.current.currentTime = c.t + 0.05;
                      v.current.play();
                    }
                  }}
                  className={`flex w-full items-baseline gap-3 rounded-lg px-2 py-1.5 text-left text-sm transition-colors ${i === cur ? "bg-basalt-3 text-moon" : "text-ash hover:bg-basalt-2"}`}
                >
                  <span className="w-10 shrink-0 font-mono text-xs text-dust">
                    {Math.floor(c.t / 60)}:{String(Math.floor(c.t % 60)).padStart(2, "0")}
                  </span>
                  <span className="truncate">{c.title}</span>
                </button>
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h3 className="mb-2 text-sm font-medium text-ash">Download</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { k: "video", l: "MP4" },
              { k: "srt", l: "Subtitles" },
              { k: "transcript", l: "Transcript" },
              { k: "storyboard", l: "Storyboard" },
              { k: "spec", l: "Render spec" },
            ].map((d) => (
              <a key={d.k} href={media((outputs as any)[d.k])} download className="rounded-full border border-regolith px-3 py-1.5 text-xs text-ash hover:border-regolith-2 hover:text-moon">
                {d.l}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Storyboard                                                          */
/* ------------------------------------------------------------------ */
const STATUS_TEXT: Record<string, string> = { queued: "Queued", designing: "Designing", designed: "Designed", narrating: "Voicing", animating: "Animating", ready: "Ready" };
const VISUAL_CHOICES = ["bullets", "diagram", "equation", "steps", "comparison", "definition", "kinetic", "cards3d", "orbit3d", "timeline", "manim", "summary", "quote", "code", "stats", "chart"];

export function Storyboard({ scenes, jobId, editable, onEdited }: { scenes: SceneState[]; jobId: string; editable: boolean; onEdited: () => void }) {
  const [open, setOpen] = useState<number | null>(null);
  if (!scenes.length) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="shimmer h-28 rounded-xl border border-regolith/50 bg-basalt-2" />
        ))}
      </div>
    );
  }
  return (
    <div>
      <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {scenes.map((s) =>
          s ? (
            <li key={s.index}>
              <button
                onClick={() => setOpen(open === s.index ? null : s.index)}
                aria-expanded={open === s.index}
                className={`flex h-full w-full flex-col rounded-xl border p-3.5 text-left transition-colors ${
                  open === s.index ? "border-saffron/70 bg-basalt-3" : "border-regolith/70 bg-basalt-2 hover:border-regolith-2"
                }`}
              >
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-mono text-dust">{String(s.index + 1).padStart(2, "0")}</span>
                  <span className="text-ash">{VISUAL_LABEL[s.type] ?? s.type}</span>
                  <span className={`ml-auto flex items-center gap-1.5 ${s.status === "ready" ? "text-dust" : "text-earth"}`}>
                    {s.status !== "ready" && <span className="size-1.5 animate-pulse rounded-full bg-earth" />}
                    {STATUS_TEXT[s.status] ?? s.status}
                  </span>
                </div>
                <div className="mt-2 font-display text-[15px] leading-snug font-medium text-moon">{s.chapter}</div>
                <p className="mt-1 line-clamp-2 text-[13px] leading-snug text-dust">{s.segments?.filter(Boolean).join(" ") || s.purpose}</p>
                <div className="mt-auto flex flex-wrap gap-1.5 pt-2.5">
                  {s.manim && (
                    <Chip tone={s.manim.ok ? "ok" : "err"}>
                      {s.manim.ok ? `Manim · ${s.manim.attempts} ${s.manim.attempts === 1 ? "try" : "tries"}` : "Manim failed"}
                    </Chip>
                  )}
                  {s.fallback && <Chip tone="warn">Fallback layout</Chip>}
                  {s.critic && <Chip tone="warn">Revised by critic</Chip>}
                  {s.durationInFrames ? <Chip>{(s.durationInFrames / 30).toFixed(1)} s</Chip> : null}
                </div>
              </button>
            </li>
          ) : null,
        )}
      </ol>
      {open !== null && scenes[open] && <SceneDetail scene={scenes[open]} jobId={jobId} editable={editable} onEdited={onEdited} />}
    </div>
  );
}

function Chip({ children, tone }: { children: React.ReactNode; tone?: "ok" | "err" | "warn" }) {
  const c = tone === "ok" ? "text-ok border-ok/30" : tone === "err" ? "text-err border-err/30" : tone === "warn" ? "text-saffron border-saffron/30" : "text-dust border-regolith";
  return <span className={`rounded-full border px-2 py-0.5 text-[11px] ${c}`}>{children}</span>;
}

function SceneDetail({ scene, jobId, editable, onEdited }: { scene: SceneState; jobId: string; editable: boolean; onEdited: () => void }) {
  const [instr, setInstr] = useState("");
  const [vt, setVt] = useState(scene.type);
  const [segs, setSegs] = useState<string[]>(scene.segments ?? []);
  const [busy, setBusy] = useState("");
  const [msg, setMsg] = useState("");
  const [showCode, setShowCode] = useState(false);
  useEffect(() => {
    setSegs(scene.segments ?? []);
    setVt(scene.type);
  }, [scene.index, scene.segments, scene.type]);

  const run = async (kind: "regen" | "narration") => {
    setBusy(kind);
    setMsg("");
    try {
      if (kind === "regen") await api.regenerate(jobId, scene.index, instr || "Make this scene clearer and more visual.", vt !== scene.type ? vt : undefined);
      else await api.updateScene(jobId, scene.index, { segments: segs });
      setMsg(kind === "regen" ? "Regenerating this scene — the video re-renders when it's done." : "Re-voicing and re-rendering with your narration.");
      onEdited();
    } catch (e: any) {
      setMsg(e.message === "409" || /busy/.test(e.message) ? "Pragyan is still working on this video. Try again when it finishes." : `Couldn't apply the edit: ${e.message}`);
    } finally {
      setBusy("");
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mt-4 grid gap-6 rounded-2xl border border-regolith/70 bg-basalt-2 p-5 lg:grid-cols-2">
      <div>
        <h4 className="text-sm font-medium">Narration</h4>
        <p className="mt-1 text-xs text-dust">Each line plays while its item appears on screen.</p>
        <div className="mt-3 space-y-2">
          {segs.map((s, i) => (
            <textarea
              key={i}
              value={s}
              disabled={!editable}
              onChange={(e) => setSegs((x) => x.map((y, j) => (j === i ? e.target.value : y)))}
              rows={Math.max(1, Math.ceil(s.length / 70))}
              aria-label={`Narration line ${i + 1}`}
              className="w-full resize-y rounded-lg border border-regolith bg-basalt px-3 py-2 text-sm leading-relaxed text-moon focus:border-regolith-2 focus:outline-none disabled:opacity-70"
              placeholder={i === 0 ? "(silent intro)" : ""}
            />
          ))}
        </div>
        {editable && (
          <button
            onClick={() => run("narration")}
            disabled={!!busy || JSON.stringify(segs) === JSON.stringify(scene.segments)}
            className="mt-3 rounded-full border border-regolith-2 px-4 py-2 text-sm text-moon hover:bg-basalt-3 disabled:opacity-40"
          >
            {busy === "narration" ? "Saving…" : "Re-voice with these lines"}
          </button>
        )}
      </div>
      <div>
        <h4 className="text-sm font-medium">Redirect this scene</h4>
        <p className="mt-1 text-xs text-dust">Tell the designer what to change, or switch the visual entirely.</p>
        <textarea
          value={instr}
          onChange={(e) => setInstr(e.target.value)}
          rows={3}
          disabled={!editable}
          placeholder="e.g. Use a simpler analogy, show the units, make it a flow diagram"
          className="mt-3 w-full rounded-lg border border-regolith bg-basalt px-3 py-2 text-sm text-moon focus:border-regolith-2 focus:outline-none disabled:opacity-70"
        />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <label className="text-xs text-dust" htmlFor={`vt-${scene.index}`}>
            Visual
          </label>
          <select
            id={`vt-${scene.index}`}
            value={vt}
            disabled={!editable}
            onChange={(e) => setVt(e.target.value)}
            className="rounded-lg border border-regolith bg-basalt px-2.5 py-1.5 text-sm text-moon"
          >
            {[scene.type, ...VISUAL_CHOICES.filter((v) => v !== scene.type)].map((v) => (
              <option key={v} value={v}>
                {VISUAL_LABEL[v] ?? v}
              </option>
            ))}
          </select>
          {editable && (
            <button onClick={() => run("regen")} disabled={!!busy} className="ml-auto rounded-full bg-saffron px-4 py-2 text-sm font-semibold text-basalt disabled:opacity-50">
              {busy === "regen" ? "Sending…" : "Regenerate scene"}
            </button>
          )}
        </div>
        {scene.critic && <p className="mt-3 text-xs text-saffron">Critic note: {scene.critic}</p>}
        {scene.manim?.code && (
          <div className="mt-4">
            <button onClick={() => setShowCode((s) => !s)} className="text-xs text-earth hover:underline" aria-expanded={showCode}>
              {showCode ? "Hide" : "Show"} generated Manim code
            </button>
            {showCode && (
              <pre className="scrollbar-thin mt-2 max-h-72 overflow-auto rounded-lg border border-regolith bg-basalt p-3 font-mono text-[11.5px] leading-relaxed text-ash">{scene.manim.code}</pre>
            )}
          </div>
        )}
        {msg && (
          <p role="status" className="mt-3 text-sm text-ash">
            {msg}
          </p>
        )}
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Feedback → learned steering                                         */
/* ------------------------------------------------------------------ */
export function Feedback({ jobId, initial }: { jobId: string; initial?: number }) {
  const [rating, setRating] = useState(initial ?? 0);
  const [notes, setNotes] = useState("");
  const [state, setState] = useState<"idle" | "saving" | "saved">(initial ? "saved" : "idle");
  const [learned, setLearned] = useState<string | null>(null);
  const send = async () => {
    setState("saving");
    try {
      const r = await api.feedback(jobId, rating, notes, true);
      setLearned(r.learned?.name ?? null);
      setState("saved");
    } catch {
      setState("idle");
    }
  };
  return (
    <div className="rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
      <h3 className="text-sm font-medium">How did it land?</h3>
      <p className="mt-1 text-xs text-dust">Rate 4 or 5 and Pragyan distils this video&apos;s structure into a reusable steering pack.</p>
      <div className="mt-3 flex gap-1" role="radiogroup" aria-label="Rating">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            role="radio"
            aria-checked={rating === n}
            onClick={() => {
              setRating(n);
              setState("idle");
            }}
            className={`grid size-9 place-items-center rounded-full border text-sm transition-colors ${n <= rating ? "border-saffron bg-saffron/15 text-saffron" : "border-regolith text-dust hover:text-moon"}`}
          >
            {n}
          </button>
        ))}
      </div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={2}
        placeholder="What worked, what didn't (optional)"
        className="mt-3 w-full rounded-lg border border-regolith bg-basalt px-3 py-2 text-sm text-moon focus:border-regolith-2 focus:outline-none"
      />
      <button onClick={send} disabled={!rating || state === "saving"} className="mt-3 rounded-full border border-regolith-2 px-4 py-2 text-sm hover:bg-basalt-3 disabled:opacity-40">
        {state === "saving" ? (rating >= 4 ? "Learning from this video…" : "Saving…") : state === "saved" ? "Saved" : "Save rating"}
      </button>
      {learned && <p className="mt-3 text-sm text-ok">New steering pack learned: {learned}</p>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Interactive quiz (same question as the video's last scene)           */
/* ------------------------------------------------------------------ */
export function QuizCard({ quiz }: { quiz: { question: string; options: string[]; answerIndex: number; explanation?: string } }) {
  const [pick, setPick] = useState<number | null>(null);
  return (
    <div className="rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
      <h3 className="text-sm font-medium">Check yourself</h3>
      <p className="mt-2 font-display text-lg leading-snug">{quiz.question}</p>
      <div className="mt-3 grid gap-2">
        {quiz.options.map((o, i) => {
          const right = pick !== null && i === quiz.answerIndex;
          const wrong = pick === i && i !== quiz.answerIndex;
          return (
            <button
              key={i}
              onClick={() => setPick(i)}
              disabled={pick !== null}
              className={`flex items-center gap-3 rounded-xl border px-3 py-2.5 text-left text-sm transition-colors ${
                right ? "border-ok bg-ok/10 text-moon" : wrong ? "border-err bg-err/10 text-moon" : "border-regolith text-ash hover:border-regolith-2 hover:text-moon"
              }`}
            >
              <span className="font-mono text-xs text-dust">{String.fromCharCode(65 + i)}</span>
              {o}
            </button>
          );
        })}
      </div>
      {pick !== null && quiz.explanation && <p className="mt-3 text-sm text-ash">{quiz.explanation}</p>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Understanding + knowledge                                           */
/* ------------------------------------------------------------------ */
export function Understanding({ intent, steering, settings, plan }: { intent?: any; steering?: any; settings?: any; plan?: any }) {
  if (!intent) return null;
  const packs = (steering?.packs ?? []).filter((p: any) => p.kind !== "core");
  return (
    <div className="rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
      <h3 className="text-sm font-medium">What Pragyan understood</h3>
      <p className="mt-2 font-display text-lg leading-snug">{intent.key_question}</p>
      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
        <Def k="Video type" v={String(intent.intent).replace(/_/g, " ")} />
        <Def k="Subject" v={String(intent.domain).replace(/_/g, " ")} />
        <Def k="Audience" v={intent.audience_level} />
        <Def k="Tone" v={intent.tone} />
        {settings && <Def k="Look" v={`${settings.theme} · ${settings.background}`} />}
        {settings && <Def k="Voice" v={settings.voice ?? "auto"} raw />}
      </dl>
      {packs.length > 0 && (
        <div className="mt-4">
          <div className="text-xs text-dust">Steering applied</div>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {packs.map((p: any) => (
              <span key={p.id} className="rounded-full border border-saffron/30 px-2.5 py-1 text-xs text-saffron">
                {p.name}
              </span>
            ))}
          </div>
        </div>
      )}
      {plan?.agents?.length > 0 && (
        <div className="mt-4">
          <div className="text-xs text-dust">Specialists spawned</div>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {plan.agents.map((a: string) => (
              <span key={a} className="rounded-full border border-earth/30 px-2.5 py-1 text-xs text-earth">
                {a}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Def({ k, v, raw }: { k: string; v?: string; raw?: boolean }) {
  return (
    <div>
      <dt className="text-xs text-dust">{k}</dt>
      <dd className={`mt-0.5 text-ash ${raw ? "" : "first-letter:uppercase"}`}>{v || "—"}</dd>
    </div>
  );
}

export function SolutionCard({ solution, verification }: { solution: any; verification: any }) {
  const status = verification?.status;
  return (
    <div className="rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-medium">Worked solution</h3>
        <span
          className={`ml-auto rounded-full border px-2.5 py-0.5 text-xs ${
            status === "verified" ? "border-ok/40 text-ok" : status === "disputed" ? "border-err/40 text-err" : "border-regolith text-dust"
          }`}
          title={verification?.output}
        >
          {status === "verified" ? "Checked with SymPy" : status === "disputed" ? "Couldn't verify" : "Not machine-checked"}
        </span>
      </div>
      <ol className="mt-3 space-y-2.5 text-sm">
        {solution.steps?.map((s: any, i: number) => (
          <li key={i} className="flex gap-3">
            <span className="mt-0.5 font-mono text-xs text-dust">{i + 1}</span>
            <div>
              <div className="text-moon">{s.title}</div>
              <div className="text-[13px] text-dust">{s.explanation}</div>
            </div>
          </li>
        ))}
      </ol>
      <div className="mt-4 rounded-xl bg-basalt-3 px-4 py-3 text-sm">
        <span className="text-dust">Answer </span>
        <span className="text-moon">{solution.final_answer}</span>
      </div>
    </div>
  );
}

export function BriefCard({ brief }: { brief: any }) {
  return (
    <div className="rounded-2xl border border-regolith/70 bg-basalt-2 p-5">
      <h3 className="text-sm font-medium">Teaching brief</h3>
      <p className="mt-2 font-display text-lg leading-snug">{brief.hook_question}</p>
      <p className="mt-3 text-sm text-ash">{brief.core_idea}</p>
      {brief.analogy && (
        <p className="mt-3 border-l-2 border-saffron/60 pl-3 text-sm text-ash">
          <span className="text-dust">Analogy · </span>
          {brief.analogy}
        </p>
      )}
    </div>
  );
}
