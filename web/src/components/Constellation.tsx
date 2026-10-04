"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState } from "react";
import type { AgentNode } from "@/lib/api";

const SIZE = 720;
const C = SIZE / 2;
const RINGS = [0, 150, 245, 318];

type Placed = AgentNode & { depth: number; angle: number; x: number; y: number; px: number; py: number };

/** Sunburst-style allocation: each branch gets angular room proportional to its subtree. */
function layout(agents: Record<string, AgentNode>, order: string[]): Placed[] {
  const kids: Record<string, string[]> = {};
  const roots: string[] = [];
  for (const id of order) {
    const a = agents[id];
    if (!a) continue;
    const p = a.parent && agents[a.parent] ? a.parent : null;
    if (id === "orchestrator") continue;
    if (!p || p === "orchestrator") roots.push(id);
    else (kids[p] ??= []).push(id);
  }
  const weight = (id: string): number => 1 + (kids[id] ?? []).reduce((s, k) => s + weight(k) * 0.9, 0);
  const out: Placed[] = [];
  const orch = agents["orchestrator"];
  if (orch) out.push({ ...orch, depth: 0, angle: 0, x: C, y: C, px: C, py: C });

  const place = (ids: string[], from: number, to: number, depth: number, parent?: Placed) => {
    const total = ids.reduce((s, id) => s + weight(id), 0) || 1;
    let a0 = from;
    for (const id of ids) {
      const span = ((to - from) * weight(id)) / total;
      const ang = a0 + span / 2;
      const r = RINGS[Math.min(depth, RINGS.length - 1)];
      const node: Placed = {
        ...agents[id],
        depth,
        angle: ang,
        x: C + r * Math.cos(ang),
        y: C + r * Math.sin(ang),
        px: parent ? parent.x : C,
        py: parent ? parent.y : C,
      };
      out.push(node);
      if (kids[id]?.length) place(kids[id], a0 + span * 0.04, a0 + span * 0.96, Math.min(depth + 1, 3), node);
      a0 += span;
    }
  };
  place(roots, -Math.PI / 2, (3 * Math.PI) / 2, 1);
  return out;
}

const color = (s: AgentNode["status"]) => (s === "working" ? "var(--color-earth)" : s === "error" ? "var(--color-err)" : "var(--color-moon)");

