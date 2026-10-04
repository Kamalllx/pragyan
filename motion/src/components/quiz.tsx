import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, Reveal, SPRING, useScene} from '../motion';
import {Body, Glass, Heading, Stage} from './ui';
import {useLabel} from '../i18n';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

export const QuizScene: React.FC<{v: V<'quiz'>}> = ({v}) => {
	const label = useLabel();
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const {scene, duration} = useScene();
	const opts = v.options.slice(0, 4);
	const segs = scene.segments ?? [];
	const optStart = segs[1]?.start ?? 40;
	// Reveal lands on the last narration segment (the explanation), else at 62%.
	const reveal = segs.length >= 3 ? segs[segs.length - 1].start : Math.round(duration * 0.62);
	const thinkFrom = optStart + opts.length * 6 + 10;
	const ring = interpolate(frame, [thinkFrom, reveal], [0, 1], clamp);
	const shown = frame >= reveal;
	return (
		<Stage>
			<Heading text={v.question} size={v.question.length > 80 ? 54 : 66} eyebrow={label('quiz')} />
			<div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 26, marginTop: 50}}>
				{opts.map((o, i) => {
					const correct = i === v.answerIndex;
					const p = spring({frame: frame - optStart - i * 6, fps, config: SPRING.snappy});
					const r = spring({frame: frame - reveal, fps, config: SPRING.bouncy});
					return (
						<div
							key={i}
							style={{
								opacity: interpolate(p, [0, 0.5], [0, 1], clamp) * (shown && !correct ? 1 - 0.6 * r : 1),
								transform: `translateY(${(1 - p) * 30}px) scale(${shown && correct ? 1 + 0.03 * r : 1})`,
							}}
						>
							<Glass
								style={{
									padding: '26px 30px',
									display: 'flex',
									gap: 24,
									alignItems: 'center',
									borderColor: shown && correct ? theme.good : undefined,
									boxShadow: shown && correct ? `0 0 ${60 * r}px ${alpha(theme.good, 0.35)}` : undefined,
								}}
							>
								<div
									style={{
										width: 52,
										height: 52,
										borderRadius: 14,
										flexShrink: 0,
										display: 'grid',
										placeItems: 'center',
										fontFamily: theme.mono,
										fontSize: 24,
										background: shown && correct ? theme.good : alpha(theme.text, 0.06),
										color: shown && correct ? theme.bg : theme.text,
									}}
								>
									{String.fromCharCode(65 + i)}
								</div>
								<Body size={32}>{o}</Body>
							</Glass>
						</div>
					);
				})}
			</div>
			<div style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 40, minHeight: 90}}>
				{!shown ? (
					<div style={{display: 'flex', alignItems: 'center', gap: 20, opacity: interpolate(frame, [thinkFrom, thinkFrom + 10], [0, 1], clamp)}}>
						<svg width={56} height={56} viewBox="0 0 56 56">
							<circle cx={28} cy={28} r={24} fill="none" stroke={alpha(theme.text, 0.12)} strokeWidth={4} />
							<circle
								cx={28}
								cy={28}
								r={24}
								fill="none"
								stroke={theme.accent}
								strokeWidth={4}
								strokeLinecap="round"
								strokeDasharray={150.8}
								strokeDashoffset={150.8 * ring}
								transform="rotate(-90 28 28)"
							/>
						</svg>
						<span style={{fontFamily: theme.mono, fontSize: 24, letterSpacing: '0.18em', color: theme.muted, textTransform: 'uppercase'}}>{label('think')}</span>
					</div>
				) : v.explanation ? (
					<Reveal start={reveal + 6} y={16}>
						<Body size={30} style={{color: theme.text}}>
							<span style={{color: theme.good, fontFamily: theme.mono, fontSize: 22, letterSpacing: '0.16em', marginRight: 18}}>{label('why')}</span>
							{v.explanation}
						</Body>
					</Reveal>
				) : null}
			</div>
		</Stage>
	);
};

