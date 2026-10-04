import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import './fonts';
import {PragyanVideo, totalFrames} from './PragyanVideo';
import {SAMPLE} from './sample';
import type {VideoSpec} from './spec';
import {PragyanFilm, FILM_FRAMES} from './film/PragyanFilm';

const calc: CalculateMetadataFunction<VideoSpec> = ({props}) => ({
	durationInFrames: totalFrames(props),
	fps: props.meta.fps ?? 30,
	width: props.meta.width ?? 1920,
	height: props.meta.height ?? 1080,
});

export const Root: React.FC = () => (
	<>
		<Composition
			id="PragyanVideo"
			component={PragyanVideo as unknown as React.FC<Record<string, unknown>>}
			defaultProps={SAMPLE as unknown as Record<string, unknown>}
			calculateMetadata={calc as unknown as CalculateMetadataFunction<Record<string, unknown>>}
			durationInFrames={300}
			fps={30}
			width={1920}
			height={1080}
		/>
		<Composition id="PragyanFilm" component={PragyanFilm} durationInFrames={FILM_FRAMES} fps={30} width={1920} height={1080} />
	</>
);
