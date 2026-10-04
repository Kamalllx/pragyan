import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, DrawLine, EASE, Reveal, SPRING, useActiveIndex, useCues} from '../motion';
import {Body, Glass, Heading, IndexBadge, Latex, Stage} from './ui';
import {useLabel} from '../i18n';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

/** Smoothly glide between per-cue targets (the "camera follows narration" move). */
const useFollow = (cues: number[], targets: number[], dur = 22) => {
	const frame = useCurrentFrame();
	let v = targets[0] ?? 0;
	for (let i = 1; i < cues.length; i++) {
		const t = interpolate(frame, [cues[i] - 4, cues[i] - 4 + dur], [0, 1], {...clamp, easing: EASE.inOut});
		v = v + (targets[i] - v) * t;
	}
	return v;
};

/* --------------------------------- BULLETS -------------------------------- */
export const BulletsScene: React.FC<{v: V<'bullets'>}> = ({v}) => {
	const theme = useTheme();
	const items = v.items.slice(0, 6);
	const cues = useCues(items.length, {first: 24});
	const active = useActiveIndex(cues);
	const dense = items.length > 4 || items.some((i) => (i.detail?.length ?? 0) > 90);
	return (
		<Stage>
			<div style={{display: 'flex', gap: 110, height: '100%', alignItems: 'center'}}>
				<div style={{flex: '0 0 600px'}}>
					<Heading text={v.heading} size={v.heading.length > 40 ? 68 : 84} />
				</div>
				<div style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
					{items.map((it, i) => (
						<div key={i}>
							{i > 0 ? <DrawLine start={cues[i] - 6} color={theme.border} duration={24} /> : null}
							<Reveal start={cues[i]} y={26}>
								<div
									style={{
										display: 'flex',
										gap: 30,
										padding: dense ? '20px 0' : '30px 0',
										opacity: active > i ? 0.4 : 1,
										transition: 'none',
									}}
								>
									<IndexBadge n={i + 1} active={i === active} size={dense ? 46 : 54} />
									<div style={{display: 'flex', flexDirection: 'column', gap: 8}}>
										<div
											style={{
												fontFamily: theme.display,
												fontWeight: Math.min(650, theme.displayWeight + 50),
												letterSpacing: '-0.02em',
												fontSize: dense ? 38 : 46,
												color: theme.text,
												lineHeight: 1.1,
											}}
										>
											{it.title}
										</div>
										{it.detail ? (
											<Body size={dense ? 26 : 30} muted>
												{it.detail}
											</Body>
										) : null}
									</div>
								</div>
							</Reveal>
						</div>
					))}
				</div>
			</div>
		</Stage>
	);
};

