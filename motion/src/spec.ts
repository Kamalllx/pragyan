/**
 * The VideoSpec contract — the single source of truth shared between the
 * Python agents (pydantic mirror in backend/pragyan/spec.py) and the renderer.
 *
 * Small local models are good at *choosing and filling* well-shaped JSON and
 * bad at writing a whole motion system from scratch. So the LLM picks visuals
 * from this curated library, and all of the motion craft lives here.
 */

export type ThemeName = 'cosmos' | 'midnight' | 'chalk' | 'paper' | 'neon' | 'solar';
export type BackgroundName = 'shader' | 'aurora' | 'grid' | 'particles' | 'stars' | 'mesh' | 'plain';
export type TransitionName = 'dip' | 'slide' | 'rise' | 'zoom' | 'wipe' | 'iris' | 'push' | 'none';

export type Word = {w: string; s: number; e: number};
/** A narration segment, frames relative to the scene start. Segment 0 = scene intro, k = item k. */
export type Segment = {text: string; start: number; end: number; words?: Word[]};

export type Visual =
	| {type: 'title'; eyebrow?: string; title: string; subtitle?: string}
	| {type: 'kinetic'; lines: string[]; emphasis?: string[]}
	| {type: 'bullets'; heading: string; items: {title: string; detail?: string}[]}
	| {type: 'definition'; term: string; definition: string; analogy?: string}
	| {type: 'equation'; heading?: string; steps: {latex: string; note?: string}[]}
	| {type: 'steps'; heading: string; steps: {title: string; detail?: string; latex?: string}[]; answer?: string}
	| {
			type: 'diagram';
			heading?: string;
			nodes: {id: string; label: string; sub?: string}[];
			edges: {from: string; to: string; label?: string}[];
			direction?: 'LR' | 'TB';
	  }
	| {
			type: 'comparison';
			heading?: string;
			left: {title: string; points: string[]};
			right: {title: string; points: string[]};
			verdict?: string;
	  }
	| {
			type: 'stats';
			heading?: string;
			stats: {value: number; prefix?: string; suffix?: string; label: string; decimals?: number}[];
	  }
	| {
			type: 'chart';
			heading?: string;
			kind: 'bar' | 'line';
			labels: string[];
			values: number[];
			unit?: string;
			caption?: string;
	  }
	| {type: 'code'; heading?: string; language?: string; code: string; highlightLines?: number[]; caption?: string}
	| {type: 'quote'; text: string; attribution?: string}
	| {type: 'image'; src: string; caption?: string; annotations?: {x: number; y: number; label: string}[]}
	| {type: 'timeline'; heading?: string; events: {date: string; title: string; detail?: string}[]}
	| {type: 'orbit3d'; center: string; satellites: string[]; caption?: string}
	| {type: 'cards3d'; heading?: string; cards: {title: string; body: string}[]}
	| {type: 'manim'; src: string; title?: string; caption?: string; transparent?: boolean}
	| {type: 'summary'; heading: string; takeaways: string[]}
	| {type: 'quiz'; question: string; options: string[]; answerIndex: number; explanation?: string};

export type VisualType = Visual['type'];

export type SceneSpec = {
	id: string;
	durationInFrames: number;
	/** Absolute URL or staticFile path of narration audio. */
	audio?: string | null;
	/** Frame (scene-relative) at which narration audio begins. */
	audioOffset?: number;
	segments?: Segment[];
	transition?: TransitionName;
	chapter?: string;
	visual: Visual;
};

export type VideoSpec = {
	meta: {
		title: string;
		fps: number;
		width: number;
		height: number;
		theme: ThemeName;
		background: BackgroundName;
		captions: boolean;
		watermark?: boolean;
		/** Narration language (ISO 639-1), drives built-in labels. */
		language?: string;
		accent?: string;
	};
	scenes: SceneSpec[];
	transitionFrames?: number;
	music?: {src: string; volume?: number} | null;
};
