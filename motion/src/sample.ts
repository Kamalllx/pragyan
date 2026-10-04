import type {SceneSpec, Segment, VideoSpec, Visual} from './spec';

/** Fake narration timing so the gallery exercises cue-sync without audio. */
const segs = (n: number, dur: number): Segment[] =>
	Array.from({length: n}, (_, i) => {
		const start = 10 + Math.round(((dur - 40) * i) / n);
		const end = 10 + Math.round(((dur - 40) * (i + 1)) / n) - 4;
		const text = i === 0 ? 'This is the introduction of the scene being narrated now.' : `Here is point number ${i} explained in a few words.`;
		const words = text.split(' ');
		return {
			text,
			start,
			end,
			words: words.map((w, k) => ({w, s: start + Math.round(((end - start) * k) / words.length), e: start + Math.round(((end - start) * (k + 1)) / words.length)})),
		};
	});

const scene = (id: string, visual: Visual, dur: number, n: number, extra: Partial<SceneSpec> = {}): SceneSpec => ({
	id,
	durationInFrames: dur,
	segments: segs(n, dur),
	transition: 'dip',
	chapter: visual.type,
	visual,
	...extra,
});

export const SAMPLE: VideoSpec = {
	meta: {title: 'Pragyan gallery', fps: 30, width: 1920, height: 1080, theme: 'cosmos', background: 'shader', captions: true},
	scenes: [
		scene('s1', {type: 'title', eyebrow: 'Pragyan AI · Explainer', title: 'Why is the sky blue?', subtitle: 'Rayleigh scattering, from a single photon to the whole sky.'}, 150, 1),
		scene('s2', {type: 'kinetic', lines: ['Light is not one colour.', 'It is every colour,', 'travelling together.'], emphasis: ['every', 'together']}, 150, 4, {transition: 'rise'}),
		scene('s3', {type: 'definition', term: 'Rayleigh scattering', definition: 'The scattering of light by particles much smaller than its wavelength — stronger for shorter wavelengths.', analogy: 'Small pebbles bounce ripples more than they bounce ocean swells.'}, 180, 3),
		scene('s4', {type: 'equation', heading: 'Intensity falls with wavelength', steps: [{latex: 'I \\propto \\frac{1}{\\lambda^4}', note: 'the key relation'}, {latex: '\\frac{I_{blue}}{I_{red}} = \\left(\\frac{700}{450}\\right)^4', note: 'compare blue and red'}, {latex: '\\frac{I_{blue}}{I_{red}} \\approx 5.8', note: 'blue scatters ~6x more'}]}, 210, 4, {transition: 'zoom'}),
		scene('s5', {type: 'bullets', heading: 'What happens to sunlight', items: [{title: 'Enters the atmosphere', detail: 'A mix of all visible wavelengths.'}, {title: 'Hits N₂ and O₂ molecules', detail: 'Far smaller than the light’s wavelength.'}, {title: 'Blue scatters everywhere', detail: 'So blue reaches your eye from every direction.'}]}, 210, 4, {transition: 'slide'}),
		scene('s6', {type: 'diagram', heading: 'The path of a photon', nodes: [{id: 'sun', label: 'Sun', sub: 'white light'}, {id: 'atm', label: 'Atmosphere', sub: 'N₂ · O₂'}, {id: 'blue', label: 'Blue', sub: 'scattered'}, {id: 'red', label: 'Red', sub: 'passes through'}, {id: 'eye', label: 'Your eye'}], edges: [{from: 'sun', to: 'atm'}, {from: 'atm', to: 'blue', label: 'λ⁻⁴'}, {from: 'atm', to: 'red'}, {from: 'blue', to: 'eye'}]}, 240, 6),
		scene('s7', {type: 'stats', heading: 'By the numbers', stats: [{value: 5.8, suffix: '×', label: 'more blue scattering than red', decimals: 1}, {value: 450, suffix: ' nm', label: 'wavelength of blue light'}, {value: 100, suffix: ' km', label: 'thickness of the sky that matters'}]}, 180, 4),
		scene('s8', {type: 'chart', heading: 'Relative scattering by colour', kind: 'bar', labels: ['Violet', 'Blue', 'Green', 'Yellow', 'Red'], values: [9.4, 5.8, 3.4, 2.4, 1], unit: 'relative to red'}, 180, 1),
		scene('s9', {type: 'comparison', heading: 'Noon vs sunset', left: {title: 'Noon', points: ['Short path through air', 'Blue scattered toward you', 'Sky looks blue']}, right: {title: 'Sunset', points: ['Long path through air', 'Blue scattered away', 'Sky looks red-orange']}, verdict: 'Path length decides the colour.'}, 210, 4),
		scene('s10', {type: 'steps', heading: 'Solve: ratio for violet vs red', steps: [{title: 'Write the law', latex: 'I \\propto \\lambda^{-4}'}, {title: 'Plug wavelengths', detail: 'Violet 400 nm, red 700 nm', latex: '(700/400)^4'}, {title: 'Compute', latex: '1.75^4 \\approx 9.38'}], answer: 'Violet scatters about 9.4× more'}, 240, 5),
		scene('s11', {type: 'timeline', heading: 'Who figured it out', events: [{date: '1859', title: 'Tyndall', detail: 'Blue light from particles'}, {date: '1871', title: 'Rayleigh', detail: 'The λ⁻⁴ law'}, {date: '1910', title: 'Einstein', detail: 'Molecular fluctuations'}, {date: 'Today', title: 'Climate models', detail: 'Aerosols & haze'}]}, 220, 5),
		scene('s12', {type: 'orbit3d', center: 'Scattering', satellites: ['Rayleigh', 'Mie', 'Tyndall', 'Raman', 'Thomson'], caption: 'Different particles, different physics.'}, 210, 6, {transition: 'zoom'}),
		scene('s13', {type: 'cards3d', heading: 'Three ideas to keep', cards: [{title: 'Wavelength matters', body: 'Shorter waves scatter far more.'}, {title: 'Size matters', body: 'Tiny molecules favour blue.'}, {title: 'Path matters', body: 'Long paths strip the blue away.'}]}, 200, 4),
		scene('s14', {type: 'code', heading: 'Simulate it', language: 'python', code: 'import numpy as np\n\n# relative Rayleigh intensity\ndef intensity(wl_nm):\n    return (700 / wl_nm) ** 4\n\nfor c, wl in [("violet", 400), ("blue", 450), ("red", 700)]:\n    print(c, round(intensity(wl), 2))', highlightLines: [5], caption: 'Four lines of NumPy reproduce the λ⁻⁴ law.'}, 210, 1),
		scene('s15', {type: 'quote', text: 'The blue of the sky is the light of the sun, scattered by the air itself.', attribution: 'Lord Rayleigh, paraphrased'}, 150, 1),
		scene('s16', {type: 'quiz', question: 'Why are sunsets red?', options: ['Red light is brighter', 'Blue is scattered away over the long path', 'The sun cools down', 'Clouds absorb blue'], answerIndex: 1, explanation: 'The long path through air removes most blue before it reaches you.'}, 240, 3),
		scene('s17', {type: 'summary', heading: 'The sky, decoded', takeaways: ['Sunlight holds every colour', 'Air molecules scatter short waves most', 'Blue reaches you from every direction', 'Long sunset paths strip the blue away']}, 210, 5),
	],
};
