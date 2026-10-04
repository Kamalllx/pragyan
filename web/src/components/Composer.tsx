"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, type JobOptions } from "@/lib/api";

const THEMES: { id: string | null; label: string; swatch: [string, string] }[] = [
  { id: null, label: "Auto", swatch: ["#2f3238", "#8f8b83"] },
  { id: "cosmos", label: "Cosmos", swatch: ["#08090D", "#E8A33D"] },
  { id: "midnight", label: "Midnight", swatch: ["#06070C", "#7C9CFF"] },
  { id: "chalk", label: "Chalkboard", swatch: ["#18201D", "#F2C14E"] },
  { id: "paper", label: "Paper", swatch: ["#F1ECE2", "#D2491E"] },
  { id: "neon", label: "Neon", swatch: ["#040406", "#00E5C7"] },
  { id: "solar", label: "Solar", swatch: ["#110B07", "#FF8A3D"] },
];

const LENGTHS = [
  { s: 45, label: "45 s" },
  { s: 60, label: "1 min" },
  { s: 90, label: "1.5 min" },
  { s: 120, label: "2 min" },
];

const LANGS = [
  { id: "en", label: "English" },
  { id: "hi", label: "Hindi" },
  { id: "es", label: "Spanish" },
  { id: "fr", label: "French" },
];

const EXAMPLES = [
  "Why is the sky blue but sunsets are red?",
  "Solve ∫₀¹ x·eˣ dx and explain every step",
  "How does attention work inside a transformer?",
  "Pitch my project: an app that turns any question into an explainer video",
  "TCP vs UDP — which should a game use?",
  "The story of the Pragyan rover on the Moon",
];

