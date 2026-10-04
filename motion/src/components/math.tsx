import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {Visual} from '../spec';
import {useTheme} from '../theme';
import {clamp, EASE, useCues} from '../motion';
import {Body, Heading, Latex, Stage} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

/**
 * A derivation as a vertical "film strip": the current line sits centre stage,
 * earlier lines rise, shrink and dim — you always see where you came from.
 */
export const EquationScene: React.FC<{v: V<'equation'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const steps = v.steps.slice(0, 8);
	const cues = useCues(steps.length, {first: v.heading ? 26 : 12, spread: 0.78});
	// Continuous "playhead" over step indices so motion is smooth, not stepped.
	let pos = 0;
	for (let i = 1; i < cues.length; i++) {
		pos += interpolate(frame, [cues[i] - 4, cues[i] + 18], [0, 1], {...clamp, easing: EASE.inOut});
	}
	const maxLen = Math.max(...steps.map((s) => s.latex.length));
	const size = maxLen > 70 ? 54 : maxLen > 40 ? 66 : 80;
	const tall = steps.some((s) => /\\frac|\\sum|\\int|\\begin|\\sqrt|\\over/.test(s.latex));
	const slot = size * (tall ? 3.6 : 2.6);
	return (
		<Stage>
			{v.heading ? <Heading text={v.heading} size={60} /> : null}
			<div style={{position: 'relative', flex: 1, height: v.heading ? 600 : 740, overflow: 'hidden', maskImage: 'linear-gradient(to bottom, transparent, black 22%, black 85%, transparent)'}}>
				{steps.map((s, i) => {
					const d = i - pos; // 0 = active, negative = above (past)
					const appear = interpolate(frame, [cues[i], cues[i] + 16], [0, 1], {...clamp, easing: EASE.out});
					const scale = interpolate(Math.abs(d), [0, 1, 3], [1, 0.62, 0.5], clamp);
					const opacity = (d < -2.6 ? 0 : interpolate(Math.abs(d), [0, 1, 2.6], [1, 0.38, 0.12], clamp)) * appear;
					const centreY = (v.heading ? 600 : 740) * 0.56;
					const y = centreY + d * slot * (d < 0 ? 0.8 : 1) + (1 - appear) * 50;
					return (
						<div
							key={i}
							style={{
								position: 'absolute',
								left: 0,
								right: 0,
								top: y,
								transform: `translateY(-50%) scale(${scale})`,
								opacity,
								filter: `blur(${(1 - appear) * 10}px)`,
								display: 'flex',
								flexDirection: 'column',
								alignItems: 'center',
								gap: 12,
							}}
						>
							<Latex tex={s.latex} size={size} color={Math.abs(d) < 0.5 ? theme.text : theme.muted} />
							{s.note ? (
								<div style={{opacity: interpolate(Math.abs(d), [0, 0.6], [1, 0], clamp)}}>
									<Body size={30} style={{color: theme.accent2, fontStyle: 'italic', fontFamily: theme.serif, fontSize: 36}}>
										{s.note}
									</Body>
								</div>
							) : null}
						</div>
					);
				})}
			</div>
		</Stage>
	);
};