/* ---------------------------------- STEPS --------------------------------- */
export const StepsScene: React.FC<{v: V<'steps'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const steps = v.steps.slice(0, 8);
	const n = steps.length + (v.answer ? 1 : 0);
	const cues = useCues(n, {first: 30, spread: 0.8});
	const active = useActiveIndex(cues);
	const heights = steps.map((s) => (s.latex ? 230 : s.detail ? 150 : 104));
	const tops = heights.reduce<number[]>((acc, h, i) => [...acc, i === 0 ? 0 : acc[i - 1] + heights[i - 1] + 26], []);
	const viewport = 560;
	const targets = [...tops, (tops[tops.length - 1] ?? 0) + (heights[heights.length - 1] ?? 0) + 26].map((t) =>
		Math.max(0, t - viewport * 0.35),
	);
	const offset = useFollow(cues, targets.slice(0, n));
	const railP = interpolate(frame, [cues[0], cues[Math.max(0, steps.length - 1)] + 20], [0, 1], {...clamp, easing: EASE.inOut});
	const totalH = (tops[tops.length - 1] ?? 0) + (heights[heights.length - 1] ?? 0);
	return (
		<Stage>
			<Heading text={v.heading} size={64} eyebrow={label('steps')} />
			<div
				style={{
					position: 'relative',
					marginTop: 44,
					height: viewport + 40,
					overflow: 'hidden',
					maskImage: 'linear-gradient(to bottom, transparent, black 6%, black 88%, transparent)',
				}}
			>
				<div style={{position: 'relative', transform: `translateY(${-offset + 16}px)`}}>
					<div
						style={{
							position: 'absolute',
							left: 26,
							top: 30,
							width: 2,
							height: totalH,
							background: alpha(theme.text, 0.1),
						}}
					/>
					<div
						style={{
							position: 'absolute',
							left: 26,
							top: 30,
							width: 2,
							height: totalH * railP,
							background: `linear-gradient(${theme.accent}, ${alpha(theme.accent, 0.2)})`,
						}}
					/>
					{steps.map((s, i) => {
						const p = spring({frame: frame - cues[i], fps, config: SPRING.soft});
						return (
							<div
								key={i}
								style={{
									position: 'absolute',
									top: tops[i],
									left: 0,
									right: 0,
									display: 'flex',
									gap: 40,
									opacity: interpolate(p, [0, 0.5], [0, 1], clamp) * (active > i ? 0.5 : 1),
									transform: `translateX(${(1 - p) * 30}px)`,
								}}
							>
								<IndexBadge n={i + 1} active={i === active} />
								<div style={{display: 'flex', flexDirection: 'column', gap: 10, paddingTop: 4, flex: 1}}>
									<div style={{fontFamily: theme.display, fontWeight: theme.displayWeight, fontSize: 42, color: theme.text, letterSpacing: '-0.02em'}}>
										{s.title}
									</div>
									{s.detail ? (
										<Body size={28} muted style={{maxWidth: 1300}}>
											{s.detail}
										</Body>
									) : null}
									{s.latex ? <Latex tex={s.latex} size={50} display={false} style={{marginTop: 6, color: theme.accent2}} /> : null}
								</div>
							</div>
						);
					})}
					{v.answer ? (
						<div style={{position: 'absolute', top: totalH + 40, left: 90, right: 0}}>
							<Reveal start={cues[n - 1]} y={30} scale={0.94} config={SPRING.bouncy}>
								<Glass style={{padding: '28px 40px', display: 'inline-flex', alignItems: 'center', gap: 30}} glow={1}>
									<span style={{fontFamily: theme.mono, fontSize: 22, letterSpacing: '0.2em', color: theme.accent, textTransform: 'uppercase'}}>
										{label('answer')}
									</span>
									<AnswerBody text={v.answer} />
								</Glass>
							</Reveal>
						</div>
					) : null}
				</div>
			</div>
		</Stage>
	);
};