export function Constellation({
  agents,
  order,
  selected,
  onSelect,
  live,
}: {
  agents: Record<string, AgentNode>;
  order: string[];
  selected: string | null;
  onSelect: (id: string | null) => void;
  live: boolean;
}) {
  const nodes = useMemo(() => layout(agents, order), [agents, order]);
  const [hover, setHover] = useState<string | null>(null);
  const focus = nodes.find((n) => n.id === (hover ?? selected));
  const working = nodes.filter((n) => n.status === "working" && n.depth > 0).length;

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="block h-auto w-full" role="img" aria-label={`Agent constellation: ${nodes.length} agents, ${working} working`}>
        <defs>
          <radialGradient id="core-glow">
            <stop offset="0%" stopColor="var(--color-saffron)" stopOpacity="0.35" />
            <stop offset="100%" stopColor="var(--color-saffron)" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* orbits */}
        {RINGS.slice(1).map((r, i) => (
          <circle key={r} cx={C} cy={C} r={r} fill="none" stroke="var(--color-regolith)" strokeOpacity={0.7 - i * 0.15} strokeDasharray={i === 2 ? "2 6" : undefined} />
        ))}
        {/* instrument ticks on the outer bezel, slowly turning while live */}
        <g className={live ? "origin-center animate-[spin_120s_linear_infinite]" : ""} style={{ transformOrigin: `${C}px ${C}px` }}>
          {Array.from({ length: 72 }, (_, i) => {
            const a = (i / 72) * Math.PI * 2;
            const r1 = 346;
            const r2 = i % 6 === 0 ? 336 : 341;
            return (
              <line
                key={i}
                x1={C + r1 * Math.cos(a)}
                y1={C + r1 * Math.sin(a)}
                x2={C + r2 * Math.cos(a)}
                y2={C + r2 * Math.sin(a)}
                stroke="var(--color-regolith-2)"
                strokeWidth={i % 6 === 0 ? 1.4 : 0.8}
              />
            );
          })}
        </g>

        {/* links */}
        {nodes
          .filter((n) => n.depth > 0)
          .map((n) => {
            const mx = (n.px + n.x) / 2 + (C - (n.px + n.x) / 2) * 0.18;
            const my = (n.py + n.y) / 2 + (C - (n.py + n.y) / 2) * 0.18;
            return (
              <motion.path
                key={`l-${n.id}`}
                d={`M${n.px},${n.py} Q${mx},${my} ${n.x},${n.y}`}
                fill="none"
                stroke={n.status === "working" ? "var(--color-earth)" : "var(--color-regolith-2)"}
                strokeOpacity={n.status === "working" ? 0.7 : 0.55}
                strokeWidth={n.status === "working" ? 1.4 : 1}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              />
            );
          })}

        {/* core */}
        <circle cx={C} cy={C} r={70} fill="url(#core-glow)" />
        <g>
          <circle cx={C} cy={C} r={30} fill="var(--color-basalt-2)" stroke="var(--color-saffron)" strokeOpacity={0.7} strokeWidth={1.5} />
          <circle cx={C} cy={C} r={20} fill="none" stroke="var(--color-saffron)" strokeOpacity={0.5} strokeDasharray="60 22" className={live ? "animate-[spin_6s_linear_infinite]" : ""} style={{ transformOrigin: `${C}px ${C}px` }} />
          <circle cx={C} cy={C} r={7} fill="var(--color-saffron)" />
        </g>

        {/* agents */}
        <AnimatePresence>
          {nodes
            .filter((n) => n.depth > 0)
            .map((n) => {
              const r = n.depth === 1 ? 9 : n.depth === 2 ? 6.5 : 5;
              const isSel = selected === n.id || hover === n.id;
              const showLabel = n.depth === 1 || isSel || n.status === "working";
              const outward = n.x >= C - 2;
              return (
                <motion.g
                  key={n.id}
                  initial={{ x: n.px - n.x, y: n.py - n.y, opacity: 0, scale: 0.2 }}
                  animate={{ x: 0, y: 0, opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 140, damping: 18 }}
                  style={{ cursor: "pointer" }}
                  onMouseEnter={() => setHover(n.id)}
                  onMouseLeave={() => setHover(null)}
                  onClick={() => onSelect(selected === n.id ? null : n.id)}
                  tabIndex={0}
                  role="button"
                  aria-label={`${n.label}: ${n.status}`}
                  onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect(selected === n.id ? null : n.id)}
                >
                  {n.status === "working" && (
                    <circle cx={n.x} cy={n.y} r={r} fill="none" stroke="var(--color-earth)" style={{ transformOrigin: `${n.x}px ${n.y}px`, animation: "pulse-ring 1.8s ease-out infinite" }} />
                  )}
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={r + (isSel ? 3 : 0)}
                    fill={n.status === "done" ? "var(--color-basalt-3)" : color(n.status)}
                    stroke={color(n.status)}
                    strokeWidth={n.status === "done" ? 1.5 : 0}
                  />
                  {n.status === "done" && <circle cx={n.x} cy={n.y} r={r * 0.38} fill="var(--color-saffron)" />}
                  {showLabel && (
                    <text
                      x={n.x + (outward ? r + 8 : -(r + 8))}
                      y={n.y + 4}
                      textAnchor={outward ? "start" : "end"}
                      fontSize={n.depth === 1 ? 13 : 11.5}
                      fill={n.status === "working" ? "var(--color-moon)" : "var(--color-ash)"}
                      style={{ fontFamily: "var(--font-sans)", paintOrder: "stroke", stroke: "var(--color-basalt)", strokeWidth: 4 }}
                    >
                      {n.label}
                    </text>
                  )}
                </motion.g>
              );
            })}
        </AnimatePresence>
      </svg>

      {/* readout */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center">
        <AnimatePresence mode="wait">
          {focus && focus.depth > 0 ? (
            <motion.div
              key={focus.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="max-w-md rounded-xl border border-regolith bg-basalt-2/95 px-4 py-3 text-sm shadow-xl backdrop-blur"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-moon">{focus.label}</span>
                <span className={`text-xs ${focus.status === "working" ? "text-earth" : focus.status === "error" ? "text-err" : "text-dust"}`}>
                  {focus.status === "working" ? "working" : focus.status === "error" ? "error" : `${focus.seconds ?? 0}s`}
                </span>
                {focus.tokens > 0 && <span className="text-xs text-dust">{focus.tokens.toLocaleString()} tokens</span>}
              </div>
              {(focus.summary || focus.detail) && <p className="mt-1 text-[13px] leading-snug text-ash">{focus.summary || focus.detail}</p>}
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}
