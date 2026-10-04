import React, {useMemo} from 'react';
import * as THREE from 'three';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme} from '../theme';
import {clamp, Reveal, SPRING, useActiveIndex, useCues} from '../motion';
import {Body} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

const CAM_POS = new THREE.Vector3(0, 1.1, 10);
const FOV = 38;
const TILT = 0.38;
const RADIUS = 4.1;

const satPos = (i: number, n: number, frame: number) => {
	const a = (i / n) * Math.PI * 2 + frame * 0.0065 - Math.PI / 2;
	const x = Math.cos(a) * RADIUS * 1.25;
	const z0 = Math.sin(a) * RADIUS;
	return new THREE.Vector3(x, -z0 * Math.sin(TILT), z0 * Math.cos(TILT));
};

const Core: React.FC<{accent: string; accent2: string; dark: boolean}> = ({accent, accent2, dark}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const p = spring({frame: frame - 4, fps, config: SPRING.heavy});
	return (
		<group scale={0.4 + 0.6 * p} rotation={[frame * 0.004, frame * 0.009, 0]}>
			<mesh>
				<icosahedronGeometry args={[1.35, 1]} />
				<meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={dark ? 0.55 : 0.25} roughness={0.35} metalness={0.4} flatShading />
			</mesh>
			<mesh scale={1.32}>
				<icosahedronGeometry args={[1.35, 1]} />
				<meshBasicMaterial color={accent2} wireframe transparent opacity={0.35} />
			</mesh>
		</group>
	);
};

const Ring: React.FC<{color: string}> = ({color}) => {
	const frame = useCurrentFrame();
	const geo = useMemo(() => {
		const pts: THREE.Vector3[] = [];
		for (let i = 0; i <= 160; i++) {
			const a = (i / 160) * Math.PI * 2;
			const z0 = Math.sin(a) * RADIUS;
			pts.push(new THREE.Vector3(Math.cos(a) * RADIUS * 1.25, -z0 * Math.sin(TILT), z0 * Math.cos(TILT)));
		}
		return new THREE.BufferGeometry().setFromPoints(pts);
	}, []);
	const o = interpolate(frame, [6, 40], [0, 0.35], clamp);
	return (
		// @ts-expect-error — R3F's <line> collides with the SVG <line> JSX type.
		<line geometry={geo}>
			<lineBasicMaterial color={color} transparent opacity={o} />
		</line>
	);
};

const Satellites: React.FC<{n: number; cues: number[]; active: number; accent: string; text: string}> = ({n, cues, active, accent, text}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<>
			{Array.from({length: n}, (_, i) => {
				const p = spring({frame: frame - cues[i], fps, config: SPRING.bouncy});
				const pos = satPos(i, n, frame);
				return (
					<mesh key={i} position={pos} scale={Math.max(0.0001, p) * (i === active ? 0.42 : 0.3)}>
						<sphereGeometry args={[1, 32, 32]} />
						<meshStandardMaterial color={i === active ? accent : text} emissive={i === active ? accent : text} emissiveIntensity={i === active ? 0.9 : 0.15} roughness={0.4} />
					</mesh>
				);
			})}
		</>
	);
};

export const Orbit3dScene: React.FC<{v: V<'orbit3d'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {width, height, fps} = useVideoConfig();
	const sats = v.satellites.slice(0, 7);
	const cues = useCues(sats.length, {first: 30});
	const active = useActiveIndex(cues);
	const cam = useMemo(() => {
		const c = new THREE.PerspectiveCamera(FOV, width / height, 0.1, 100);
		c.position.copy(CAM_POS);
		c.lookAt(0, 0, 0);
		c.updateMatrixWorld();
		return c;
	}, [width, height]);
	const centreP = spring({frame: frame - 10, fps, config: SPRING.soft});
	return (
		<AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					left: '50%',
					top: '48%',
					width: 900,
					height: 900,
					transform: 'translate(-50%,-50%)',
					background: `radial-gradient(closest-side, ${alpha(theme.accent, theme.dark ? 0.22 : 0.15)}, transparent)`,
				}}
			/>
			<AbsoluteFill style={{transform: 'translateY(-70px) scale(0.9)'}}>
			<ThreeCanvas width={width} height={height} camera={{fov: FOV, position: [CAM_POS.x, CAM_POS.y, CAM_POS.z]}} gl={{antialias: true, alpha: true}}>
				<ambientLight intensity={0.5} />
				<pointLight position={[6, 6, 8]} intensity={120} color={'#ffffff'} />
				<pointLight position={[-6, -3, 4]} intensity={60} color={theme.accent2} />
				<Ring color={theme.text} />
				<Core accent={theme.accent} accent2={theme.accent2} dark={theme.dark} />
				<Satellites n={sats.length} cues={cues} active={active} accent={theme.accent} text={theme.text} />
			</ThreeCanvas>
			{/* Labels projected from 3D into screen space so type stays crisp. */}
						{sats.map((s, i) => {
				const p3 = satPos(i, sats.length, frame).project(cam);
				const x = ((p3.x + 1) / 2) * width;
				const y = ((1 - p3.y) / 2) * height;
				const depth = satPos(i, sats.length, frame).z;
				const p = spring({frame: frame - cues[i] - 3, fps, config: SPRING.snappy});
				const front = interpolate(depth, [-RADIUS, RADIUS], [0.45, 1], clamp);
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: x,
							top: y - 64,
							transform: `translate(-50%, -50%) scale(${0.8 + 0.2 * front})`,
							opacity: p * front,
							fontFamily: theme.display,
							fontWeight: 560,
							fontSize: 30,
							color: i === active ? theme.accent : theme.text,
							whiteSpace: 'nowrap',
							padding: '8px 18px',
							borderRadius: 999,
							background: alpha(theme.bg, 0.55),
							border: `1px solid ${i === active ? alpha(theme.accent, 0.6) : theme.border}`,
							zIndex: depth > 0 ? 3 : 1,
						}}
					>
						{s}
					</div>
				);
			})}
			</AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					top: 90,
					textAlign: 'center',
					fontFamily: theme.display,
					fontWeight: theme.displayWeight,
					letterSpacing: theme.displayTracking,
					fontSize: 72,
					color: theme.text,
					opacity: centreP,
					transform: `translateY(${(1 - centreP) * 20}px)`,
				}}
			>
				{v.center}
			</div>
			{v.caption ? (
				<div style={{position: 'absolute', left: 0, right: 0, bottom: 215, textAlign: 'center'}}>
					<Reveal start={40}>
						<Body size={30} muted>
							{v.caption}
						</Body>
					</Reveal>
				</div>
			) : null}
		</AbsoluteFill>
	);
};
