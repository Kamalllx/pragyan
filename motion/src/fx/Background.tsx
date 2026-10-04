import React, {useLayoutEffect, useMemo, useRef, useState} from 'react';
import {AbsoluteFill, interpolate, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {noise2D, noise3D} from '@remotion/noise';
import type {BackgroundName} from '../spec';
import {alpha, useTheme, type Theme} from '../theme';

/* ------------------------------------------------------------------ */
/* GLSL: domain-warped fbm — slow, living, never repeating.             */
/* ------------------------------------------------------------------ */
const VERT = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;
const FRAG = `
precision highp float;
uniform vec2 uRes; uniform float uTime; uniform vec3 uBg; uniform vec3 uA; uniform vec3 uB; uniform float uLight;
float hash(vec2 p){ p = fract(p*vec2(123.34, 456.21)); p += dot(p, p+45.32); return fract(p.x*p.y); }
float noise(vec2 p){ vec2 i=floor(p), f=fract(p); vec2 u=f*f*(3.0-2.0*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),u.x), mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),u.x), u.y); }
float fbm(vec2 p){ float v=0.0, a=0.5; mat2 m=mat2(1.6,1.2,-1.2,1.6);
  for(int i=0;i<5;i++){ v+=a*noise(p); p=m*p; a*=0.5; } return v; }
void main(){
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = (uv - 0.5) * vec2(uRes.x/uRes.y, 1.0) * 1.7;
  float t = uTime * 0.035;
  vec2 q = vec2(fbm(p + vec2(0.0, t)), fbm(p + vec2(5.2, 1.3) - t));
  vec2 r = vec2(fbm(p + 3.8*q + vec2(1.7, 9.2) + 1.4*t), fbm(p + 3.8*q + vec2(8.3, 2.8) - 1.1*t));
  float f = fbm(p + 3.2*r);
  vec3 col = uBg;
  float ka = smoothstep(0.42, 1.05, f) * mix(0.42, 0.22, uLight);
  float kb = smoothstep(0.62, 1.25, length(q) * f * 1.6) * mix(0.30, 0.16, uLight);
  col = mix(col, uA, ka);
  col = mix(col, uB, kb);
  // horizon glow, low in frame
  col += uA * 0.06 * smoothstep(0.9, 0.0, uv.y) * (1.0 - uLight);
  float v = smoothstep(1.3, 0.2, length((uv - 0.5) * vec2(1.25, 1.6)));
  col *= mix(mix(0.5, 0.92, uLight), 1.0, v);
  gl_FragColor = vec4(col, 1.0);
}`;

const hexToVec = (hex: string): [number, number, number] => {
	const n = parseInt(hex.replace('#', '').slice(0, 6), 16);
	return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
};

const ShaderBackground: React.FC<{theme: Theme}> = ({theme}) => {
	const frame = useCurrentFrame();
	const {width, height, fps} = useVideoConfig();
	const ref = useRef<HTMLCanvasElement>(null);
	const state = useRef<{gl: WebGLRenderingContext; u: Record<string, WebGLUniformLocation | null>} | null>(null);
	const [failed, setFailed] = useState(false);
	// Half resolution: the image is soft by design, and it halves the GPU cost.
	const W = Math.round(width / 2);
	const H = Math.round(height / 2);

	useLayoutEffect(() => {
		const canvas = ref.current;
		if (!canvas) return;
		const gl = canvas.getContext('webgl', {preserveDrawingBuffer: true, antialias: false});
		if (!gl) {
			setFailed(true);
			return;
		}
		const sh = (type: number, src: string) => {
			const s = gl.createShader(type)!;
			gl.shaderSource(s, src);
			gl.compileShader(s);
			return s;
		};
		const prog = gl.createProgram()!;
		gl.attachShader(prog, sh(gl.VERTEX_SHADER, VERT));
		gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
		gl.linkProgram(prog);
		if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
			setFailed(true);
			return;
		}
		gl.useProgram(prog);
		const buf = gl.createBuffer();
		gl.bindBuffer(gl.ARRAY_BUFFER, buf);
		gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
		const loc = gl.getAttribLocation(prog, 'p');
		gl.enableVertexAttribArray(loc);
		gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
		const u = Object.fromEntries(
			['uRes', 'uTime', 'uBg', 'uA', 'uB', 'uLight'].map((k) => [k, gl.getUniformLocation(prog, k)]),
		);
		state.current = {gl, u};
	}, []);

	useLayoutEffect(() => {
		const s = state.current;
		if (!s) return;
		const {gl, u} = s;
		gl.viewport(0, 0, W, H);
		gl.uniform2f(u.uRes, W, H);
		gl.uniform1f(u.uTime, frame / fps);
		gl.uniform3fv(u.uBg, hexToVec(theme.bg));
		gl.uniform3fv(u.uA, hexToVec(theme.accent));
		gl.uniform3fv(u.uB, hexToVec(theme.accent2));
		gl.uniform1f(u.uLight, theme.dark ? 0 : 1);
		gl.drawArrays(gl.TRIANGLES, 0, 6);
	}, [frame, fps, W, H, theme]);

	if (failed) return <AuroraBackground theme={theme} />;
	return <canvas ref={ref} width={W} height={H} style={{width: '100%', height: '100%', position: 'absolute', inset: 0}} />;
};