export function Composer() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [more, setMore] = useState(false);
  const [voices, setVoices] = useState<string[]>([]);
  const [opts, setOpts] = useState<JobOptions>({
    target_seconds: 60,
    theme: null,
    voice: null,
    language: "en",
    captions: true,
    quiz: null,
    quality: "standard",
    critic: true,
    allow_manim: true,
  });
  const ta = useRef<HTMLTextAreaElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.voices().then((v) => setVoices(v.voices)).catch(() => {});
  }, []);

  useEffect(() => {
    const el = ta.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = Math.min(320, Math.max(120, el.scrollHeight)) + "px";
  }, [prompt]);

  const addFiles = useCallback((list: FileList | File[]) => {
    const arr = Array.from(list).slice(0, 6);
    setFiles((f) => [...f, ...arr].slice(0, 6));
  }, []);

  const submit = async () => {
    if (busy) return;
    if (!prompt.trim() && files.length === 0) {
      setErr("Type a question or attach an image, PDF or notes first.");
      ta.current?.focus();
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const { id } = await api.create(prompt, opts, files);
      router.push(`/jobs/${id}`);
    } catch (e: any) {
      setErr(`Couldn't start the job: ${e.message}. Is the backend running on port 8000?`);
      setBusy(false);
    }
  };

  const set = <K extends keyof JobOptions>(k: K, v: JobOptions[K]) => setOpts((o) => ({ ...o, [k]: v }));

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
        }}
        className={`relative rounded-[22px] border bg-basalt-2 transition-colors ${
          drag ? "border-saffron" : "border-regolith focus-within:border-regolith-2"
        } shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_30px_80px_-40px_rgba(0,0,0,0.8)]`}
      >
        <label htmlFor="prompt" className="sr-only">
          What should Pragyan explain?
        </label>
        <textarea
          id="prompt"
          ref={ta}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit();
          }}
          onPaste={(e) => {
            if (e.clipboardData.files.length) addFiles(e.clipboardData.files);
          }}
          placeholder="Ask a question, paste a problem, describe your project — or drop an image or PDF here."
          className="block w-full resize-none bg-transparent px-6 pt-5 pb-2 text-[17px] leading-relaxed text-moon placeholder:text-dust/70 focus:outline-none"
        />

        {files.length > 0 && (
          <ul className="flex flex-wrap gap-2 px-6 pb-2">
            {files.map((f, i) => (
              <li key={i} className="flex items-center gap-2 rounded-full border border-regolith bg-basalt-3 py-1 pr-1 pl-1 text-xs text-ash">
                {f.type.startsWith("image/") ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={URL.createObjectURL(f)} alt="" className="size-6 rounded-full object-cover" />
                ) : (
                  <span className="grid size-6 place-items-center rounded-full bg-regolith font-mono text-[9px] uppercase">{f.name.split(".").pop()}</span>
                )}
                <span className="max-w-[180px] truncate">{f.name}</span>
                <button
                  onClick={() => setFiles((x) => x.filter((_, j) => j !== i))}
                  className="grid size-6 place-items-center rounded-full text-dust hover:bg-regolith hover:text-moon"
                  aria-label={`Remove ${f.name}`}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}

        <div className="flex flex-wrap items-center gap-2 border-t border-regolith/70 px-4 py-3">
          <button
            onClick={() => fileInput.current?.click()}
            className="flex items-center gap-2 rounded-full px-3 py-2 text-sm text-ash hover:bg-basalt-3 hover:text-moon"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
              <path d="M21 12.5 12.6 20.9a5.5 5.5 0 0 1-7.8-7.8L13.6 4.3a3.7 3.7 0 0 1 5.2 5.2L10 18.3a1.8 1.8 0 0 1-2.6-2.6l8.1-8.1" strokeLinecap="round" />
            </svg>
            Attach
          </button>
          <input
            ref={fileInput}
            type="file"
            multiple
            accept="image/*,.pdf,.txt,.md,.py,.js,.ts,.tsx,.java,.c,.cpp,.go,.rs,.json,.csv"
            className="hidden"
            onChange={(e) => e.target.files && addFiles(e.target.files)}
          />

          <Segmented
            label="Length"
            value={opts.target_seconds}
            onChange={(v) => set("target_seconds", v)}
            options={LENGTHS.map((l) => ({ value: l.s, label: l.label }))}
          />

          <button
            onClick={() => setMore((m) => !m)}
            aria-expanded={more}
            className={`rounded-full px-3 py-2 text-sm ${more ? "bg-basalt-3 text-moon" : "text-ash hover:bg-basalt-3 hover:text-moon"}`}
          >
            Style &amp; voice
          </button>

          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-xs text-dust sm:inline">Ctrl + Enter</span>
            <button
              onClick={submit}
              disabled={busy}
              className="rounded-full bg-saffron px-5 py-2.5 text-sm font-semibold text-basalt transition-[transform,background] hover:bg-[#f0b456] active:scale-[0.97] disabled:opacity-60"
            >
              {busy ? "Starting…" : "Make the video"}
            </button>
          </div>
        </div>

        {more && (
          <div className="grid gap-5 border-t border-regolith/70 px-6 py-5 md:grid-cols-2">
            <Field label="Look">
              <div className="flex flex-wrap gap-2">
                {THEMES.map((t) => (
                  <button
                    key={t.label}
                    onClick={() => set("theme", t.id)}
                    aria-pressed={opts.theme === t.id}
                    className={`flex items-center gap-2 rounded-full border py-1 pr-3 pl-1 text-xs ${
                      opts.theme === t.id ? "border-saffron text-moon" : "border-regolith text-ash hover:border-regolith-2"
                    }`}
                  >
                    <span className="relative size-5 overflow-hidden rounded-full" style={{ background: t.swatch[0] }}>
                      <span className="absolute right-0.5 bottom-0.5 size-2 rounded-full" style={{ background: t.swatch[1] }} />
                    </span>
                    {t.label}
                  </button>
                ))}
              </div>
            </Field>
            <Field label="Narration">
              <div className="flex flex-wrap gap-2">
                <select
                  value={opts.language}
                  onChange={(e) => set("language", e.target.value)}
                  className="rounded-lg border border-regolith bg-basalt-3 px-3 py-1.5 text-sm text-moon"
                  aria-label="Language"
                >
                  {LANGS.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.label}
                    </option>
                  ))}
                </select>
                <select
                  value={opts.voice ?? ""}
                  onChange={(e) => set("voice", e.target.value || null)}
                  className="rounded-lg border border-regolith bg-basalt-3 px-3 py-1.5 text-sm text-moon"
                  aria-label="Voice"
                >
                  <option value="">Voice picked by style</option>
                  {voices.map((v) => (
                    <option key={v} value={v}>
                      {v}
                    </option>
                  ))}
                </select>
              </div>
            </Field>
            <Field label="Quality">
              <Segmented
                value={opts.quality}
                onChange={(v) => set("quality", v)}
                options={[
                  { value: "draft", label: "Draft · fast" },
                  { value: "standard", label: "1080p" },
                  { value: "high", label: "1080p + HQ maths" },
                ]}
              />
            </Field>
            <Field label="Extras">
              <div className="flex flex-wrap gap-2">
                <Toggle on={opts.captions} set={(v) => set("captions", v)} label="Captions" />
                <Toggle on={opts.quiz !== false} set={(v) => set("quiz", v ? null : false)} label="Quiz at the end" />
                <Toggle on={opts.allow_manim} set={(v) => set("allow_manim", v)} label="Manim animations" />
                <Toggle on={opts.critic} set={(v) => set("critic", v)} label="Self-review" />
              </div>
            </Field>
          </div>
        )}
      </div>

      {err && (
        <p role="alert" className="mt-3 text-sm text-err">
          {err}
        </p>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        {EXAMPLES.map((e) => (
          <button
            key={e}
            onClick={() => {
              setPrompt(e);
              ta.current?.focus();
            }}
            className="rounded-full border border-regolith/80 px-3.5 py-1.5 text-left text-[13px] text-ash transition-colors hover:border-regolith-2 hover:text-moon"
          >
            {e}
          </button>
        ))}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-2 text-xs text-dust">{label}</div>
      {children}
    </div>
  );
}

function Segmented<T extends string | number>({
  value,
  onChange,
  options,
  label,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
  label?: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="flex rounded-full border border-regolith bg-basalt p-0.5">
      {options.map((o) => (
        <button
          key={String(o.value)}
          role="radio"
          aria-checked={value === o.value}
          onClick={() => onChange(o.value)}
          className={`rounded-full px-3 py-1.5 text-xs transition-colors ${value === o.value ? "bg-basalt-3 text-moon" : "text-dust hover:text-ash"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function Toggle({ on, set, label }: { on: boolean; set: (v: boolean) => void; label: string }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      onClick={() => set(!on)}
      className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs ${on ? "border-regolith-2 text-moon" : "border-regolith text-dust"}`}
    >
      <span className={`relative h-3.5 w-6 rounded-full transition-colors ${on ? "bg-saffron" : "bg-regolith"}`}>
        <span className={`absolute top-0.5 size-2.5 rounded-full bg-basalt transition-[left] ${on ? "left-3" : "left-0.5"}`} />
      </span>
      {label}
    </button>
  );
}
