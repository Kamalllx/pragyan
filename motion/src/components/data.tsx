import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath} from '@remotion/paths';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, CountUp, DrawLine, EASE, Reveal, SPRING, useActiveIndex, useCues} from '../motion';
import {Body, Glass, Heading, Stage} from './ui';
import {useLabel} from '../i18n';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

/* ---------------------------------- STATS --------------------------------- */
export const StatsScene: React.FC<{v: V<'stats'>}> = ({v}) => {
	const theme = useTheme();
	const stats = v.stats.slice(0, 4);
	const cues = useCues(stats.length, {first: 22});
	const active = useActiveIndex(cues);
	const big = stats.length <= 2 ? 190 : stats.length === 3 ? 140 : 112;
	return (
		<Stage>
			{v.heading ? <Heading text={v.heading} size={64} /> : null}
			<div style={{display: 'flex', gap: 60, flex: 1, alignItems: 'center', marginTop: v.heading ? 20 : 0, height: v.heading ? 'auto' : '100%'}}>
				{stats.map((s, i) => (
					<div key={i} style={{flex: 1, opacity: active > i ? 0.55 : 1}}>
						<Reveal start={cues[i]} y={40} blur={18}>
							<div
								style={{
									fontFamily: theme.display,
									fontWeight: theme.displayWeight,
									fontSize: big,
									letterSpacing: '-0.05em',
									lineHeight: 1,
									color: i === active ? theme.accent : theme.text,
								}}
							>
								<CountUp value={s.value} start={cues[i]} prefix={s.prefix} decimals={s.decimals} duration={40} />
								{s.suffix ? <span style={{fontSize: '0.42em', letterSpacing: '-0.01em', marginLeft: '0.08em', color: theme.muted}}>{s.suffix.trim()}</span> : null}
							</div>
							<DrawLine start={cues[i] + 8} color={alpha(theme.accent, 0.6)} length={120} thickness={2} style={{margin: '30px 0 22px'}} />
							<Body size={32} muted style={{maxWidth: 440}}>
								{s.label}
							</Body>
						</Reveal>
					</div>
				))}
			</div>
		</Stage>
	);
};

/* ---------------------------------- CHART --------------------------------- */
export const ChartScene: React.FC<{v: V<'chart'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const n = Math.min(v.values.length, v.labels.length, 12);
	const values = v.values.slice(0, n);
	const labels = v.labels.slice(0, n);
	const max = Math.max(...values.map((x) => Math.abs(x)), 1) * 1.12;
	const W = 1500;
	const H = 500;
	const start = 26;
	const fmt = (x: number) => (Math.abs(x) >= 1000 ? x.toLocaleString('en-US', {maximumFractionDigits: 1}) : Number.isInteger(x) ? `${x}` : x.toFixed(1));
	const gridLines = [0.25, 0.5, 0.75, 1];

	const body =
		v.kind === 'line' ? (
			(() => {
				const pts = values.map((val, i) => [n > 1 ? (i / (n - 1)) * W : W / 2, H - (val / max) * H] as const);
				const d = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
				const t = interpolate(frame - start, [0, 60], [0, 1], {...clamp, easing: EASE.draw});
				const ev = evolvePath(t, d);
				const area = `${d} L${W},${H} L0,${H} Z`;
				return (
					<svg width={W} height={H + 60} style={{overflow: 'visible'}}>
						<defs>
							<linearGradient id="areaG" x1="0" x2="0" y1="0" y2="1">
								<stop offset="0%" stopColor={theme.accent} stopOpacity={0.35} />
								<stop offset="100%" stopColor={theme.accent} stopOpacity={0} />
							</linearGradient>
							<clipPath id="reveal">
								<rect x={0} y={-20} width={W * t} height={H + 40} />
							</clipPath>
						</defs>
						{gridLines.map((g) => (
							<line key={g} x1={0} x2={W} y1={H - g * H} y2={H - g * H} stroke={alpha(theme.text, 0.07)} />
						))}
						<path d={area} fill="url(#areaG)" clipPath="url(#reveal)" />
						<path d={d} fill="none" stroke={theme.accent} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round" strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />
						{pts.map(([x, y], i) => {
							const p = spring({frame: frame - start - (i / Math.max(1, n - 1)) * 60, fps, config: SPRING.bouncy});
							return (
								<g key={i} opacity={p}>
									<circle cx={x} cy={y} r={9 * p} fill={theme.bg} stroke={theme.accent} strokeWidth={3} />
									<text x={x} y={y - 26} textAnchor="middle" fill={theme.text} fontFamily={theme.mono} fontSize={24}>
										{fmt(values[i])}
									</text>
									<text x={x} y={H + 46} textAnchor="middle" fill={theme.muted} fontFamily={theme.body} fontSize={24}>
										{labels[i]}
									</text>
								</g>
							);
						})}
					</svg>
				);
			})()
		) : (
			<svg width={W} height={H + 60} style={{overflow: 'visible'}}>
				{gridLines.map((g) => (
					<line key={g} x1={0} x2={W} y1={H - g * H} y2={H - g * H} stroke={alpha(theme.text, 0.07)} />
				))}
				{values.map((val, i) => {
					const slot = W / n;
					const bw = Math.min(150, slot * 0.58);
					const x = i * slot + (slot - bw) / 2;
					const p = spring({frame: frame - start - i * 5, fps, config: SPRING.soft});
					const h = (Math.abs(val) / max) * H * p;
					const isMax = val === Math.max(...values);
					return (
						<g key={i}>
							<rect x={x} y={H - h} width={bw} height={h} rx={10} fill={isMax ? theme.accent : alpha(theme.text, 0.16)} />
							<text x={x + bw / 2} y={H - h - 18} textAnchor="middle" fill={isMax ? theme.accent : theme.text} fontFamily={theme.mono} fontSize={26} opacity={p}>
								{fmt(val * Math.min(1, p))}
							</text>
							<text x={x + bw / 2} y={H + 44} textAnchor="middle" fill={theme.muted} fontFamily={theme.body} fontSize={24}>
								{labels[i]}
							</text>
						</g>
					);
				})}
			</svg>
		);

	return (
		<Stage>
			{v.heading ? <Heading text={v.heading} size={62} eyebrow={v.unit ? `${label('unit')} · ${v.unit}` : undefined} /> : null}
			<Reveal start={14} y={30} style={{marginTop: 50, display: 'flex', justifyContent: 'center'}}>
				{body}
			</Reveal>
			{v.caption ? (
				<Reveal start={70} y={14} style={{marginTop: 26}}>
					<Body size={28} muted>
						{v.caption}
					</Body>
				</Reveal>
			) : null}
		</Stage>
	);
};

