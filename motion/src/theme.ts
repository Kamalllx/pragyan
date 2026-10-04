import {createContext, useContext} from 'react';
import type {ThemeName} from './spec';

export type Theme = {
	name: ThemeName;
	dark: boolean;
	bg: string;
	bg2: string;
	surface: string;
	border: string;
	text: string;
	muted: string;
	accent: string;
	accent2: string;
	good: string;
	bad: string;
	display: string;
	serif: string;
	body: string;
	mono: string;
	/** Display weight + tracking so each theme has its own typographic voice. */
	displayWeight: number;
	displayTracking: string;
};

const SANS = '"Inter Variable", "Inter", system-ui, sans-serif';
const GROTESK = '"Space Grotesk Variable", "Space Grotesk", system-ui, sans-serif';
const FRAUNCES = '"Fraunces Variable", "Fraunces", Georgia, serif';
const INSTRUMENT = '"Instrument Serif", Georgia, serif';
const MONO = '"JetBrains Mono Variable", "JetBrains Mono", ui-monospace, monospace';

export const THEMES: Record<ThemeName, Theme> = {
	// Pragyan house style: lunar regolith + saffron. A quiet nod to the Chandrayaan-3 rover.
	cosmos: {
		name: 'cosmos',
		dark: true,
		bg: '#08090D',
		bg2: '#12141C',
		surface: 'rgba(236,232,223,0.045)',
		border: 'rgba(236,232,223,0.12)',
		text: '#ECE8DF',
		muted: '#8D8A84',
		accent: '#E8A33D',
		accent2: '#8FB3FF',
		good: '#7FD6A4',
		bad: '#F07167',
		display: GROTESK,
		serif: INSTRUMENT,
		body: SANS,
		mono: MONO,
		displayWeight: 600,
		displayTracking: '-0.035em',
	},
	midnight: {
		name: 'midnight',
		dark: true,
		bg: '#06070C',
		bg2: '#0E1120',
		surface: 'rgba(255,255,255,0.045)',
		border: 'rgba(255,255,255,0.11)',
		text: '#EEF0F6',
		muted: '#8A8FA3',
		accent: '#7C9CFF',
		accent2: '#F5B971',
		good: '#6EE7B7',
		bad: '#FB7185',
		display: SANS,
		serif: INSTRUMENT,
		body: SANS,
		mono: MONO,
		displayWeight: 650,
		displayTracking: '-0.04em',
	},
	// Blackboard for maths — chalk white, chalk yellow.
	chalk: {
		name: 'chalk',
		dark: true,
		bg: '#18201D',
		bg2: '#202B27',
		surface: 'rgba(242,239,230,0.05)',
		border: 'rgba(242,239,230,0.14)',
		text: '#F2EFE6',
		muted: '#9AA59F',
		accent: '#F2C14E',
		accent2: '#7FD1B9',
		good: '#9BE38A',
		bad: '#F28B82',
		display: FRAUNCES,
		serif: FRAUNCES,
		body: SANS,
		mono: MONO,
		displayWeight: 560,
		displayTracking: '-0.02em',
	},
	// Warm editorial light mode.
	paper: {
		name: 'paper',
		dark: false,
		bg: '#F1ECE2',
		bg2: '#E7E0D2',
		surface: 'rgba(27,26,23,0.04)',
		border: 'rgba(27,26,23,0.14)',
		text: '#1B1A17',
		muted: '#6E685E',
		accent: '#D2491E',
		accent2: '#2B59C3',
		good: '#2E7D4F',
		bad: '#B3261E',
		display: INSTRUMENT,
		serif: INSTRUMENT,
		body: SANS,
		mono: MONO,
		displayWeight: 400,
		displayTracking: '-0.02em',
	},
	neon: {
		name: 'neon',
		dark: true,
		bg: '#040406',
		bg2: '#0B0B12',
		surface: 'rgba(255,255,255,0.04)',
		border: 'rgba(255,255,255,0.1)',
		text: '#F5F5F7',
		muted: '#85859A',
		accent: '#00E5C7',
		accent2: '#FF4D8D',
		good: '#00E5C7',
		bad: '#FF4D8D',
		display: GROTESK,
		serif: INSTRUMENT,
		body: SANS,
		mono: MONO,
		displayWeight: 650,
		displayTracking: '-0.045em',
	},
	solar: {
		name: 'solar',
		dark: true,
		bg: '#110B07',
		bg2: '#1C130C',
		surface: 'rgba(255,244,230,0.05)',
		border: 'rgba(255,244,230,0.12)',
		text: '#FFF4E6',
		muted: '#A8978A',
		accent: '#FF8A3D',
		accent2: '#FFD166',
		good: '#B8E986',
		bad: '#FF6B6B',
		display: FRAUNCES,
		serif: FRAUNCES,
		body: SANS,
		mono: MONO,
		displayWeight: 600,
		displayTracking: '-0.03em',
	},
};

export const getTheme = (name: ThemeName | undefined, accent?: string): Theme => {
	const base = THEMES[name ?? 'cosmos'] ?? THEMES.cosmos;
	return accent ? {...base, accent} : base;
};

export const ThemeContext = createContext<Theme>(THEMES.cosmos);
export const useTheme = () => useContext(ThemeContext);

/** Hex -> rgba helper for glows and tints. */
export const alpha = (hex: string, a: number) => {
	if (!hex.startsWith('#')) return hex;
	const h = hex.length === 4 ? hex.replace(/#(.)(.)(.)/, '#$1$1$2$2$3$3') : hex;
	const n = parseInt(h.slice(1, 7), 16);
	return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};
