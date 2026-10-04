import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, DrawLine, EASE, FadeWords, isLatin, Reveal, SPRING, tracking, useActiveIndex, useCues, useEnter, Words} from '../motion';
import {useLabel} from '../i18n';
import {Body, Eyebrow, Glass, Heading, Stage} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

/* ---------------------------------- TITLE --------------------------------- */
export const TitleScene: React.FC<{v: V<'title'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const len = v.title.length;
	const size = len > 48 ? 104 : len > 30 ? 128 : 156;
	return (
		<Stage drift={1.4}>
			<OrbitMark />
			<div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%', gap: 40, maxWidth: 1380}}>
				{v.eyebrow ? <Eyebrow text={v.eyebrow} start={6} /> : null}
				<div
					style={{
						fontFamily: theme.display,
						fontWeight: theme.displayWeight,
						letterSpacing: tracking(v.title, theme.displayTracking),
						fontSize: size,
						lineHeight: isLatin(v.title) ? 0.98 : 1.25,
						color: theme.text,
						textWrap: 'balance',
					}}
				>
					<Words text={v.title} start={12} stagger={3.5} config={SPRING.soft} />
				</div>
				{v.subtitle ? (
					<Reveal start={34} y={20} blur={10}>
						<Body size={38} muted style={{maxWidth: 1100}}>
							{v.subtitle}
						</Body>
					</Reveal>
				) : null}
				<div style={{opacity: interpolate(frame, [40, 60], [0, 1], clamp)}}>
					<DrawLine start={40} duration={40} color={alpha(theme.text, 0.18)} length={520} />
				</div>
			</div>
		</Stage>
	);
};

/** Concentric arcs that draw themselves — the Pragyan "orbit" signature. */
const OrbitMark: React.FC = () => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const rings = [420, 330, 240];
	return (
		<svg
			width={1000}
			height={1000}
			viewBox="-500 -500 1000 1000"
			style={{position: 'absolute', right: -180, top: '50%', transform: `translateY(-50%) rotate(${frame * 0.08}deg)`}}
		>
			{rings.map((r, i) => {
				const c = 2 * Math.PI * r;
				const t = interpolate(frame - 8 - i * 6, [0, 70], [0, 1], {...clamp, easing: EASE.draw});
				return (
					<circle
						key={r}
						r={r}
						fill="none"
						stroke={i === 1 ? alpha(theme.accent, 0.5) : alpha(theme.text, 0.1)}
						strokeWidth={i === 1 ? 1.6 : 1}
						strokeDasharray={c}
						strokeDashoffset={c * (1 - t * (i === 1 ? 0.72 : 1))}
					/>
				);
			})}
			{(() => {
				const a = frame / 40;
				const p = interpolate(frame, [40, 60], [0, 1], clamp);
				return <circle cx={Math.cos(a) * 330} cy={Math.sin(a) * 330} r={9} fill={theme.accent} opacity={p} />;
			})()}
		</svg>
	);
};

/* --------------------------------- KINETIC -------------------------------- */
export const KineticScene: React.FC<{v: V<'kinetic'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const cues = useCues(v.lines.length, {first: 8, spread: 0.75});
	const active = useActiveIndex(cues);
	const emph = new Set((v.emphasis ?? []).map((e) => e.toLowerCase().replace(/[^\w]/g, '')));
	return (
		<Stage drift={0.8}>
			<div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%', gap: 10}}>
				{v.lines.map((line, i) => {
					const p = spring({frame: frame - cues[i], fps, config: SPRING.snappy});
					const isActive = i === active;
					const size = line.length > 34 ? 96 : 128;
					return (
						<div
							key={i}
							style={{
								fontFamily: theme.display,
								fontWeight: theme.displayWeight,
								letterSpacing: tracking(line, theme.displayTracking),
								fontSize: size,
								lineHeight: isLatin(line) ? 1.02 : 1.3,
								color: theme.text,
								opacity: frame < cues[i] ? 0 : isActive || active < 0 ? 1 : 0.28,
								transform: `translateY(${(1 - p) * 40}px)`,
								filter: `blur(${(1 - p) * 12}px)`,
							}}
						>
							<Words
								text={line}
								start={cues[i]}
								stagger={2.2}
								wordStyle={(w) =>
									isLatin(w) && emph.has(w.toLowerCase().replace(/[^\w]/g, ''))
										? {fontFamily: theme.serif, fontStyle: 'italic', fontWeight: 400, color: theme.accent, letterSpacing: '-0.01em'}
										: undefined
								}
							/>
						</div>
					);
				})}
			</div>
		</Stage>
	);
};

