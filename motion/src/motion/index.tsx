import React, {createContext, useContext, useMemo} from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {SceneSpec} from '../spec';

/* ------------------------------------------------------------------ */
/* Curves. One vocabulary for the whole film keeps motion coherent.     */
/* ------------------------------------------------------------------ */
export const EASE = {
	/** Entrances: fast start, long soft landing. */
	out: Easing.bezier(0.16, 1, 0.3, 1),
	/** Camera moves and morphs. */
	inOut: Easing.bezier(0.65, 0, 0.35, 1),
	/** Exits: accelerate away. */
	in: Easing.bezier(0.7, 0, 0.84, 0),
	/** Drawn lines. */
	draw: Easing.bezier(0.45, 0, 0.15, 1),
};

export const SPRING = {
	soft: {damping: 22, stiffness: 110, mass: 1},
	snappy: {damping: 18, stiffness: 190, mass: 0.7},
	heavy: {damping: 26, stiffness: 90, mass: 1.4},
	bouncy: {damping: 11, stiffness: 160, mass: 0.8},
};

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/* ------------------------------------------------------------------ */
/* Script awareness. Tracking, uppercase and synthetic italics are       */
/* Latin conventions — on Devanagari, CJK, Arabic etc. they break        */
/* shaping (conjuncts split, matras clip).                              */
/* ------------------------------------------------------------------ */
const NON_LATIN = /[֐-ࣿऀ-෿฀-࿿က-႟぀-ヿ㐀-鿿가-힯]/;
export const isLatin = (s: string | undefined | null) => !NON_LATIN.test(s ?? '');
export const tracking = (s: string | undefined | null, latin: string) => (isLatin(s) ? latin : '0em');
export const caps = (s: string | undefined | null): React.CSSProperties =>
	isLatin(s) ? {textTransform: 'uppercase'} : {textTransform: 'none', letterSpacing: 0};

/* ------------------------------------------------------------------ */
/* Scene context: lets every component sync to narration cues.          */
/* ------------------------------------------------------------------ */
type SceneCtx = {scene: SceneSpec; duration: number};
export const SceneContext = createContext<SceneCtx | null>(null);
export const useScene = () => {
	const ctx = useContext(SceneContext);
	if (!ctx) throw new Error('useScene outside SceneContext');
	return ctx;
};

/**
 * Returns n reveal frames for n items, synced to narration where possible.
 * Contract: segment 0 introduces the scene, segment k narrates item k.
 */
export const useCues = (n: number, opts: {first?: number; spread?: number} = {}): number[] => {
	const {scene, duration} = useScene();
	return useMemo(() => {
		const segs = scene.segments ?? [];
		const first = opts.first ?? 14;
		if (n <= 0) return [];
		if (segs.length >= n + 1) return segs.slice(1, n + 1).map((s) => Math.max(first, s.start - 4));
		if (segs.length === n && n > 1) return segs.map((s, i) => (i === 0 ? first : Math.max(first, s.start - 4)));
		const spread = opts.spread ?? 0.62;
		const span = Math.max(1, duration * spread - first);
		return Array.from({length: n}, (_, i) => Math.round(first + (span * i) / Math.max(1, n - 1 || 1)));
	}, [scene.segments, duration, n, opts.first, opts.spread]);
};

/** Index of the item currently being narrated (-1 before the first cue). */
export const useActiveIndex = (cues: number[]) => {
	const frame = useCurrentFrame();
	let active = -1;
	cues.forEach((c, i) => {
		if (frame >= c) active = i;
	});
	return active;
};

/* ------------------------------------------------------------------ */
/* Primitives                                                           */
/* ------------------------------------------------------------------ */
export const useEnter = (start: number, config = SPRING.soft, durationInFrames?: number) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return spring({frame: frame - start, fps, config, durationInFrames});
};

/** Fade + rise + de-blur. The default entrance for anything that isn't text. */
export const Reveal: React.FC<{
	start?: number;
	y?: number;
	x?: number;
	blur?: number;
	scale?: number;
	config?: typeof SPRING.soft;
	style?: React.CSSProperties;
	children: React.ReactNode;
}> = ({start = 0, y = 36, x = 0, blur = 14, scale = 0.985, config = SPRING.soft, style, children}) => {
	const p = useEnter(start, config);
	return (
		<div
			style={{
				opacity: interpolate(p, [0, 0.6], [0, 1], clamp),
				transform: `translate3d(${(1 - p) * x}px, ${(1 - p) * y}px, 0) scale(${scale + (1 - scale) * p})`,
				filter: blur ? `blur(${(1 - Math.min(1, p)) * blur}px)` : undefined,
				willChange: 'transform, opacity, filter',
				...style,
			}}
		>
			{children}
		</div>
	);
};

/**
 * Masked word-by-word reveal. Each word rises out of its own clipping line —
 * the editorial headline move.
 */
