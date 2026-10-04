export const API = process.env.NEXT_PUBLIC_PRAGYAN_API ?? "http://127.0.0.1:8000";

export const media = (p?: string | null) => (!p ? "" : p.startsWith("http") ? p : `${API}${p}`);

export type JobOptions = {
  target_seconds: number;
  audience?: string | null;
  theme?: string | null;
  background?: string | null;
  voice?: string | null;
  language: string;
  captions: boolean;
  quiz?: boolean | null;
  quality: "draft" | "standard" | "high";
  critic: boolean;
  allow_manim: boolean;
  steering_ids?: string[];
};

export type SceneState = {
  index: number;
  id: string;
  chapter: string;
  purpose: string;
  type: string;
  status: "queued" | "designing" | "designed" | "narrating" | "animating" | "ready";
  visual?: Record<string, unknown>;
  segments?: string[];
  durationInFrames?: number;
  audio_url?: string;
  fallback?: boolean;
  manim?: { ok: boolean; attempts: number; code: string };
  critic?: string;
};

export type Outputs = {
  video: string;
  poster?: string;
  srt: string;
  vtt: string;
  transcript: string;
  storyboard: string;
  spec: string;
  duration: number;
  chapters: { t: number; title: string }[];
};

export type Job = {
  id: string;
  title: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  stage: string;
  created_at: string;
  input: { prompt: string; options: JobOptions; files: { name: string; kind: string; url: string }[] };
  data?: {
    intent?: Record<string, any>;
    steering?: { packs: { id: string; name: string; kind: string; score: number }[]; settings: Record<string, any>; arc: string[] };
    settings?: Record<string, any>;
    knowledge?: Record<string, any>;
    outline?: { title: string; logline: string; scenes: any[] };
  };
  scenes?: SceneState[];
  outputs?: Outputs;
  metrics?: Record<string, any>;
  quiz?: { question: string; options: string[]; answerIndex: number; explanation?: string };
  rating?: number;
  error?: string;
  running?: boolean;
};

export type AgentNode = {
  id: string;
  kind: string;
  label: string;
  parent: string | null;
  detail?: string;
  status: "working" | "done" | "error";
  summary?: string;
  seconds?: number;
  tokens: number;
  started: number;
};

export type LogLine = { seq: number; ts: number; agent: string; text: string; level?: string };

async function j<T>(r: Response): Promise<T> {
  if (!r.ok) {
    let msg = `${r.status}`;
    try {
      const b = await r.json();
      msg = b.detail ?? msg;
    } catch {}
    throw new Error(msg);
  }
  return r.json();
}

export const api = {
  system: () => fetch(`${API}/api/system`, { cache: "no-store" }).then((r) => j<any>(r)),
  jobs: () => fetch(`${API}/api/jobs`, { cache: "no-store" }).then((r) => j<Job[]>(r)),
  job: (id: string) => fetch(`${API}/api/jobs/${id}`, { cache: "no-store" }).then((r) => j<Job>(r)),
  create: (prompt: string, options: JobOptions, files: File[]) => {
    const fd = new FormData();
    fd.append("prompt", prompt);
    fd.append("options", JSON.stringify(options));
    files.forEach((f) => fd.append("files", f));
    return fetch(`${API}/api/jobs`, { method: "POST", body: fd }).then((r) => j<{ id: string }>(r));
  },
  cancel: (id: string) => fetch(`${API}/api/jobs/${id}/cancel`, { method: "POST" }).then((r) => j<any>(r)),
  remove: (id: string) => fetch(`${API}/api/jobs/${id}`, { method: "DELETE" }).then((r) => j<any>(r)),
  regenerate: (id: string, index: number, instruction: string, visual_type?: string) =>
    fetch(`${API}/api/jobs/${id}/scenes/${index}/regenerate`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ instruction, visual_type }),
    }).then((r) => j<any>(r)),
  updateScene: (id: string, index: number, body: { segments?: string[]; visual?: any }) =>
    fetch(`${API}/api/jobs/${id}/scenes/${index}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).then((r) => j<any>(r)),
  rerender: (id: string, body: Record<string, unknown>) =>
    fetch(`${API}/api/jobs/${id}/rerender`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).then((r) => j<any>(r)),
  feedback: (id: string, rating: number, notes: string, learn: boolean) =>
    fetch(`${API}/api/jobs/${id}/feedback`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ rating, notes, learn }) }).then((r) => j<any>(r)),
  steering: () => fetch(`${API}/api/steering`, { cache: "no-store" }).then((r) => j<any[]>(r)),
  saveSteering: (p: any) => fetch(`${API}/api/steering`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(p) }).then((r) => j<any>(r)),
  deleteSteering: (id: string) => fetch(`${API}/api/steering/${id}`, { method: "DELETE" }).then((r) => j<any>(r)),
  previewSteering: (prompt: string) =>
    fetch(`${API}/api/steering/preview`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ prompt }) }).then((r) => j<any>(r)),
  voices: () => fetch(`${API}/api/voices`).then((r) => j<{ voices: string[] }>(r)),
};

export const VISUAL_LABEL: Record<string, string> = {
  title: "Title",
  kinetic: "Kinetic type",
  bullets: "Points",
  definition: "Definition",
  equation: "Derivation",
  steps: "Steps",
  diagram: "Flow diagram",
  comparison: "Comparison",
  stats: "Numbers",
  chart: "Chart",
  code: "Code",
  quote: "Quote",
  image: "Your image",
  timeline: "Timeline",
  orbit3d: "3D orbit",
  cards3d: "3D cards",
  manim: "Manim animation",
  summary: "Takeaways",
  quiz: "Quiz",
};

export const STAGES = [
  { id: "ingest", label: "Read" },
  { id: "understand", label: "Understand" },
  { id: "steer", label: "Steer" },
  { id: "think", label: "Think" },
  { id: "storyboard", label: "Storyboard" },
  { id: "produce", label: "Produce" },
  { id: "review", label: "Review" },
  { id: "render", label: "Render" },
];