const AnswerBody: React.FC<{text: string}> = ({text}) => {
	const theme = useTheme();
	const looksLatex = /\\[a-zA-Z]+|\^|_\{|=/.test(text) && !/\s{2,}/.test(text) && text.length < 80;
	return looksLatex ? (
		<Latex tex={text} size={52} display={false} />
	) : (
		<span style={{fontFamily: theme.display, fontSize: 46, fontWeight: theme.displayWeight, color: theme.text}}>{text}</span>
	);
};

/* -------------------------------- TIMELINE -------------------------------- */
export const TimelineScene: React.FC<{v: V<'timeline'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const events = v.events.slice(0, 8);
	const cues = useCues(events.length, {first: 26});
	const active = useActiveIndex(cues);
	const gap = 440;
	const visibleW = 1620;
	const trackW = Math.max(visibleW, (events.length - 1) * gap + 200);
	const xs = events.map((_, i) => 100 + i * (events.length > 1 ? (trackW - 200) / (events.length - 1) : 0));
	const targets = xs.map((x) => Math.min(Math.max(0, x - visibleW / 2), trackW - visibleW));
	const pan = useFollow(cues, targets, 30);
	const lineP = interpolate(frame, [cues[0] - 10, cues[events.length - 1] + 20], [0.02, 1], {...clamp, easing: EASE.inOut});
	return (
		<Stage>
			{v.heading ? <Heading text={v.heading} size={68} eyebrow={label('timeline')} /> : null}
			<div style={{position: 'relative', marginTop: 90, height: 460, overflow: 'hidden', maskImage: 'linear-gradient(90deg, transparent, black 5%, black 95%, transparent)'}}>
				<div style={{position: 'absolute', left: 0, top: 0, width: trackW, height: '100%', transform: `translateX(${-pan}px)`}}>
					<div style={{position: 'absolute', top: 120, left: 0, width: trackW, height: 2, background: alpha(theme.text, 0.1)}} />
					<div style={{position: 'absolute', top: 120, left: 0, width: trackW * lineP, height: 2, background: theme.accent}} />
					{events.map((e, i) => {
						const p = spring({frame: frame - cues[i], fps, config: SPRING.bouncy});
						const on = i === active;
						return (
							<div key={i} style={{position: 'absolute', left: xs[i], top: 0, width: 380, transform: 'translateX(-24px)'}}>
								<div
									style={{
										fontFamily: theme.mono,
										fontSize: 26,
										color: theme.accent,
										letterSpacing: '0.06em',
										height: 70,
										opacity: p,
										transform: `translateY(${(1 - p) * 16}px)`,
									}}
								>
									{e.date}
								</div>
								<div
									style={{
										width: 48,
										height: 48,
										borderRadius: 48,
										marginTop: 26 - 24 + 2,
										display: 'grid',
										placeItems: 'center',
										transform: `scale(${p})`,
									}}
								>
									<div
										style={{
											width: on ? 22 : 16,
											height: on ? 22 : 16,
											borderRadius: 22,
											background: on ? theme.accent : theme.bg,
											border: `2px solid ${theme.accent}`,
											boxShadow: on ? `0 0 30px ${alpha(theme.accent, 0.7)}` : 'none',
										}}
									/>
								</div>
								<Reveal start={cues[i] + 4} y={20}>
									<div style={{marginTop: 26, opacity: active > i ? 0.5 : 1}}>
										<div style={{fontFamily: theme.display, fontWeight: theme.displayWeight, fontSize: 38, color: theme.text, lineHeight: 1.1, letterSpacing: '-0.02em'}}>
											{e.title}
										</div>
										{e.detail ? (
											<Body size={25} muted style={{marginTop: 10}}>
												{e.detail}
											</Body>
										) : null}
									</div>
								</Reveal>
							</div>
						);
					})}
				</div>
			</div>
		</Stage>
	);
};

/* --------------------------------- CARDS3D -------------------------------- */
export const Cards3dScene: React.FC<{v: V<'cards3d'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const cards = v.cards.slice(0, 5);
	const cues = useCues(cards.length, {first: 24});
	const active = useActiveIndex(cues);
	const n = cards.length;
	const camY = interpolate(frame, [0, 400], [-8, 8], {extrapolateRight: 'extend'});
	return (
		<Stage drift={0.5}>
			{v.heading ? <Heading text={v.heading} size={64} /> : null}
			<div style={{position: 'relative', flex: 1, minHeight: 560, perspective: 1800, marginTop: 10}}>
				<div
					style={{
						position: 'absolute',
						inset: 0,
						transformStyle: 'preserve-3d',
						transform: `rotateX(8deg) rotateY(${Math.sin(camY / 10) * 6}deg)`,
					}}
				>
					{cards.map((c, i) => {
						const p = spring({frame: frame - cues[i], fps, config: SPRING.soft});
						const on = i === active;
						const spread = n > 1 ? (i - (n - 1) / 2) : 0;
						const cw = n > 4 ? 300 : n > 3 ? 350 : 440;
						const x = spread * (cw + (n > 3 ? 40 : 70));
						const z = on ? 90 : -40 - Math.abs(spread) * 30;
						const ry = on ? 0 : -spread * 8;
						return (
							<div
								key={i}
								style={{
									position: 'absolute',
									left: '50%',
									top: '50%',
									width: cw,
									transformStyle: 'preserve-3d',
									transform: `translate(-50%, -50%) translate3d(${x}px, ${(1 - p) * 220}px, ${z * p}px) rotateY(${ry}deg)`,
									opacity: interpolate(p, [0, 0.4], [0, 1], clamp),
									zIndex: on ? 10 : 5 - Math.abs(Math.round(spread)),
								}}
							>
								<Glass style={{padding: '40px 38px', minHeight: 400}} glow={on ? 0.9 : 0}>
									<div style={{fontFamily: theme.mono, fontSize: 22, color: theme.accent, letterSpacing: '0.16em'}}>
										{String(i + 1).padStart(2, '0')}
									</div>
									<div
										style={{
											fontFamily: theme.display,
											fontWeight: theme.displayWeight,
											fontSize: 40,
											lineHeight: 1.08,
											color: theme.text,
											margin: '26px 0 18px',
											letterSpacing: '-0.02em',
										}}
									>
										{c.title}
									</div>
									<Body size={26} muted>
										{c.body}
									</Body>
								</Glass>
							</div>
						);
					})}
				</div>
			</div>
		</Stage>
	);
};
