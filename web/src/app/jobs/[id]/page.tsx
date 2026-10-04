"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Constellation } from "@/components/Constellation";
import { ActivityLog, BriefCard, Feedback, QuizCard, SolutionCard, StageRail, Storyboard, Understanding, VideoPanel } from "@/components/Mission";
import { api, type Job } from "@/lib/api";
import { useJobStream } from "@/lib/useJobStream";

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const s = useJobStream(id);
  const [job, setJob] = useState<Job | null>(null);
  const [missing, setMissing] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [showProcess, setShowProcess] = useState(false);

  const load = useCallback(() => {
    api
      .job(id)
      .then(setJob)
      .catch(() => setMissing(true));
  }, [id]);

  useEffect(load, [load]);
  // Refresh the persisted job whenever the stream reports a finish (initial run or an edit).
  useEffect(() => {
    if (s.outputs) load();
  }, [s.outputs, load]);

  if (missing)
    return (
      <div className="mx-auto max-w-xl px-6 py-24 text-center">
        <h1 className="font-display text-3xl font-semibold">This video doesn&apos;t exist</h1>
        <p className="mt-3 text-ash">It may have been deleted, or the backend was reset.</p>
        <Link href="/" className="mt-6 inline-block rounded-full bg-saffron px-5 py-2.5 text-sm font-semibold text-basalt">
          Back to the studio
        </Link>
      </div>
    );

  const status = s.status !== "live" ? s.status : job?.status === "done" && !job.running ? "done" : job?.status === "failed" ? "failed" : "live";
  const outputs = s.outputs ?? job?.outputs;
  const scenes = s.scenes.length ? s.scenes : job?.scenes ?? [];
  const intent = s.intent ?? job?.data?.intent;
  const steering = s.steering ?? job?.data?.steering;
  const settings = s.settings ?? job?.data?.settings;
  const solution = s.solution ?? (job?.data?.knowledge?.solution ? { solution: job.data.knowledge.solution, verification: job.data.knowledge.verification } : undefined);
  const brief = s.brief ?? job?.data?.knowledge?.brief;
  const working = status === "live";
  const title = s.outline?.title ?? job?.data?.outline?.title ?? job?.title ?? "…";
  const progress = status === "done" ? 1 : s.progress;
  const editable = status === "done" && !job?.running && s.stage !== "render";
  const hasAgents = Object.keys(s.agents).length > 0;
  const showMission = working || showProcess || !outputs;

  return (
    <div className="mx-auto max-w-[1440px] px-4 pt-8 pb-24 sm:px-6">
      {/* header */}
      <div className="flex flex-wrap items-start gap-6">
        <div className="min-w-0 flex-1">
          <Link href="/" className="text-sm text-dust hover:text-moon">
            Studio
          </Link>
          <h1 className="mt-2 max-w-[28ch] font-display text-[clamp(1.8rem,3.4vw,2.8rem)] leading-[1.05] font-semibold tracking-[-0.03em] text-balance">{title}</h1>
          {job?.input?.prompt && job.input.prompt !== title && <p className="mt-2 max-w-[70ch] text-sm text-dust">“{job.input.prompt}”</p>}
        </div>
        <div className="flex items-center gap-2 pt-7">
          {working && (
            <button
              onClick={() => api.cancel(id).then(load)}
              className="rounded-full border border-regolith px-4 py-2 text-sm text-ash hover:border-err/60 hover:text-err"
            >
              Stop
            </button>
          )}
          {!working && (
            <button
              onClick={async () => {
                if (confirm("Delete this video and its files?")) {
                  await api.remove(id);
                  router.push("/");
                }
              }}
              className="rounded-full border border-regolith px-4 py-2 text-sm text-dust hover:border-err/60 hover:text-err"
            >
              Delete
            </button>
          )}
        </div>
      </div>

      <div className="mt-6 max-w-3xl">
        <StageRail stage={status === "done" ? "done" : s.stage} progress={progress} label={s.render && s.stage === "render" ? `Rendering frames · ${Math.round(s.render.progress * 100)}%` : s.stageLabel} status={status} />
        {(s.error || job?.error) && status === "failed" && (
          <p role="alert" className="mt-4 rounded-xl border border-err/40 bg-err/10 px-4 py-3 text-sm text-moon">
            {s.error || job?.error}
          </p>
        )}
      </div>

      {/* finished film */}
      {outputs && (
        <section className="mt-10" aria-label="Video">
          <VideoPanel outputs={outputs} version={Date.parse((outputs as any).rendered_at ?? "") || 0} />
        </section>
      )}

      {outputs && !working && (
        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          {job?.quiz ? <QuizCard quiz={job.quiz} /> : brief ? <BriefCard brief={brief} /> : null}
          {solution ? <SolutionCard solution={solution.solution} verification={solution.verification} /> : <Understanding intent={intent} steering={steering} settings={settings} />}
          <Feedback jobId={id} initial={job?.rating} />
        </div>
      )}

      {/* mission control */}
      {outputs && !working && (
        <button onClick={() => setShowProcess((x) => !x)} className="mt-10 text-sm text-earth hover:underline" aria-expanded={showProcess}>
          {showProcess ? "Hide how it was made" : "See how it was made"}
        </button>
      )}

      {showMission && (
        <section className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]" aria-label="Agents at work">
          <div className="rounded-2xl border border-regolith/70 bg-basalt-2/60 p-4">
            <div className="flex items-center justify-between px-1">
              <h2 className="text-sm font-medium">Agents</h2>
              <span className="text-xs text-dust">
                {Object.values(s.agents).filter((a) => a.status === "working").length} working · {Object.keys(s.agents).length} spawned
                {s.tokens ? ` · ${s.tokens.toLocaleString()} tokens` : ""}
              </span>
            </div>
            {hasAgents ? (
              <Constellation agents={s.agents} order={s.order} selected={selected} onSelect={setSelected} live={working} />
            ) : (
              <div className="grid aspect-square place-items-center text-sm text-dust">{s.connected ? "Waking the orchestrator…" : "Connecting…"}</div>
            )}
          </div>
          <div className="flex flex-col gap-6">
            <ActivityLog logs={s.logs} agents={s.agents} filter={selected} onClear={() => setSelected(null)} />
            {working && <Understanding intent={intent} steering={steering} settings={settings} plan={s.plan} />}
            {working && solution && <SolutionCard solution={solution.solution} verification={solution.verification} />}
          </div>
        </section>
      )}

      <section className="mt-12" aria-labelledby="sb-h">
        <div className="mb-4 flex items-baseline justify-between">
          <h2 id="sb-h" className="font-display text-2xl font-semibold tracking-[-0.02em]">
            Storyboard
          </h2>
          {editable && <span className="text-xs text-dust">Open a scene to rewrite its narration or redirect it</span>}
        </div>
        <Storyboard scenes={scenes} jobId={id} editable={editable} onEdited={() => setTimeout(load, 500)} />
      </section>
    </div>
  );
}
