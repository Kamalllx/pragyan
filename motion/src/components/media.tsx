import React from 'react';
import {AbsoluteFill, Img, interpolate, OffthreadVideo, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, EASE, Reveal, SPRING, useCues, useScene} from '../motion';
import {Body, Eyebrow, Glass} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

/* ---------------------------------- IMAGE --------------------------------- */
export const ImageScene: React.FC<{v: V<'image'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const {duration} = useScene();
	const ann = (v.annotations ?? []).slice(0, 5);
	const cues = useCues(ann.length, {first: 30});
	const t = frame / Math.max(1, duration);
	const enter = spring({frame: frame - 2, fps, config: SPRING.heavy});
	return (
		<AbsoluteFill style={{padding: '90px 150px 210px', display: 'flex', flexDirection: 'column', gap: 26}}>
			<div
				style={{
					flex: 1,
					position: 'relative',
					borderRadius: 28,
					overflow: 'hidden',
					border: `1px solid ${theme.border}`,
					boxShadow: '0 40px 100px -40px rgba(0,0,0,0.7)',
					opacity: enter,
					transform: `scale(${0.94 + 0.06 * enter})`,
				}}
			>
				<Img
					src={v.src}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'contain',
						background: theme.bg2,
						transform: `scale(${1.02 + 0.06 * t}) translate(${-1.2 * t}%, ${-0.8 * t}%)`,
					}}
				/>
				{ann.map((a, i) => {
					const p = spring({frame: frame - cues[i], fps, config: SPRING.bouncy});
					return (
						<div key={i} style={{position: 'absolute', left: `${a.x * 100}%`, top: `${a.y * 100}%`, transform: 'translate(-50%,-50%)'}}>
							<div style={{width: 26, height: 26, borderRadius: 26, background: theme.accent, transform: `scale(${p})`, boxShadow: `0 0 0 ${10 * p}px ${alpha(theme.accent, 0.25)}`}} />
							<div style={{position: 'absolute', left: 40, top: -24, opacity: p, transform: `translateX(${(1 - p) * -16}px)`, whiteSpace: 'nowrap'}}>
								<Glass style={{padding: '10px 20px', borderRadius: 14}}>
									<span style={{fontFamily: theme.body, fontSize: 26, color: theme.text}}>{a.label}</span>
								</Glass>
							</div>
						</div>
					);
				})}
			</div>
			{v.caption ? (
				<Reveal start={18} y={14}>
					<Body size={30} muted>
						{v.caption}
					</Body>
				</Reveal>
			) : null}
		</AbsoluteFill>
	);
};

/* ---------------------------------- MANIM --------------------------------- */
/** Embedded Manim render. Transparent renders composite straight onto the shader background. */
export const ManimScene: React.FC<{v: V<'manim'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const o = interpolate(frame, [0, 10], [0, 1], {...clamp, easing: EASE.out});
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{opacity: o, padding: v.transparent ? 0 : '70px 120px 200px'}}>
				<div
					style={{
						width: '100%',
						height: '100%',
						borderRadius: v.transparent ? 0 : 24,
						overflow: 'hidden',
						border: v.transparent ? 'none' : `1px solid ${theme.border}`,
						boxShadow: v.transparent ? 'none' : '0 40px 100px -40px rgba(0,0,0,0.7)',
					}}
				>
					<OffthreadVideo src={v.src} transparent={v.transparent} muted style={{width: '100%', height: '100%', objectFit: 'contain'}} />
				</div>
			</AbsoluteFill>
			{v.title ? (
				<div style={{position: 'absolute', left: 150, top: 70}}>
					<Eyebrow text={v.title} start={6} />
				</div>
			) : null}
			{v.caption ? (
				<div style={{position: 'absolute', left: 150, right: 150, bottom: 215}}>
					<Reveal start={20} y={10}>
						<Body size={28} muted>
							{v.caption}
						</Body>
					</Reveal>
				</div>
			) : null}
		</AbsoluteFill>
	);
};
