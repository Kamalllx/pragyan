import React, {useMemo} from 'react';
import katex from 'katex';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {alpha, useTheme} from '../theme';
import {caps, clamp, DrawLine, EASE, isLatin, Reveal, tracking, useScene, Words} from '../motion';

export const SAFE = {x: 150, top: 120, bottom: 220};

/** Content area that respects caption space, with the slow ambient camera drift. */
export const Stage: React.FC<{children: React.ReactNode; style?: React.CSSProperties; drift?: number}> = ({
	children,
	style,
	drift = 1,
}) => {
	const frame = useCurrentFrame();
	const {duration} = useScene();
	const t = frame / Math.max(1, duration);
	const s = 1 + 0.022 * drift * t;
	const x = Math.sin(frame / 95) * 5 * drift;
	const y = Math.cos(frame / 120) * 3 * drift;
	return (
		<AbsoluteFill
			style={{
				padding: `${SAFE.top}px ${SAFE.x}px ${SAFE.bottom}px`,
				transform: `translate3d(${x}px, ${y}px, 0) scale(${s})`,
				...style,
			}}
		>
			{children}
		</AbsoluteFill>
	);
};

export const Eyebrow: React.FC<{text: string; start?: number; color?: string}> = ({text, start = 0, color}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const o = interpolate(frame - start, [0, 18], [0, 1], {...clamp, easing: EASE.out});
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: o}}>
			<DrawLine start={start} duration={22} color={color ?? theme.accent} length={56} thickness={2} />
			<span
				style={{
					fontFamily: isLatin(text) ? theme.mono : theme.body,
					fontSize: isLatin(text) ? 22 : 26,
					letterSpacing: tracking(text, '0.22em'),
					...caps(text),
					color: color ?? theme.accent,
					transform: `translateX(${(1 - o) * -12}px)`,
				}}
			>
				{text}
			</span>
		</div>
	);
};

export const Heading: React.FC<{text: string; start?: number; size?: number; eyebrow?: string; style?: React.CSSProperties}> = ({
	text,
	start = 0,
	size = 76,
	eyebrow,
	style,
}) => {
	const theme = useTheme();
	return (
		<div style={{display: 'flex', flexDirection: 'column', gap: 22, ...style}}>
			{eyebrow ? <Eyebrow text={eyebrow} start={start} /> : null}
			<div
				style={{
					fontFamily: theme.display,
					fontWeight: theme.displayWeight,
					letterSpacing: tracking(text, theme.displayTracking),
					fontSize: size,
					lineHeight: 1.04,
					color: theme.text,
					textWrap: 'balance',
				}}
			>
				<Words text={text} start={start + 4} stagger={2.5} />
			</div>
		</div>
	);
};

export const Glass: React.FC<{children: React.ReactNode; style?: React.CSSProperties; glow?: number}> = ({
	children,
	style,
	glow = 0,
}) => {
	const theme = useTheme();
	return (
		<div
			style={{
				background: theme.dark
					? `linear-gradient(180deg, ${alpha('#ffffff', 0.065)}, ${alpha('#ffffff', 0.025)})`
					: `linear-gradient(180deg, ${alpha('#ffffff', 0.7)}, ${alpha('#ffffff', 0.45)})`,
				border: `1px solid ${theme.border}`,
				borderRadius: 28,
				boxShadow: theme.dark
					? `inset 0 1px 0 ${alpha('#ffffff', 0.08)}, 0 30px 80px -30px rgba(0,0,0,0.6)${glow ? `, 0 0 ${60 * glow}px ${alpha(theme.accent, 0.25 * glow)}` : ''}`
					: `0 1px 0 rgba(255,255,255,0.8) inset, 0 24px 60px -30px rgba(60,40,20,0.35)${glow ? `, 0 0 ${50 * glow}px ${alpha(theme.accent, 0.2 * glow)}` : ''}`,
				backdropFilter: 'blur(18px)',
				...style,
			}}
		>
			{children}
		</div>
	);
};

export const Latex: React.FC<{tex: string; size?: number; color?: string; display?: boolean; style?: React.CSSProperties}> = ({
	tex,
	size = 64,
	color,
	display = true,
	style,
}) => {
	const theme = useTheme();
	const html = useMemo(() => {
		try {
			return katex.renderToString(tex, {throwOnError: false, displayMode: display, strict: 'ignore', output: 'html'});
		} catch {
			return tex;
		}
	}, [tex, display]);
	return (
		<div
			className="pragyan-katex"
			style={{fontSize: size, color: color ?? theme.text, lineHeight: 1.2, ...style}}
			dangerouslySetInnerHTML={{__html: html}}
		/>
	);
};

export const IndexBadge: React.FC<{n: number; active?: boolean; size?: number}> = ({n, active, size = 54}) => {
	const theme = useTheme();
	return (
		<div
			style={{
				width: size,
				height: size,
				borderRadius: size,
				flexShrink: 0,
				display: 'grid',
				placeItems: 'center',
				fontFamily: theme.mono,
				fontSize: size * 0.36,
				color: active ? theme.bg : theme.accent,
				background: active ? theme.accent : 'transparent',
				border: `1.5px solid ${active ? theme.accent : alpha(theme.accent, 0.5)}`,
				boxShadow: active ? `0 0 40px ${alpha(theme.accent, 0.45)}` : 'none',
			}}
		>
			{String(n).padStart(2, '0')}
		</div>
	);
};

export const Body: React.FC<{children: React.ReactNode; size?: number; style?: React.CSSProperties; muted?: boolean}> = ({
	children,
	size = 34,
	style,
	muted,
}) => {
	const theme = useTheme();
	return (
		<div
			style={{
				fontFamily: theme.body,
				fontSize: size,
				lineHeight: 1.4,
				color: muted ? theme.muted : theme.text,
				textWrap: 'pretty',
				...style,
			}}
		>
			{children}
		</div>
	);
};

export {Reveal};
