import React, {useMemo} from 'react';
import {AbsoluteFill, Html5Audio, interpolate, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import type {VideoSpec} from './spec';
import {alpha, getTheme, ThemeContext, useTheme} from './theme';
import {Background, Grain, Vignette} from './fx/Background';
import {SceneRenderer} from './SceneRenderer';
import {presentationFor} from './transitions';
import {Captions} from './Captions';
import {caps, clamp, tracking} from './motion';
import {LangContext} from './i18n';

export const DEFAULT_TRANSITION = 18;

export const totalFrames = (spec: VideoSpec) => {
	const T = spec.transitionFrames ?? DEFAULT_TRANSITION;
	const sum = spec.scenes.reduce((a, s) => a + s.durationInFrames, 0);
	return Math.max(1, sum - T * Math.max(0, spec.scenes.length - 1));
};

const placeScenes = (spec: VideoSpec) => {
	const T = spec.transitionFrames ?? DEFAULT_TRANSITION;
	let t = 0;
	return spec.scenes.map((scene) => {
		const placed = {scene, start: t};
		t += scene.durationInFrames - T;
		return placed;
	});
};

/** Hairline progress + chapter label: orientation without clutter. */
const Chrome: React.FC<{spec: VideoSpec; placed: ReturnType<typeof placeScenes>}> = ({spec, placed}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	let idx = 0;
	placed.forEach((p, i) => {
		if (frame >= p.start + 6) idx = i;
	});
	const chapter = placed[idx]?.scene.chapter;
	const local = frame - (placed[idx]?.start ?? 0);
	const chO = interpolate(local, [6, 22], [0, 1], clamp) * interpolate(frame, [0, 30], [0, 1], clamp);
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<div style={{position: 'absolute', left: 0, top: 0, height: 3, width: `${(frame / durationInFrames) * 100}%`, background: alpha(theme.accent, 0.8)}} />
			{chapter ? (
				<div
					style={{
						position: 'absolute',
						left: 60,
						top: 40,
						fontFamily: theme.mono,
						fontSize: 18,
						letterSpacing: tracking(chapter, '0.2em'),
						...caps(chapter),
						color: theme.muted,
						opacity: chO * 0.9,
						display: 'flex',
						gap: 14,
					}}
				>
					<span style={{color: theme.accent}}>{String(idx + 1).padStart(2, '0')}</span>
					<span>{chapter}</span>
				</div>
			) : null}
			{spec.meta.watermark !== false ? (
				<div
					style={{
						position: 'absolute',
						right: 60,
						top: 38,
						display: 'flex',
						alignItems: 'center',
						gap: 12,
						fontFamily: theme.display,
						fontWeight: 600,
						fontSize: 20,
						letterSpacing: '0.02em',
						color: alpha(theme.text, 0.55),
					}}
				>
					<svg width={22} height={22} viewBox="0 0 22 22">
						<circle cx={11} cy={11} r={9.5} fill="none" stroke={alpha(theme.text, 0.5)} strokeWidth={1.4} />
						<circle cx={11} cy={11} r={3.2} fill={theme.accent} />
					</svg>
					Pragyan
				</div>
			) : null}
		</AbsoluteFill>
	);
};

export const PragyanVideo: React.FC<VideoSpec> = (spec) => {
	const theme = useMemo(() => getTheme(spec.meta.theme, spec.meta.accent), [spec.meta.theme, spec.meta.accent]);
	const T = spec.transitionFrames ?? DEFAULT_TRANSITION;
	const placed = useMemo(() => placeScenes(spec), [spec]);
	return (
		<ThemeContext.Provider value={theme}>
			<LangContext.Provider value={spec.meta.language ?? 'en'}>
			<AbsoluteFill style={{background: theme.bg, fontFamily: theme.body}}>
				<Background kind={spec.meta.background ?? 'shader'} />
				<TransitionSeries>
					{spec.scenes.map((s, i) => (
						<React.Fragment key={s.id}>
							{i > 0 ? (
								<TransitionSeries.Transition
									timing={linearTiming({durationInFrames: T})}
									presentation={presentationFor(s.transition)}
								/>
							) : null}
							<TransitionSeries.Sequence durationInFrames={s.durationInFrames} name={`${s.id} · ${s.visual.type}`}>
								<SceneRenderer scene={s} />
								{s.audio ? (
									<Sequence from={s.audioOffset ?? 0} name="narration">
										<Html5Audio src={s.audio} />
									</Sequence>
								) : null}
							</TransitionSeries.Sequence>
						</React.Fragment>
					))}
				</TransitionSeries>
				{spec.music ? <Html5Audio src={spec.music.src} volume={spec.music.volume ?? 0.08} loop /> : null}
				<Vignette />
				<Grain />
				{spec.meta.captions ? <Captions placed={placed} /> : null}
				<Chrome spec={spec} placed={placed} />
			</AbsoluteFill>
			</LangContext.Provider>
		</ThemeContext.Provider>
	);
};