/* ------------------------------- COMPARISON ------------------------------- */
export const ComparisonScene: React.FC<{v: V<'comparison'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const L = v.left.points.slice(0, 5);
	const R = v.right.points.slice(0, 5);
	// Narration order: left title+points, then right title+points, then verdict.
	const total = 2 + (v.verdict ? 1 : 0);
	const cues = useCues(total, {first: 20});
	const divider = interpolate(frame, [8, 40], [0, 1], {...clamp, easing: EASE.draw});
	const side = (s: {title: string; points: string[]}, pts: string[], start: number, color: string, label: string) => (
		<div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 26}}>
			<Reveal start={start} y={20}>
				<div style={{fontFamily: theme.mono, fontSize: 22, letterSpacing: '0.22em', color, textTransform: 'uppercase'}}>{label}</div>
				<div
					style={{
						fontFamily: theme.display,
						fontWeight: theme.displayWeight,
						fontSize: 60,
						letterSpacing: theme.displayTracking,
						color: theme.text,
						marginTop: 12,
						lineHeight: 1.05,
					}}
				>
					{s.title}
				</div>
			</Reveal>
			{pts.map((p, i) => (
				<Reveal key={i} start={start + 10 + i * 8} y={16} x={-8}>
					<div style={{display: 'flex', gap: 20, alignItems: 'baseline'}}>
						<div style={{width: 10, height: 10, borderRadius: 10, background: color, flexShrink: 0, transform: 'translateY(-4px)'}} />
						<Body size={32}>{p}</Body>
					</div>
				</Reveal>
			))}
		</div>
	);
	return (
		<Stage>
			{v.heading ? <Heading text={v.heading} size={58} style={{marginBottom: 40}} /> : null}
			<div style={{display: 'flex', gap: 80, flex: 1, position: 'relative'}}>
				{side(v.left, L, cues[0], theme.accent2, 'A')}
				<div style={{width: 2, background: alpha(theme.text, 0.14), transform: `scaleY(${divider})`, transformOrigin: 'top'}} />
				{side(v.right, R, cues[1], theme.accent, 'B')}
			</div>
			{v.verdict ? (
				<Reveal start={cues[2]} y={24} style={{marginTop: 30}}>
					<Glass style={{padding: '22px 34px', display: 'flex', gap: 24, alignItems: 'center'}} glow={0.6}>
						<span style={{fontFamily: theme.mono, fontSize: 20, letterSpacing: '0.2em', color: theme.accent, textTransform: 'uppercase'}}>{label('verdict')}</span>
						<Body size={32}>{v.verdict}</Body>
					</Glass>
				</Reveal>
			) : null}
		</Stage>
	);
};
