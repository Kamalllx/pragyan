import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import type {SceneSpec, Word} from './spec';
import {alpha, useTheme} from './theme';
import {clamp} from './motion';

type Placed = {scene: SceneSpec; start: number};

const PAGE = 7;

/** Group words into short readable pages, breaking early at sentence ends. */
const paginate = (words: Word[]) => {
	const pages: Word[][] = [];
	let cur: Word[] = [];
	for (const w of words) {
		cur.push(w);
		if (cur.length >= PAGE || (/[.!?;:]$/.test(w.w) && cur.length >= 3)) {
			pages.push(cur);
			cur = [];
		}
	}
	if (cur.length) pages.push(cur);
	return pages;
};

export const Captions: React.FC<{placed: Placed[]}> = ({placed}) => {
	const theme = useTheme();
	const frame = useCurrentFrame();
	let cur: Placed | undefined;
	for (const p of placed) if (frame >= p.start) cur = p;
	if (!cur?.scene.segments?.length) return null;
	const local = frame - cur.start;
	const seg = cur.scene.segments.find((s) => local >= s.start - 2 && local <= s.end + 6);
	if (!seg) return null;
	const words = seg.words?.length ? seg.words : null;
	let page: Word[] | null = null;
	if (words) {
		const pages = paginate(words);
		page = pages.find((pg) => local <= pg[pg.length - 1].e + 2) ?? pages[pages.length - 1];
	}
	const segIn = interpolate(local, [seg.start - 2, seg.start + 4], [0, 1], clamp);
	const segOut = interpolate(local, [seg.end, seg.end + 6], [1, 0], clamp);
	return (
		<AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', pointerEvents: 'none'}}>
			<div
				style={{
					position: 'absolute',
					left: 0,
					right: 0,
					bottom: 0,
					height: 260,
					background: `linear-gradient(to top, ${alpha(theme.dark ? '#000000' : theme.bg, theme.dark ? 0.55 : 0.75)}, transparent)`,
				}}
			/>
			<div
				style={{
					position: 'relative',
					marginBottom: 74,
					maxWidth: 1480,
					textAlign: 'center',
					fontFamily: theme.body,
					fontWeight: 560,
					fontSize: 42,
					lineHeight: 1.3,
					letterSpacing: '-0.01em',
					opacity: segIn * segOut,
					textShadow: theme.dark ? '0 2px 24px rgba(0,0,0,0.6)' : 'none',
				}}
			>
				{page
					? page.map((w, i) => {
							const said = local >= w.s;
							const now = local >= w.s && local < w.e + 1;
							return (
								<span
									key={i}
									style={{
										color: now ? theme.accent : said ? theme.text : alpha(theme.text, 0.38),
										display: 'inline-block',
										transform: `translateY(${now ? -2 : 0}px)`,
									}}
								>
									{w.w}
									{i < page!.length - 1 ? ' ' : ''}
								</span>
							);
						})
					: <span style={{color: theme.text}}>{seg.text}</span>}
			</div>
		</AbsoluteFill>
	);
};