/* ------------------------------------------------------------------ */
/* CSS fallbacks / alternatives                                          */
/* ------------------------------------------------------------------ */
const AuroraBackground: React.FC<{theme: Theme}> = ({theme}) => {
	const frame = useCurrentFrame();
	const blobs = [
		{c: theme.accent, x: 0.2, y: 0.25, s: 0.75, a: theme.dark ? 0.28 : 0.16},
		{c: theme.accent2, x: 0.8, y: 0.7, s: 0.65, a: theme.dark ? 0.2 : 0.12},
		{c: theme.accent, x: 0.65, y: 0.15, s: 0.45, a: theme.dark ? 0.14 : 0.08},
	];
	return (
		<AbsoluteFill style={{background: theme.bg, overflow: 'hidden'}}>
			{blobs.map((b, i) => {
				const dx = noise2D(`ax${i}`, frame / 300, 0) * 0.12;
				const dy = noise2D(`ay${i}`, 0, frame / 300) * 0.1;
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: `${(b.x + dx) * 100}%`,
							top: `${(b.y + dy) * 100}%`,
							width: `${b.s * 100}vw`,
							height: `${b.s * 100}vw`,
							transform: 'translate(-50%,-50%)',
							background: `radial-gradient(closest-side, ${alpha(b.c, b.a)}, transparent)`,
						}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

const GridBackground: React.FC<{theme: Theme}> = ({theme}) => {
	const frame = useCurrentFrame();
	const offset = (frame * 0.9) % 80;
	return (
		<AbsoluteFill style={{background: theme.bg, overflow: 'hidden', perspective: 900}}>
			<AuroraBackground theme={theme} />
			<div
				style={{
					position: 'absolute',
					left: '-50%',
					right: '-50%',
					top: '48%',
					height: '120%',
					transform: 'rotateX(74deg)',
					transformOrigin: 'top center',
					backgroundImage: `linear-gradient(${alpha(theme.text, 0.09)} 1px, transparent 1px), linear-gradient(90deg, ${alpha(theme.text, 0.09)} 1px, transparent 1px)`,
					backgroundSize: '80px 80px',
					backgroundPosition: `0 ${offset}px`,
					maskImage: 'linear-gradient(to bottom, transparent, black 25%, black 50%, transparent)',
				}}
			/>
		</AbsoluteFill>
	);
};

const ParticleField: React.FC<{theme: Theme; stars?: boolean}> = ({theme, stars}) => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const count = stars ? 220 : 90;
	const pts = useMemo(
		() =>
			Array.from({length: count}, (_, i) => ({
				x: random(`px${i}`) * width,
				y: random(`py${i}`) * height,
				z: 0.2 + random(`pz${i}`) * 0.8,
				tw: random(`pt${i}`) * Math.PI * 2,
			})),
		[count, width, height],
	);
	return (
		<AbsoluteFill style={{background: theme.bg}}>
			<AuroraBackground theme={theme} />
			<svg width={width} height={height} style={{position: 'absolute', inset: 0}}>
				{pts.map((p, i) => {
					const drift = stars ? frame * 0.08 * p.z : frame * 0.35 * p.z;
					const x = (p.x + (stars ? drift : noise3D('n', p.x / 400, p.y / 400, frame / 200) * 30)) % width;
					const y = (p.y - (stars ? 0 : drift) + height) % height;
					const tw = 0.45 + 0.55 * Math.sin(frame / 18 + p.tw);
					return (
						<circle
							key={i}
							cx={x}
							cy={y}
							r={(stars ? 1.1 : 1.8) * p.z}
							fill={i % 7 === 0 ? theme.accent : theme.text}
							opacity={(stars ? 0.7 : 0.35) * p.z * tw}
						/>
					);
				})}
			</svg>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* Finishing: grain + vignette — the difference between "web page"     */
/* and "film".                                                          */
/* ------------------------------------------------------------------ */
let grainUrl: string | null = null;
const getGrain = () => {
	if (grainUrl || typeof document === 'undefined') return grainUrl;
	const c = document.createElement('canvas');
	c.width = c.height = 256;
	const ctx = c.getContext('2d')!;
	const img = ctx.createImageData(256, 256);
	for (let i = 0; i < img.data.length; i += 4) {
		const v = Math.floor(random(`g${i}`) * 255);
		img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
		img.data[i + 3] = 255;
	}
	ctx.putImageData(img, 0, 0);
	grainUrl = c.toDataURL();
	return grainUrl;
};

export const Grain: React.FC<{opacity?: number}> = ({opacity}) => {
	const frame = useCurrentFrame();
	const theme = useTheme();
	const url = getGrain();
	if (!url) return null;
	const ox = Math.floor(random(`gx${frame % 12}`) * 256);
	const oy = Math.floor(random(`gy${frame % 12}`) * 256);
	return (
		<AbsoluteFill
			style={{
				backgroundImage: `url(${url})`,
				backgroundPosition: `${ox}px ${oy}px`,
				opacity: opacity ?? (theme.dark ? 0.055 : 0.07),
				mixBlendMode: theme.dark ? 'overlay' : 'multiply',
				pointerEvents: 'none',
			}}
		/>
	);
};

export const Vignette: React.FC = () => {
	const theme = useTheme();
	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(ellipse 75% 70% at 50% 45%, transparent 55%, ${alpha(theme.dark ? '#000000' : '#5a4a32', theme.dark ? 0.55 : 0.14)} 100%)`,
				pointerEvents: 'none',
			}}
		/>
	);
};

export const Background: React.FC<{kind: BackgroundName}> = ({kind}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const fadeIn = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
	let inner: React.ReactNode;
	switch (kind) {
		case 'shader':
			inner = <ShaderBackground theme={theme} />;
			break;
		case 'grid':
			inner = <GridBackground theme={theme} />;
			break;
		case 'particles':
			inner = <ParticleField theme={theme} />;
			break;
		case 'stars':
			inner = <ParticleField theme={theme} stars />;
			break;
		case 'aurora':
		case 'mesh':
			inner = <AuroraBackground theme={theme} />;
			break;
		default:
			inner = null;
	}
	return (
		<AbsoluteFill style={{background: theme.bg}}>
			<AbsoluteFill style={{opacity: fadeIn}}>{inner}</AbsoluteFill>
		</AbsoluteFill>
	);
};
