"use client";

import { useEffect, useReducer, useRef } from "react";
import { API, type AgentNode, type LogLine, type Outputs, type SceneState } from "./api";

export type StreamState = {
  connected: boolean;
  agents: Record<string, AgentNode>;
  order: string[];
  logs: LogLine[];
  stage: string;
  stageLabel: string;
  progress: number;
  render: { progress: number; phase?: string } | null;
  scenes: SceneState[];
  intent?: Record<string, any>;
  steering?: any;
  settings?: Record<string, any>;
  plan?: { agents: string[]; reasoning: string };
  solution?: { solution: any; verification: any };
  brief?: any;
  outline?: any;
  outputs?: Outputs;
  reviewStills: Record<number, string>;
  status: "live" | "done" | "failed" | "cancelled";
  error?: string;
  tokens: number;
  lastSeq: number;
};

const initial: StreamState = {
  connected: false,
  agents: {},
  order: [],
  logs: [],
  stage: "queued",
  stageLabel: "Waiting to start",
  progress: 0,
  render: null,
  scenes: [],
  reviewStills: {},
  status: "live",
  tokens: 0,
  lastSeq: 0,
};

type Ev = { seq: number; ts: number; type: string; [k: string]: any };

function reduce(s: StreamState, a: { kind: "ev"; ev: Ev } | { kind: "conn"; on: boolean } | { kind: "reset" }): StreamState {
  if (a.kind === "reset") return initial;
  if (a.kind === "conn") return { ...s, connected: a.on };
  const ev = a.ev;
  if (ev.seq && ev.seq <= s.lastSeq) return s;
  const n: StreamState = { ...s, lastSeq: ev.seq || s.lastSeq };
  const log = (agent: string, text: string, level?: string) => {
    n.logs = [...s.logs.slice(-600), { seq: ev.seq, ts: ev.ts, agent, text, level }];
  };
  switch (ev.type) {
    case "agent.spawn": {
      n.agents = {
        ...s.agents,
        [ev.agent]: { id: ev.agent, kind: ev.kind, label: ev.label, parent: ev.parent, detail: ev.detail, status: "working", tokens: 0, started: ev.ts },
      };
      n.order = s.order.includes(ev.agent) ? s.order : [...s.order, ev.agent];
      log(ev.agent, `${ev.label} started${ev.detail ? ` — ${ev.detail}` : ""}`, "spawn");
      break;
    }
    case "agent.done": {
      const ag = s.agents[ev.agent];
      if (ag) n.agents = { ...s.agents, [ev.agent]: { ...ag, status: "done", summary: ev.summary, seconds: ev.seconds } };
      log(ev.agent, ev.summary ? `done · ${ev.summary}` : "done", "done");
      break;
    }
    case "agent.error": {
      const ag = s.agents[ev.agent];
      if (ag) n.agents = { ...s.agents, [ev.agent]: { ...ag, status: "error", summary: ev.error, seconds: ev.seconds } };
      log(ev.agent, ev.error, "error");
      break;
    }
    case "agent.log":
      log(ev.agent, ev.message, ev.level);
      break;
    case "agent.llm": {
      const ag = s.agents[ev.agent];
      if (ag) n.agents = { ...s.agents, [ev.agent]: { ...ag, tokens: ag.tokens + (ev.tokens || 0) } };
      n.tokens = s.tokens + (ev.tokens || 0);
      break;
    }
    case "stage":
      if (ev.stage !== "done" && s.status !== "live") n.status = "live"; // an edit restarted work
      n.stage = ev.stage;
      n.stageLabel = ev.label || ev.stage;
      n.progress = Math.max(ev.stage === "done" ? 1 : 0, ev.progress ?? s.progress);
      break;
    case "render.progress":
      n.render = { progress: ev.progress ?? 0, phase: ev.phase };
      if (ev.overall) n.progress = ev.overall;
      break;
    case "understanding":
      n.intent = ev.intent;
      break;
    case "steering":
      n.steering = ev.steering;
      n.settings = ev.settings;
      break;
    case "plan":
      n.plan = { agents: ev.agents, reasoning: ev.reasoning };
      break;
    case "solution":
      n.solution = { solution: ev.solution, verification: ev.verification };
      break;
    case "brief":
      n.brief = ev.brief;
      break;
    case "storyboard":
      n.outline = ev.outline;
      n.scenes = ev.scenes;
      break;
    case "scene.update": {
      const sc = ev.scene as SceneState;
      const list = [...s.scenes];
      list[sc.index] = { ...(list[sc.index] ?? {}), ...sc };
      n.scenes = list;
      break;
    }
    case "artifact":
      if (ev.kind === "review_still") n.reviewStills = { ...s.reviewStills, [ev.scene]: ev.url };
      break;
    case "job.done":
      n.status = "done";
      n.outputs = ev.outputs;
      n.progress = 1;
      break;
    case "job.failed":
      n.status = ev.recoverable ? "done" : "failed";
      n.error = ev.error;
      break;
    case "job.cancelled":
      n.status = "cancelled";
      break;
  }
  return n;
}

export function useJobStream(id: string | null, epoch = 0) {
  const [state, dispatch] = useReducer(reduce, initial);
  const lastSeq = useRef(0);
  lastSeq.current = state.lastSeq;

  useEffect(() => {
    if (!id) return;
    dispatch({ kind: "reset" });
    lastSeq.current = 0;
    let es: EventSource | null = null;
    let retry: ReturnType<typeof setTimeout> | null = null;
    let closed = false;
    const open = () => {
      es = new EventSource(`${API}/api/jobs/${id}/events?after=${lastSeq.current}`);
      es.onopen = () => dispatch({ kind: "conn", on: true });
      es.onmessage = (m) => {
        try {
          dispatch({ kind: "ev", ev: JSON.parse(m.data) });
        } catch {}
      };
      es.onerror = () => {
        dispatch({ kind: "conn", on: false });
        es?.close();
        if (!closed) retry = setTimeout(open, 2000);
      };
    };
    open();
    return () => {
      closed = true;
      es?.close();
      if (retry) clearTimeout(retry);
    };
  }, [id, epoch]);

  return state;
}