export const Words: React.FC<{
	text: string;
	start?: number;
	stagger?: number;
	style?: React.CSSProperties;
	wordStyle?: (word: string, i: number) => React.CSSProperties | undefined;
	mask?: boolean;
	config?: typeof SPRING.soft;
}> = ({text, start = 0, stagger = 3, style, wordStyle, mask = true, config = SPRING.snappy}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const words = text.split(/\s+/).filter(Boolean);
	return (
		<span style={{display: 'inline', ...style}}>
			{words.map((w, i) => {
				const p = spring({frame: frame - start - i * stagger, fps, config});
				return (
					<span
						key={i}
						style={{
							display: 'inline-block',
							overflow: mask ? 'hidden' : 'visible',
							verticalAlign: 'top',
							// Room above/below for ascending matras, accents and descenders.
							paddingTop: mask ? '0.22em' : 0,
							marginTop: mask ? '-0.22em' : 0,
							paddingBottom: mask ? '0.12em' : 0,
							marginBottom: mask ? '-0.12em' : 0,
						}}
					>
						<span
							style={{
								display: 'inline-block',
								transform: `translate3d(0, ${(1 - p) * 105}%, 0) rotate(${(1 - p) * 4}deg)`,
								opacity: mask ? 1 : p,
								transformOrigin: '0% 100%',
								...wordStyle?.(w, i),
							}}
						>
							{w}
						</span>
						{i < words.length - 1 ? ' ' : ''}
					</span>
				);
			})}
		</span>
	);
};

/** Soft fade-in by word (for body copy, where masks feel too dramatic). */
export const FadeWords: React.FC<{text: string; start?: number; stagger?: number; style?: React.CSSProperties}> = ({
	text,
	start = 0,
	stagger = 1.5,
	style,
}) => {
	const frame = useCurrentFrame();
	const words = text.split(/\s+/).filter(Boolean);
	return (
		<span style={style}>
			{words.map((w, i) => {
				const t = interpolate(frame - start - i * stagger, [0, 14], [0, 1], {...clamp, easing: EASE.out});
				return (
					<span
						key={i}
						style={{
							opacity: 0.08 + t * 0.92,
							filter: `blur(${(1 - t) * 6}px)`,
							display: 'inline-block',
							transform: `translateY(${(1 - t) * 8}px)`,
						}}
					>
						{w}
						{i < words.length - 1 ? ' ' : ''}
					</span>
				);
			})}
		</span>
	);
};

export const CountUp: React.FC<{
	value: number;
	start?: number;
	duration?: number;
	decimals?: number;
	prefix?: string;
	suffix?: string;
}> = ({value, start = 0, duration = 45, decimals, prefix = '', suffix = ''}) => {
	const frame = useCurrentFrame();
	const t = interpolate(frame - start, [0, duration], [0, 1], {...clamp, easing: EASE.out});
	const d = decimals ?? (Number.isInteger(value) ? 0 : 1);
	const v = value * t;
	const s = Math.abs(value) >= 10000 ? v.toLocaleString('en-US', {maximumFractionDigits: d}) : v.toFixed(d);
	return (
		<span style={{fontVariantNumeric: 'tabular-nums'}}>
			{prefix}
			{s}
			{suffix}
		</span>
	);
};

/** A hairline that draws itself. */
export const DrawLine: React.FC<{
	start?: number;
	duration?: number;
	color: string;
	vertical?: boolean;
	thickness?: number;
	length?: number | string;
	style?: React.CSSProperties;
	origin?: 'start' | 'center';
}> = ({start = 0, duration = 30, color, vertical, thickness = 1.5, length = '100%', style, origin = 'start'}) => {
	const frame = useCurrentFrame();
	const t = interpolate(frame - start, [0, duration], [0, 1], {...clamp, easing: EASE.draw});
	return (
		<div
			style={{
				width: vertical ? thickness : length,
				height: vertical ? length : thickness,
				background: color,
				transform: vertical ? `scaleY(${t})` : `scaleX(${t})`,
				transformOrigin: origin === 'center' ? 'center' : vertical ? 'top' : 'left',
				...style,
			}}
		/>
	);
};

/** Slow ambient drift so no frame is ever perfectly still. */
export const useDrift = (amp = 1) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const t = frame / Math.max(1, durationInFrames);
	return {
		scale: 1 + 0.025 * amp * t,
		x: Math.sin(frame / 90) * 6 * amp,
		y: Math.cos(frame / 110) * 4 * amp,
	};
};

/** Focus treatment: the narrated item is bright, earlier items recede. */
export const focusStyle = (i: number, active: number): React.CSSProperties => {
	if (active < 0 || i === active) return {opacity: 1};
	if (i < active) return {opacity: 0.42};
	return {opacity: 1};
};
