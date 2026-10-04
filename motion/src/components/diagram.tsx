import React, {useMemo} from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath, getLength, getPointAtLength} from '@remotion/paths';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, EASE, SPRING, useActiveIndex, useCues} from '../motion';
import {Heading, Stage} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

type Laid = {id: string; label: string; sub?: string; x: number; y: number; w: number; h: number; rank: number};

/** Layered (Sugiyama-lite) layout: longest-path ranks + one barycentre pass. */
const layout = (v: V<'diagram'>, W: number, H: number) => {
	const nodes = v.nodes.slice(0, 12);
	const ids = new Set(nodes.map((n) => n.id));
	const edges = v.edges.filter((e) => ids.has(e.from) && ids.has(e.to) && e.from !== e.to).slice(0, 20);
	const rank: Record<string, number> = {};
	nodes.forEach((n) => (rank[n.id] = 0));
	// Bellman-style relaxation; bounded iterations make cycles harmless.
	for (let it = 0; it < nodes.length; it++) {
		let changed = false;
		for (const e of edges) {
			if (rank[e.to] < rank[e.from] + 1 && rank[e.from] + 1 < nodes.length) {
				rank[e.to] = rank[e.from] + 1;
				changed = true;
			}
		}
		if (!changed) break;
	}
	const maxRank = Math.max(0, ...Object.values(rank));
	const layers: string[][] = Array.from({length: maxRank + 1}, () => []);
	nodes.forEach((n) => layers[rank[n.id]].push(n.id));
	// Barycentre ordering to reduce crossings.
	const order: Record<string, number> = {};
	layers[0].forEach((id, i) => (order[id] = i));
	for (let r = 1; r < layers.length; r++) {
		const bc = (id: string) => {
			const preds = edges.filter((e) => e.to === id && rank[e.from] < r).map((e) => order[e.from] ?? 0);
			return preds.length ? preds.reduce((a, b) => a + b, 0) / preds.length : 0;
		};
		layers[r].sort((a, b) => bc(a) - bc(b));
		layers[r].forEach((id, i) => (order[id] = i));
	}
	const lr = (v.direction ?? (layers.length > 3 ? 'LR' : layers.length <= 1 ? 'LR' : 'TB')) === 'LR';
	const maxPer = Math.max(...layers.map((l) => l.length));
	const w = lr ? Math.min(330, (W / layers.length) * 0.72) : Math.min(330, (W / maxPer) * 0.78);
	const h = lr ? Math.min(124, (H / maxPer) * 0.66) : Math.min(124, (H / layers.length) * 0.56);
	const laid: Record<string, Laid> = {};
	layers.forEach((layer, r) => {
		layer.forEach((id, i) => {
			const n = nodes.find((x) => x.id === id)!;
			const along = (r + 0.5) / layers.length;
			const across = (i + 0.5) / layer.length;
			const x = lr ? along * W : across * W;
			const y = lr ? across * H : along * H;
			laid[id] = {...n, x, y, w, h, rank: r};
		});
	});
	return {laid, edges, lr};
};

