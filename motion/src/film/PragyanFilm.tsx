/**
 * "Pragyan" — the hand-directed launch film.
 * Built the way Claude Code directs motion: storyboard → bespoke shots on top of the
 * shared motion library → render → inspect stills → iterate.
 */
import React from 'react';
import {AbsoluteFill, Html5Audio, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {evolvePath} from '@remotion/paths';
import narration from './narration.json';
import type {SceneSpec, Segment} from '../spec';
import {alpha, getTheme, ThemeContext, useTheme} from '../theme';
import {Background, Grain, Vignette} from '../fx/Background';
import {SceneRenderer} from '../SceneRenderer';
import {presentationFor} from '../transitions';
import {Captions} from '../Captions';
import {clamp, EASE, SceneContext, SPRING, Words} from '../motion';

const FPS = 30;
const T = 16;
const LEAD = 10;
type Key = keyof typeof narration;

const seg = (key: Key): Segment[] => {
	const n = narration[key];
	const f = (s: number) => LEAD + Math.round(s * FPS);
	return [{text: n.text, start: f(0), end: f(n.seconds), words: n.words.map((w) => ({w: w.w, s: f(w.s), e: f(w.e)}))}];
};

const dur = (key: Key, pad = 1.3) => LEAD + Math.round((narration[key].seconds + pad) * FPS) + T;

type Shot = {key: Key; scene: SceneSpec; bespoke?: React.FC};

const mk = (key: Key, visual: SceneSpec['visual'], extraSegs: Segment[] = [], pad?: number, transition: SceneSpec['transition'] = 'dip'): SceneSpec => ({
	id: key,
	durationInFrames: dur(key, pad),
	segments: [...seg(key), ...extraSegs],
	visual,
	transition,
	chapter: '',
});

/* ------------------------------------------------------------------ */
/* Shot A — the question                                                */
/* ------------------------------------------------------------------ */
const TypedPrompt: React.FC = () => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const q = 'Why is the sky blue but sunsets are red?';
	const chars = Math.floor(interpolate(frame, [18, 78], [0, q.length], clamp));
	const card = spring({frame: frame - 2, fps, config: SPRING.heavy});
	const press = spring({frame: frame - 96, fps, config: SPRING.snappy});
	const pressed = frame >= 96 && frame < 104;
	const lift = interpolate(frame, [104, 140], [0, 1], {...clamp, easing: EASE.in});
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
			<div
				style={{
					width: 1180,
					borderRadius: 34,
					background: alpha('#1b1d21', 0.82),
					border: `1px solid ${alpha(theme.text, 0.12)}`,
					boxShadow: `0 50px 140px -40px rgba(0,0,0,0.9), 0 0 ${80 * press}px ${alpha(theme.accent, 0.18 * press)}`,
					transform: `translateY(${(1 - card) * 60 - lift * 40}px) scale(${0.96 + 0.04 * card - lift * 0.06})`,
					opacity: card * (1 - lift),
					filter: `blur(${lift * 14}px)`,
				}}
			>
				<div style={{padding: '46px 56px 30px', fontFamily: theme.body, fontSize: 52, color: theme.text, minHeight: 170, letterSpacing: '-0.01em'}}>
					{q.slice(0, chars)}
					<span style={{display: 'inline-block', width: 4, height: 54, marginLeft: 6, verticalAlign: 'middle', background: theme.accent, opacity: Math.floor(frame / 15) % 2 === 0 || chars < q.length ? 1 : 0}} />
				</div>
				<div style={{display: 'flex', alignItems: 'center', gap: 18, padding: '22px 34px', borderTop: `1px solid ${alpha(theme.text, 0.1)}`}}>
					{['Attach', '1 min', 'Style & voice'].map((t) => (
						<span key={t} style={{fontFamily: theme.body, fontSize: 24, color: theme.muted, padding: '8px 18px', borderRadius: 999, border: `1px solid ${alpha(theme.text, 0.1)}`}}>
							{t}
						</span>
					))}
					<span
						style={{
							marginLeft: 'auto',
							fontFamily: theme.body,
							fontWeight: 600,
							fontSize: 26,
							color: '#141518',
							background: theme.accent,
							padding: '16px 34px',
							borderRadius: 999,
							transform: `scale(${pressed ? 0.94 : 1})`,
						}}
					>
						Make the video
					</span>
				</div>
			</div>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* Shot B — the agent constellation (2.5D: slow dolly + parallax rings) */
/* ------------------------------------------------------------------ */
const AGENTS: {label: string; ring: number; a: number; at: number; parent?: number}[] = [
	{label: 'Intent Analyst', ring: 1, a: -62, at: 14},
	{label: 'Steering Curator', ring: 1, a: -22, at: 24},
	{label: 'Explainer', ring: 1, a: 18, at: 34},
	{label: 'Solver', ring: 1, a: 58, at: 42},
	{label: 'Creative Director', ring: 1, a: 180, at: 54},
	{label: 'Visual Critic', ring: 1, a: -142, at: 112},
	{label: 'Renderer', ring: 1, a: -102, at: 124},
	{label: 'Verifier', ring: 2, a: 70, at: 60, parent: 3},
	{label: 'Designer', ring: 2, a: 152, at: 66, parent: 4},
	{label: 'Designer', ring: 2, a: 168, at: 72, parent: 4},
	{label: 'Designer', ring: 2, a: 192, at: 78, parent: 4},
	{label: 'Designer', ring: 2, a: 208, at: 84, parent: 4},
	{label: 'Manim Animator', ring: 2, a: 124, at: 92, parent: 4},
	{label: 'Error Resolver', ring: 3, a: 112, at: 104, parent: 12},
];
const RING = [0, 270, 400, 480];

const Constellation: React.FC = () => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const W = 1920;
	const H = 1080;
	const cx = W / 2;
	const cy = H / 2 - 20;
	const pos = (r: number, deg: number) => {
		const a = (deg * Math.PI) / 180;
		return {x: cx + RING[r] * Math.cos(a) * 1.25, y: cy + RING[r] * Math.sin(a) * 0.62};
	};
	const dolly = interpolate(frame, [0, 200], [0.9, 1.06], {...clamp, easing: EASE.inOut});
	const tilt = interpolate(frame, [0, 200], [14, 4], clamp);
	const core = spring({frame, fps, config: SPRING.heavy});
	return (
		<AbsoluteFill style={{perspective: 1600}}>
			<AbsoluteFill style={{transform: `scale(${dolly}) rotateX(${tilt}deg)`, transformOrigin: '50% 50%'}}>
				<svg width={W} height={H}>
					{[1, 2, 3].map((r) => (
						<ellipse
							key={r}
							cx={cx}
							cy={cy}
							rx={RING[r] * 1.25}
							ry={RING[r] * 0.62}
							fill="none"
							stroke={alpha(theme.text, 0.12 - r * 0.02)}
							strokeDasharray={r === 3 ? '3 9' : undefined}
							strokeWidth={1.4}
							opacity={interpolate(frame, [r * 4, r * 4 + 20], [0, 1], clamp)}
						/>
					))}
					{AGENTS.map((g, i) => {
						const p = pos(g.ring, g.a + frame * 0.03 * (g.ring === 1 ? 1 : -0.6));
						const parent = g.parent !== undefined ? AGENTS[g.parent] : null;
						const pp = parent ? pos(parent.ring, parent.a + frame * 0.03 * (parent.ring === 1 ? 1 : -0.6)) : {x: cx, y: cy};
						const d = `M${pp.x},${pp.y} Q${(pp.x + p.x) / 2 + (cx - (pp.x + p.x) / 2) * 0.2},${(pp.y + p.y) / 2 + (cy - (pp.y + p.y) / 2) * 0.2} ${p.x},${p.y}`;
						const t = interpolate(frame - g.at, [0, 16], [0, 1], {...clamp, easing: EASE.draw});
						const ev = evolvePath(t, d);
						const s = spring({frame: frame - g.at - 8, fps, config: SPRING.bouncy});
						const working = frame - g.at < 60 && frame >= g.at;
						const pulse = ((frame - g.at) % 40) / 40;
						return (
							<g key={i}>
								<path d={d} fill="none" stroke={working ? theme.accent2 : alpha(theme.text, 0.25)} strokeWidth={working ? 2 : 1.3} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />
								{working && s > 0.5 && <circle cx={p.x} cy={p.y} r={10 + pulse * 26} fill="none" stroke={theme.accent2} opacity={1 - pulse} />}
								<circle cx={p.x} cy={p.y} r={(g.ring === 1 ? 11 : 8) * s} fill={working ? theme.accent2 : theme.bg2} stroke={working ? theme.accent2 : theme.text} strokeWidth={2} />
								{!working && s > 0.9 && <circle cx={p.x} cy={p.y} r={4} fill={theme.accent} />}
								<text
									x={p.x + (p.x >= cx ? 22 : -22)}
									y={p.y + 8}
									textAnchor={p.x >= cx ? 'start' : 'end'}
									fontFamily={theme.body}
									fontSize={g.ring === 1 ? 27 : 22}
									fill={working ? theme.text : alpha(theme.text, 0.6)}
									opacity={s}
								>
									{g.label}
								</text>
							</g>
						);
					})}
					<circle cx={cx} cy={cy} r={150} fill={`url(#coreGlow)`} opacity={core} />
					<defs>
						<radialGradient id="coreGlow">
							<stop offset="0%" stopColor={theme.accent} stopOpacity={0.4} />
							<stop offset="100%" stopColor={theme.accent} stopOpacity={0} />
						</radialGradient>
					</defs>
					<g transform={`translate(${cx},${cy}) scale(${core})`}>
						<circle r={58} fill={theme.bg2} stroke={theme.accent} strokeWidth={2.5} />
						<circle r={40} fill="none" stroke={alpha(theme.accent, 0.6)} strokeWidth={2} strokeDasharray="120 40" transform={`rotate(${frame * 3})`} />
						<circle r={14} fill={theme.accent} />
					</g>
				</svg>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* Shot F — render → inspect → fix                                      */
/* ------------------------------------------------------------------ */
const Loop: React.FC = () => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const cx = 960;
	const cy = 500;
	const R = 300;
	const nodes = ['Render', 'Inspect', 'Fix'];
	const ang = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / 3;
	const ring = interpolate(frame, [4, 40], [0, 1], {...clamp, easing: EASE.draw});
	const orbit = (frame / 70) * Math.PI * 2 - Math.PI / 2;
	const frameIn = spring({frame: frame - 20, fps, config: SPRING.soft});
	const flagged = frame > 62 && frame < 118;
	const fixed = frame >= 118;
	const fixP = spring({frame: frame - 118, fps, config: SPRING.bouncy});
	const circ = 2 * Math.PI * R;
	return (
		<AbsoluteFill>
			<svg width={1920} height={1080} style={{position: 'absolute'}}>
				<circle cx={cx} cy={cy} r={R} fill="none" stroke={alpha(theme.text, 0.14)} strokeWidth={2} strokeDasharray={circ} strokeDashoffset={circ * (1 - ring)} transform={`rotate(-90 ${cx} ${cy})`} />
				<circle cx={cx + R * Math.cos(orbit)} cy={cy + R * Math.sin(orbit)} r={9} fill={theme.accent} opacity={ring} style={{filter: `drop-shadow(0 0 12px ${theme.accent})`}} />
				{nodes.map((n, i) => {
					const p = spring({frame: frame - 10 - i * 8, fps, config: SPRING.snappy});
					const x = cx + R * Math.cos(ang(i));
					const y = cy + R * Math.sin(ang(i));
					return (
						<g key={n} opacity={p}>
							<circle cx={x} cy={y} r={58 * p} fill={theme.bg2} stroke={alpha(theme.text, 0.25)} strokeWidth={2} />
							<text x={x} y={y + 10} textAnchor="middle" fontFamily={theme.display} fontWeight={600} fontSize={28} fill={theme.text}>
								{n}
							</text>
						</g>
					);
				})}
			</svg>
			{/* the frame under review */}
			<div
				style={{
					position: 'absolute',
					left: cx - 210,
					top: cy - 120,
					width: 420,
					height: 236,
					borderRadius: 18,
					background: theme.bg2,
					border: `2px solid ${fixed ? theme.good : flagged ? theme.bad : alpha(theme.text, 0.15)}`,
					boxShadow: fixed ? `0 0 ${50 * fixP}px ${alpha(theme.good, 0.35)}` : 'none',
					transform: `scale(${0.8 + 0.2 * frameIn})`,
					opacity: frameIn,
					padding: 26,
					overflow: 'hidden',
				}}
			>
				<div style={{height: 22, width: fixed ? 250 : 470, background: alpha(theme.text, 0.75), borderRadius: 6}} />
				<div style={{height: 12, width: 300, background: alpha(theme.text, 0.25), borderRadius: 6, marginTop: 22}} />
				<div style={{height: 12, width: 250, background: alpha(theme.text, 0.25), borderRadius: 6, marginTop: 12}} />
				<div style={{height: 12, width: 280, background: alpha(theme.text, 0.25), borderRadius: 6, marginTop: 12}} />
				{flagged && (
					<div style={{position: 'absolute', right: 10, top: 14, padding: '6px 12px', borderRadius: 8, background: alpha(theme.bad, 0.18), color: theme.bad, fontFamily: theme.mono, fontSize: 17}}>
						text cut off
					</div>
				)}
				{fixed && (
					<div style={{position: 'absolute', right: 16, bottom: 16, width: 46, height: 46, borderRadius: 46, background: theme.good, display: 'grid', placeItems: 'center', transform: `scale(${fixP})`}}>
						<svg width={26} height={26} viewBox="0 0 26 26">
							<path d="M5 13.5 L10.5 19 L21 7" fill="none" stroke={theme.bg} strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round" />
						</svg>
					</div>
				)}
			</div>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* Shot H — the mark                                                     */
/* ------------------------------------------------------------------ */
const Finale: React.FC = () => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const rings = [190, 130];
	const dot = spring({frame: frame - 26, fps, config: SPRING.bouncy});
	const tag = interpolate(frame, [60, 84], [0, 1], {...clamp, easing: EASE.out});
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
			<div style={{display: 'flex', alignItems: 'center', gap: 70, transform: `translateY(-40px)`}}>
				<svg width={420} height={420} viewBox="-210 -210 420 420">
					{rings.map((r, i) => {
						const c = 2 * Math.PI * r;
						const t = interpolate(frame - i * 6, [0, 44], [0, 1], {...clamp, easing: EASE.draw});
						return (
							<circle
								key={r}
								r={r}
								fill="none"
								stroke={i === 0 ? alpha(theme.text, 0.45) : theme.accent}
								strokeWidth={i === 0 ? 4 : 5}
								strokeDasharray={i === 1 ? `${c * 0.74} ${c * 0.26}` : c}
								strokeDashoffset={c * (1 - t)}
								transform={`rotate(${-90 + frame * (i === 1 ? 1.2 : 0)})`}
							/>
						);
					})}
					<circle r={54 * dot} fill={theme.accent} />
					<circle cx={190 * Math.cos(frame / 30)} cy={190 * Math.sin(frame / 30)} r={14 * dot} fill={theme.text} />
				</svg>
				<div>
					<div style={{fontFamily: theme.display, fontWeight: 600, fontSize: 210, letterSpacing: '-0.05em', color: theme.text, lineHeight: 0.9}}>
						<Words text="Pragyan" start={14} stagger={0} config={SPRING.soft} />
					</div>
					<div style={{fontFamily: theme.body, fontSize: 40, color: theme.muted, marginTop: 30, opacity: tag, transform: `translateY(${(1 - tag) * 14}px)`}}>
						Ask anything. Watch it explained.
					</div>
					<div style={{fontFamily: theme.mono, fontSize: 22, color: alpha(theme.accent, 0.9), marginTop: 22, opacity: interpolate(frame, [84, 104], [0, 1], clamp), letterSpacing: '0.04em'}}>
						local · agentic · open models
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* Assembly                                                             */
/* ------------------------------------------------------------------ */
const SHOTS: Shot[] = [
	{key: 'open', scene: mk('open', {type: 'title', title: ''}, [], 1.5), bespoke: TypedPrompt},
	{key: 'team', scene: mk('team', {type: 'title', title: ''}, [], 1.4, 'zoom'), bespoke: Constellation},
	{
		key: 'think',
		scene: {
			...mk('think', {type: 'kinetic', lines: ['It understands.', 'It solves.', 'It checks itself.'], emphasis: ['checks']}, [], 1.2, 'rise'),
			// one cue per sentence of the line
			segments: (() => {
				const s = seg('think')[0];
				const w = s.words!;
				const at = (i: number) => w[Math.min(i, w.length - 1)].s;
				return [{...s, start: s.start, end: s.start}, {...s, start: at(0), end: at(2)}, {...s, start: at(2), end: at(4)}, {...s, start: at(4), end: s.end}];
			})(),
		},
	},
	{
		key: 'board',
		scene: mk(
			'board',
			{
				type: 'cards3d',
				heading: 'Storyboarded, scene by scene',
				cards: [
					{title: 'The hook', body: 'A question that makes you lean in.'},
					{title: 'The mechanism', body: 'Cause and effect, drawn as a flow.'},
					{title: 'The maths', body: 'Every step derived, never skipped.'},
				],
			},
			[],
			1.4,
			'slide',
		),
	},
	{
		key: 'maths',
		scene: mk(
			'maths',
			{
				type: 'equation',
				steps: [
					{latex: 'I \\propto \\frac{1}{\\lambda^{4}}', note: 'Rayleigh scattering'},
					{latex: '\\frac{I_{450}}{I_{700}} = \\left(\\frac{700}{450}\\right)^{4}', note: 'blue against red'},
					{latex: '\\approx 5.85', note: 'so the sky is blue'},
				],
			},
			[],
			2.2,
			'zoom',
		),
	},
	{key: 'loop', scene: mk('loop', {type: 'title', title: ''}, [], 1.5, 'dip'), bespoke: Loop},
	{
		key: 'local',
		scene: mk(
			'local',
			{
				type: 'stats',
				stats: [
					{value: 0, label: 'cloud APIs or keys'},
					{value: 9.7, suffix: 'B', label: 'parameter model, on your GPU', decimals: 1},
					{value: 19, label: 'cinematic visual types'},
				],
			},
			[],
			1.4,
			'push',
		),
	},
	{key: 'end', scene: mk('end', {type: 'title', title: ''}, [], 2.4, 'zoom'), bespoke: Finale},
];

// Spread the stats/cards/equation cues across their narration for a lively reveal.
for (const s of SHOTS) {
	const v = s.scene.visual;
	const base = s.scene.segments![0];
	const n = v.type === 'stats' ? v.stats.length : v.type === 'cards3d' ? v.cards.length : v.type === 'equation' ? v.steps.length : 0;
	if (n) {
		const span = base.end - base.start;
		s.scene.segments = [
			{...base, end: base.start},
			...Array.from({length: n}, (_, i) => ({...base, start: base.start + Math.round((span * i) / n) + (i === 0 ? 4 : 0), end: base.start + Math.round((span * (i + 1)) / n)})),
		];
		// captions should still show the whole line once
		s.scene.segments[0] = {...base};
		s.scene.segments[0].end = base.end;
	}
}

export const FILM_FRAMES = SHOTS.reduce((a, s) => a + s.scene.durationInFrames, 0) - T * (SHOTS.length - 1);

const placed = (() => {
	let t = 0;
	return SHOTS.map((s) => {
		const p = {scene: {...s.scene, segments: seg(s.key)}, start: t};
		t += s.scene.durationInFrames - T;
		return p;
	});
})();

export const PragyanFilm: React.FC = () => {
	const theme = getTheme('cosmos');
	return (
		<ThemeContext.Provider value={theme}>
			<AbsoluteFill style={{background: theme.bg}}>
				<Background kind="shader" />
				<TransitionSeries>
					{SHOTS.map((s, i) => (
						<React.Fragment key={s.key}>
							{i > 0 ? <TransitionSeries.Transition timing={linearTiming({durationInFrames: T})} presentation={presentationFor(s.scene.transition)} /> : null}
							<TransitionSeries.Sequence durationInFrames={s.scene.durationInFrames}>
								{s.bespoke ? (
									<SceneContext.Provider value={{scene: s.scene, duration: s.scene.durationInFrames}}>
										<s.bespoke />
									</SceneContext.Provider>
								) : (
									<SceneRenderer scene={s.scene} />
								)}
								<Sequence from={LEAD}>
									<Html5Audio src={staticFile(`film/${s.key}.wav`)} />
								</Sequence>
							</TransitionSeries.Sequence>
						</React.Fragment>
					))}
				</TransitionSeries>
				<Vignette />
				<Grain />
				<Captions placed={placed} />
			</AbsoluteFill>
		</ThemeContext.Provider>
	);
};
