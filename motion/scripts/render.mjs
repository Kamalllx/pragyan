#!/usr/bin/env node
/**
 * Pragyan render CLI — called by the Python backend.
 *
 *   node scripts/render.mjs --props spec.json --out video.mp4 [--scale 0.6667]
 *   node scripts/render.mjs --props spec.json --stills 30,120 --still-dir frames/
 *   node scripts/render.mjs --composition PragyanFilm --out film.mp4
 *
 * Emits one JSON object per line on stdout so the caller can stream progress.
 * The webpack bundle is cached by a hash of src/, so only the first render pays for it.
 */
import {bundle} from '@remotion/bundler';
import {ensureBrowser, renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const emit = (o) => process.stdout.write(JSON.stringify(o) + '\n');

const args = Object.fromEntries(
	process.argv.slice(2).reduce((acc, a, i, arr) => {
		if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : 'true']);
		return acc;
	}, []),
);

const hashDir = (dir) => {
	const h = createHash('sha1');
	const walk = (d) => {
		for (const f of fs.readdirSync(d).sort()) {
			const p = path.join(d, f);
			const st = fs.statSync(p);
			if (st.isDirectory()) walk(p);
			else h.update(p + st.size + st.mtimeMs);
		}
	};
	walk(dir);
	h.update(fs.readFileSync(path.join(ROOT, 'package.json')));
	return h.digest('hex').slice(0, 12);
};

const getBundle = async () => {
	const key = hashDir(path.join(ROOT, 'src'));
	const outDir = path.join(ROOT, '.cache', `bundle-${key}`);
	if (fs.existsSync(path.join(outDir, 'index.html'))) {
		emit({stage: 'bundle', cached: true});
		return outDir;
	}
	emit({stage: 'bundle', cached: false});
	let last = -1;
	const serveUrl = await bundle({
		entryPoint: path.join(ROOT, 'src', 'index.ts'),
		outDir,
		onProgress: (p) => {
			if (p - last >= 10) {
				last = p;
				emit({stage: 'bundle', progress: p / 100});
			}
		},
	});
	return serveUrl;
};

const main = async () => {
	const compositionId = args.composition ?? 'PragyanVideo';
	const inputProps = args.props ? JSON.parse(fs.readFileSync(args.props, 'utf8')) : {};
	await ensureBrowser();
	const serveUrl = await getBundle();
	const chromiumOptions = {gl: args.gl ?? 'angle'};
	const composition = await selectComposition({serveUrl, id: compositionId, inputProps, chromiumOptions});
	emit({stage: 'composition', durationInFrames: composition.durationInFrames, fps: composition.fps});

	if (args.stills) {
		const dir = args['still-dir'] ?? path.join(os.tmpdir(), 'pragyan-stills');
		fs.mkdirSync(dir, {recursive: true});
		const frames = args.stills.split(',').map((x) => Math.min(composition.durationInFrames - 1, Math.max(0, parseInt(x, 10))));
		for (const frame of frames) {
			const output = path.join(dir, `frame-${String(frame).padStart(5, '0')}.jpg`);
			await renderStill({composition, serveUrl, output, frame, inputProps, chromiumOptions, imageFormat: 'jpeg', jpegQuality: 88, scale: Number(args.scale ?? 1)});
			emit({stage: 'still', frame, output});
		}
		emit({done: true});
		return;
	}

	const out = path.resolve(args.out ?? 'out.mp4');
	fs.mkdirSync(path.dirname(out), {recursive: true});
	let lastP = -1;
	await renderMedia({
		composition,
		serveUrl,
		codec: 'h264',
		outputLocation: out,
		inputProps,
		chromiumOptions,
		scale: Number(args.scale ?? 1),
		crf: Number(args.crf ?? 18),
		concurrency: args.concurrency ? Number(args.concurrency) : Math.max(1, Math.floor(os.cpus().length / 2)),
		imageFormat: 'jpeg',
		jpegQuality: 92,
		timeoutInMilliseconds: 120000,
		onProgress: ({progress, renderedFrames, encodedFrames, stitchStage}) => {
			if (progress - lastP >= 0.01 || progress === 1) {
				lastP = progress;
				emit({stage: 'render', progress, renderedFrames, encodedFrames, stitchStage});
			}
		},
	});
	emit({done: true, out});
};

main().catch((e) => {
	emit({error: String(e?.stack ?? e)});
	process.exit(1);
});