/* ---------------------------------- QUOTE --------------------------------- */
export const QuoteScene: React.FC<{v: V<'quote'>}> = ({v}) => {
	const theme = useTheme();
	const p = useEnter(4, SPRING.heavy);
	const size = v.text.length > 160 ? 58 : v.text.length > 90 ? 72 : 92;
	return (
		<Stage>
			<div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%', maxWidth: 1450, margin: '0 auto'}}>
				<div
					style={{
						fontFamily: theme.serif,
						fontSize: 260,
						lineHeight: 0.6,
						color: theme.accent,
						height: 120,
						opacity: p,
						transform: `scale(${0.6 + 0.4 * p})`,
						transformOrigin: 'left bottom',
					}}
				>
					&ldquo;
				</div>
				<div style={{fontFamily: theme.serif, fontStyle: 'italic', fontSize: size, lineHeight: 1.18, color: theme.text, textWrap: 'balance'}}>
					<FadeWords text={v.text} start={10} stagger={2} />
				</div>
				{v.attribution ? (
					<Reveal start={30 + v.text.split(' ').length * 2} y={14}>
						<div style={{display: 'flex', alignItems: 'center', gap: 20, marginTop: 50}}>
							<DrawLine start={30 + v.text.split(' ').length * 2} color={theme.accent} length={60} thickness={2} />
							<span style={{fontFamily: theme.mono, fontSize: 26, letterSpacing: tracking(v.attribution, '0.12em'), textTransform: isLatin(v.attribution) ? 'uppercase' : 'none', color: theme.muted}}>
								{v.attribution}
							</span>
						</div>
					</Reveal>
				) : null}
			</div>
		</Stage>
	);
};

/* ------------------------------- DEFINITION ------------------------------- */
export const DefinitionScene: React.FC<{v: V<'definition'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const cues = useCues(v.analogy ? 2 : 1, {first: 30});
	const size = v.term.length > 22 ? 110 : v.term.length > 12 ? 140 : 180;
	return (
		<Stage>
			<div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%', gap: 34}}>
				<Eyebrow text={label('definition')} start={2} />
				<div style={{fontFamily: isLatin(v.term) ? theme.serif : theme.display, fontSize: size, lineHeight: isLatin(v.term) ? 0.95 : 1.25, color: theme.text, letterSpacing: tracking(v.term, '-0.02em')}}>
					<Words text={v.term} start={8} stagger={4} config={SPRING.soft} />
				</div>
				<div style={{display: 'flex', gap: 60, alignItems: 'flex-start'}}>
					<Reveal start={cues[0]} y={18} style={{flex: 1.3}}>
						<Body size={42} style={{maxWidth: 1000}}>
							{v.definition}
						</Body>
					</Reveal>
					{v.analogy ? (
						<Reveal start={cues[1]} y={30} x={30} style={{flex: 1}}>
							<Glass style={{padding: '34px 40px'}} glow={0.4}>
								<div
									style={{
										fontFamily: theme.mono,
										fontSize: 20,
										letterSpacing: '0.2em',
										textTransform: 'uppercase',
										color: theme.accent2,
										marginBottom: 16,
									}}
								>
									{label('analogy')}
								</div>
								<Body size={32}>{v.analogy}</Body>
							</Glass>
						</Reveal>
					) : null}
				</div>
			</div>
		</Stage>
	);
};

/* --------------------------------- SUMMARY -------------------------------- */
export const SummaryScene: React.FC<{v: V<'summary'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const items = v.takeaways.slice(0, 6);
	const cues = useCues(items.length, {first: 26});
	const active = useActiveIndex(cues);
	const size = items.length > 4 ? 34 : 40;
	return (
		<Stage>
			<div style={{display: 'flex', gap: 100, height: '100%', alignItems: 'center'}}>
				<div style={{flex: '0 0 560px'}}>
					<Heading text={v.heading} eyebrow={label('takeaways')} size={88} />
				</div>
				<div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: items.length > 4 ? 22 : 32}}>
					{items.map((t, i) => {
						const d = interpolate(frame - cues[i], [0, 18], [0, 1], {...clamp, easing: EASE.draw});
						return (
							<Reveal key={i} start={cues[i]} y={24} x={-10}>
								<div style={{display: 'flex', gap: 28, alignItems: 'flex-start', opacity: active > i ? 0.55 : 1}}>
									<svg width={46} height={46} viewBox="0 0 46 46" style={{flexShrink: 0, marginTop: 2}}>
										<circle cx={23} cy={23} r={21} fill={alpha(theme.accent, 0.12)} stroke={alpha(theme.accent, 0.6)} strokeWidth={1.5} />
										<path
											d="M13 24 L20 31 L33 16"
											fill="none"
											stroke={theme.accent}
											strokeWidth={3}
											strokeLinecap="round"
											strokeLinejoin="round"
											strokeDasharray={32}
											strokeDashoffset={32 * (1 - d)}
										/>
									</svg>
									<Body size={size}>{t}</Body>
								</div>
							</Reveal>
						);
					})}
				</div>
			</div>
		</Stage>
	);
};

export const Fill: React.FC<{children: React.ReactNode}> = ({children}) => <AbsoluteFill>{children}</AbsoluteFill>;
