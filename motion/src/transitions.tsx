import React from 'react';
import {AbsoluteFill, interpolate} from 'remotion';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
import {pushCut} from '@remotion/transitions/push-cut';
import type {TransitionName} from './spec';
import {clamp, EASE} from './motion';

type Props = {kind: TransitionName};

/**
 * Scenes are transparent over a shared background, so a naive crossfade
 * double-exposes the text. These transitions "dip through the background":
 * the old scene leaves in the first ~60%, the new one arrives in the last ~60%,
 * each with its own spatial gesture.
 */
const Through: React.FC<TransitionPresentationComponentProps<Props>> = ({
	children,
	presentationDirection,
	presentationProgress: p,
	passedProps,
}) => {
	const exiting = presentationDirection === 'exiting';
	const t = exiting
		? interpolate(p, [0, 0.62], [0, 1], {...clamp, easing: EASE.in})
		: interpolate(p, [0.38, 1], [0, 1], {...clamp, easing: EASE.out});
	const k = exiting ? t : 1 - t; // 0 = fully present, 1 = gone
	let transform = '';
	let clipPath: string | undefined;
	switch (passedProps.kind) {
		case 'slide':
			transform = `translateX(${exiting ? -k * 140 : k * 140}px)`;
			break;
		case 'rise':
			transform = `translateY(${exiting ? -k * 90 : k * 90}px)`;
			break;
		case 'zoom':
			transform = `scale(${exiting ? 1 + k * 0.28 : 1 - k * 0.14})`;
			break;
		case 'wipe':
			clipPath = exiting ? `inset(0 0 0 ${k * 100}%)` : `inset(0 ${k * 100}% 0 0)`;
			break;
		default:
			transform = `scale(${exiting ? 1 + k * 0.05 : 1 - k * 0.04})`;
	}
	const blur = passedProps.kind === 'wipe' ? 0 : k * 16;
	return (
		<AbsoluteFill
			style={{
				opacity: passedProps.kind === 'wipe' ? 1 : 1 - k,
				transform,
				filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
				clipPath,
			}}
		>
			{children}
		</AbsoluteFill>
	);
};

export const presentationFor = (kind: TransitionName | undefined): TransitionPresentation<Record<string, unknown>> => {
	if (kind === 'push') return pushCut({flashOpacity: 0.12}) as unknown as TransitionPresentation<Record<string, unknown>>;
	return {component: Through, props: {kind: kind === 'iris' || !kind ? 'dip' : kind}} as unknown as TransitionPresentation<
		Record<string, unknown>
	>;
};