export const DiagramScene: React.FC<{v: V<'diagram'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const W = 1620;
	const H = v.heading ? 560 : 700;
	const {laid, edges, lr} = useMemo(() => layout(v, W, H), [v, H]);
	const order = v.nodes.slice(0, 12).map((n) => n.id).filter((id) => laid[id]);
	const cues = useCues(order.length, {first: v.heading ? 24 : 12, spread: 0.7});
	const active = useActiveIndex(cues);
	const cueOf = (id: string) => cues[order.indexOf(id)] ?? 0;

	const paths = edges.map((e) => {
		const a = laid[e.from];
		const b = laid[e.to];
		let d: string;
		if (lr) {
			const x1 = a.x + a.w / 2;
			const x2 = b.x - b.w / 2;
			const mx = (x1 + x2) / 2;
			d = x2 > x1 ? `M${x1},${a.y} C${mx},${a.y} ${mx},${b.y} ${x2},${b.y}` : `M${a.x},${a.y + a.h / 2} C${a.x},${a.y + 160} ${b.x},${b.y + 160} ${b.x},${b.y + b.h / 2}`;
		} else {
			const y1 = a.y + a.h / 2;
			const y2 = b.y - b.h / 2;
			const my = (y1 + y2) / 2;
			d = y2 > y1 ? `M${a.x},${y1} C${a.x},${my} ${b.x},${my} ${b.x},${y2}` : `M${a.x + a.w / 2},${a.y} C${a.x + 200},${a.y} ${b.x + 200},${b.y} ${b.x + b.w / 2},${b.y}`;
		}
		const start = Math.max(cueOf(e.from), cueOf(e.to)) + 4;
		return {e, d, start, len: getLength(d)};
	});

	return (
		<Stage drift={0.7}>
			{v.heading ? <Heading text={v.heading} size={60} /> : null}
			<div style={{position: 'relative', width: W, height: H, marginTop: v.heading ? 30 : 0}}>
				<svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
					<defs>
						<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
							<path d="M 0 0 L 10 5 L 0 10 z" fill={alpha(theme.accent, 0.9)} />
						</marker>
					</defs>
					{paths.map(({e, d, start, len}, i) => {
						const t = interpolate(frame - start, [0, 26], [0, 1], {...clamp, easing: EASE.draw});
						const ev = evolvePath(t, d);
						// A pulse that travels the edge forever after it is drawn: data in motion.
						const cycle = 70;
						const k = ((frame - start - 26) % cycle) / cycle;
						const pt = frame - start > 26 ? getPointAtLength(d, len * k) : null;
						const mid = getPointAtLength(d, len / 2) ?? {x: 0, y: 0};
						return (
							<g key={i}>
								<path d={d} fill="none" stroke={alpha(theme.text, 0.22)} strokeWidth={2} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} markerEnd={t > 0.95 ? 'url(#arrow)' : undefined} />
								{pt ? <circle cx={pt.x} cy={pt.y} r={5} fill={theme.accent} opacity={Math.sin(k * Math.PI)} style={{filter: `drop-shadow(0 0 8px ${theme.accent})`}} /> : null}
								{e.label && t > 0.6 ? (
									<g opacity={interpolate(t, [0.6, 1], [0, 1], clamp)}>
										<rect x={mid.x - e.label.length * 7 - 14} y={mid.y - 19} width={e.label.length * 14 + 28} height={38} rx={19} fill={theme.bg} stroke={theme.border} />
										<text x={mid.x} y={mid.y + 7} textAnchor="middle" fontFamily={theme.mono} fontSize={20} fill={theme.muted}>
											{e.label}
										</text>
									</g>
								) : null}
							</g>
						);
					})}
				</svg>
				{order.map((id, i) => {
					const n = laid[id];
					const p = spring({frame: frame - cues[i], fps, config: SPRING.snappy});
					const on = i === active;
					return (
						<div
							key={id}
							style={{
								position: 'absolute',
								left: n.x - n.w / 2,
								top: n.y - n.h / 2,
								width: n.w,
								height: n.h,
								borderRadius: 22,
								display: 'flex',
								flexDirection: 'column',
								alignItems: 'center',
								justifyContent: 'center',
								textAlign: 'center',
								padding: '0 18px',
								background: on ? alpha(theme.accent, theme.dark ? 0.14 : 0.12) : theme.dark ? alpha('#ffffff', 0.05) : alpha('#ffffff', 0.65),
								border: `1.5px solid ${on ? theme.accent : theme.border}`,
								boxShadow: on ? `0 0 60px ${alpha(theme.accent, 0.35)}` : `0 20px 50px -25px rgba(0,0,0,${theme.dark ? 0.7 : 0.25})`,
								transform: `scale(${0.6 + 0.4 * p})`,
								opacity: interpolate(p, [0, 0.5], [0, 1], clamp),
							}}
						>
							<div style={{fontFamily: theme.display, fontWeight: Math.min(650, theme.displayWeight + 40), fontSize: n.label.length > 18 ? 26 : 32, color: theme.text, lineHeight: 1.1, letterSpacing: '-0.015em'}}>
								{n.label}
							</div>
							{n.sub ? <div style={{fontFamily: theme.body, fontSize: 20, color: theme.muted, marginTop: 6, lineHeight: 1.2}}>{n.sub}</div> : null}
						</div>
					);
				})}
			</div>
		</Stage>
	);
};
