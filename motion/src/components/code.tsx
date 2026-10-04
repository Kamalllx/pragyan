import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import type {Visual} from '../spec';
import {alpha, useTheme, type Theme} from '../theme';
import {clamp, EASE, Reveal, useScene} from '../motion';
import {Body, Glass, Heading, Stage} from './ui';

type V<T extends Visual['type']> = Extract<Visual, {type: T}>;

const KW = new Set(
	'def class return if elif else for while in not and or import from as with try except finally raise lambda yield pass break continue None True False function const let var new this async await export default interface type extends implements public private static void int float double char bool boolean string struct enum switch case match fn mut pub use impl trait package func go defer select chan map range nil null undefined include using namespace template typename auto println print'.split(
		' ',
	),
);

type Tok = {t: string; c: 'kw' | 'str' | 'num' | 'com' | 'fn' | 'op' | 'tx'};
const tokenize = (line: string): Tok[] => {
	const out: Tok[] = [];
	const re = /(#.*$|\/\/.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`[^`]*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)(\s*\()?|([^\sA-Za-z0-9_]+)|(\s+)/g;
	let m: RegExpExecArray | null;
	while ((m = re.exec(line))) {
		if (m[1]) out.push({t: m[1], c: 'com'});
		else if (m[2]) out.push({t: m[2], c: 'str'});
		else if (m[3]) out.push({t: m[3], c: 'num'});
		else if (m[4]) {
			out.push({t: m[4], c: KW.has(m[4]) ? 'kw' : m[5] ? 'fn' : 'tx'});
			if (m[5]) out.push({t: m[5], c: 'op'});
		} else if (m[6]) out.push({t: m[6], c: 'op'});
		else if (m[7]) out.push({t: m[7], c: 'tx'});
	}
	return out;
};

const colorOf = (c: Tok['c'], th: Theme) =>
	({kw: th.accent2, str: th.good, num: th.accent, com: alpha(th.muted, 0.85), fn: th.accent, op: alpha(th.text, 0.55), tx: th.text})[c];

export const CodeScene: React.FC<{v: V<'code'>}> = ({v}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	const {duration} = useScene();
	const lines = v.code.replace(/\t/g, '    ').split('\n').slice(0, 22);
	const typeEnd = Math.min(duration * 0.55, 18 + lines.length * 7);
	const shown = interpolate(frame, [18, typeEnd], [0, lines.length], clamp);
	const hl = new Set(v.highlightLines ?? []);
	const hlP = interpolate(frame, [typeEnd + 6, typeEnd + 22], [0, 1], {...clamp, easing: EASE.out});
	const maxLine = Math.max(20, ...lines.map((l) => l.length));
	const panelW = v.heading || v.caption ? 1080 : 1560;
	const fs = Math.max(18, Math.min(lines.length > 16 ? 24 : lines.length > 11 ? 28 : 32, Math.floor((panelW - 140) / (maxLine * 0.61))));
	return (
		<Stage>
			<div style={{display: 'flex', gap: 70, height: '100%', alignItems: 'center'}}>
				{v.heading || v.caption ? (
					<div style={{flex: '0 0 460px', display: 'flex', flexDirection: 'column', gap: 30}}>
						{v.heading ? <Heading text={v.heading} size={60} eyebrow={v.language ?? 'code'} /> : null}
						{v.caption ? (
							<Reveal start={30}>
								<Body size={30} muted>
									{v.caption}
								</Body>
							</Reveal>
						) : null}
					</div>
				) : null}
				<Reveal start={6} y={40} scale={0.97} style={{flex: 1, minWidth: 0}}>
					<Glass style={{padding: 0, overflow: 'hidden', background: theme.dark ? 'rgba(8,9,14,0.75)' : 'rgba(255,255,255,0.75)'}}>
						<div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '18px 24px', borderBottom: `1px solid ${theme.border}`}}>
							{['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
								<div key={c} style={{width: 14, height: 14, borderRadius: 14, background: c, opacity: 0.85}} />
							))}
							<span style={{marginLeft: 18, fontFamily: theme.mono, fontSize: 20, color: theme.muted}}>{v.language ?? 'code'}</span>
						</div>
						<div style={{padding: '26px 0', fontFamily: theme.mono, fontSize: fs, lineHeight: 1.6}}>
							{lines.map((ln, i) => {
								const vis = interpolate(shown - i, [0, 1], [0, 1], clamp);
								const isHl = hl.has(i + 1);
								return (
									<div
										key={i}
										style={{
											display: 'flex',
											opacity: vis * (hl.size && !isHl ? 1 - 0.55 * hlP : 1),
											transform: `translateX(${(1 - vis) * 14}px)`,
											background: isHl ? alpha(theme.accent, 0.13 * hlP) : 'transparent',
											boxShadow: isHl ? `inset 3px 0 0 ${alpha(theme.accent, hlP)}` : 'none',
											padding: '0 28px',
										}}
									>
										<span style={{width: 50, color: alpha(theme.muted, 0.5), flexShrink: 0, textAlign: 'right', marginRight: 28}}>{i + 1}</span>
										<span style={{whiteSpace: 'pre'}}>
											{tokenize(ln).map((tk, j) => (
												<span key={j} style={{color: colorOf(tk.c, theme), fontStyle: tk.c === 'com' ? 'italic' : 'normal'}}>
													{tk.t}
												</span>
											))}
										</span>
									</div>
								);
							})}
						</div>
					</Glass>
				</Reveal>
			</div>
		</Stage>
	);
};
