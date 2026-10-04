import React from 'react';
import {AbsoluteFill} from 'remotion';
import type {SceneSpec} from './spec';
import {SceneContext} from './motion';
import {DefinitionScene, KineticScene, QuoteScene, SummaryScene, TitleScene} from './components/text';
import {BulletsScene, Cards3dScene, StepsScene, TimelineScene} from './components/lists';
import {ChartScene, ComparisonScene, StatsScene} from './components/data';
import {EquationScene} from './components/math';
import {DiagramScene} from './components/diagram';
import {CodeScene} from './components/code';
import {ImageScene, ManimScene} from './components/media';
import {Orbit3dScene} from './components/orbit3d';
import {QuizScene} from './components/quiz';

const Visual: React.FC<{scene: SceneSpec}> = ({scene}) => {
	const v = scene.visual;
	switch (v.type) {
		case 'title':
			return <TitleScene v={v} />;
		case 'kinetic':
			return <KineticScene v={v} />;
		case 'bullets':
			return <BulletsScene v={v} />;
		case 'definition':
			return <DefinitionScene v={v} />;
		case 'equation':
			return <EquationScene v={v} />;
		case 'steps':
			return <StepsScene v={v} />;
		case 'diagram':
			return <DiagramScene v={v} />;
		case 'comparison':
			return <ComparisonScene v={v} />;
		case 'stats':
			return <StatsScene v={v} />;
		case 'chart':
			return <ChartScene v={v} />;
		case 'code':
			return <CodeScene v={v} />;
		case 'quote':
			return <QuoteScene v={v} />;
		case 'image':
			return <ImageScene v={v} />;
		case 'timeline':
			return <TimelineScene v={v} />;
		case 'orbit3d':
			return <Orbit3dScene v={v} />;
		case 'cards3d':
			return <Cards3dScene v={v} />;
		case 'manim':
			return <ManimScene v={v} />;
		case 'summary':
			return <SummaryScene v={v} />;
		case 'quiz':
			return <QuizScene v={v} />;
		default:
			return null;
	}
};

export const SceneRenderer: React.FC<{scene: SceneSpec}> = ({scene}) => (
	<SceneContext.Provider value={{scene, duration: scene.durationInFrames}}>
		<AbsoluteFill>
			<Visual scene={scene} />
		</AbsoluteFill>
	</SceneContext.Provider>
);
