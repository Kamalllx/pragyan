import '@fontsource-variable/inter';
import '@fontsource-variable/space-grotesk';
import '@fontsource-variable/jetbrains-mono';
import '@fontsource-variable/fraunces';
import '@fontsource-variable/fraunces/wght-italic.css';
import '@fontsource/instrument-serif';
import '@fontsource/instrument-serif/400-italic.css';
import 'katex/dist/katex.min.css';
import {continueRender, delayRender} from 'remotion';

/** Fonts are bundled locally (no CDN at render time). Block the first frame until they're decoded. */
const FAMILIES = [
	'400 40px "Inter Variable"',
	'600 40px "Inter Variable"',
	'600 40px "Space Grotesk Variable"',
	'400 40px "JetBrains Mono Variable"',
	'500 40px "Fraunces Variable"',
	'italic 400 40px "Fraunces Variable"',
	'400 40px "Instrument Serif"',
	'italic 400 40px "Instrument Serif"',
	'400 40px KaTeX_Main',
	'italic 400 40px KaTeX_Math',
	'400 40px KaTeX_Size1',
	'400 40px KaTeX_Size2',
];

if (typeof document !== 'undefined') {
	const handle = delayRender('Loading fonts');
	Promise.all(FAMILIES.map((f) => document.fonts.load(f).catch(() => null)))
		.then(() => document.fonts.ready)
		.finally(() => continueRender(handle));
}
