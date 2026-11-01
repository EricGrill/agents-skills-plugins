#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, extname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SKILL = join(ROOT, 'skills', 'taste-skill');
const COMMIT = '12af471f627f866411b4bd785b19646d3672784c';
const required = [
  'SKILL.md', 'README.md', 'LICENSE', 'UPSTREAM.md', 'SEVEN.md',
  'assets/app.css', 'assets/base.css', 'assets/base.js', 'assets/charts.js',
  'assets/scenes/stage.css', 'assets/scenes/stage.js',
  'evals/evals.json',
  'library/app.json', 'library/directions.json', 'library/heroes.json',
  'library/motions.json', 'library/palettes.json', 'library/photos.json',
  'library/sections.json', 'library/sites.json', 'library/type.json',
  'references/app-screens.md', 'references/colour.md', 'references/copy.md',
  'references/critique.md', 'references/imagery.md', 'references/layout.md',
  'references/motion.md', 'references/research.md', 'references/scenes.md',
  'references/tells.md', 'references/type.md',
  'scripts/assets.mjs', 'scripts/draw.mjs', 'scripts/inspect.mjs',
  'scripts/lint.mjs', 'scripts/scenes.mjs', 'scripts/lib/app-draw.mjs',
  'scripts/lib/cdp.mjs', 'scripts/lib/inspection-files.mjs',
  'scripts/lib/probe.mjs', 'scripts/lib/rules.mjs',
];
const walk = (dir) => readdirSync(dir).flatMap((name) => {
  const path = join(dir, name);
  return statSync(path).isDirectory() ? walk(path) : [path];
});
const run = (args, options = {}) => spawnSync(process.execPath, args, {
  cwd: ROOT,
  encoding: 'utf8',
  maxBuffer: 16 * 1024 * 1024,
  ...options,
});
const succeeded = (result, label) => {
  assert.equal(result.error, undefined, `${label}: ${result.error?.message}`);
  assert.equal(result.status, 0, `${label} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
};

for (const path of required) {
  assert.ok(existsSync(join(SKILL, path)), `missing companion resource: ${path}`);
  assert.ok(statSync(join(SKILL, path)).size > 0, `empty companion resource: ${path}`);
}

const source = readFileSync(join(SKILL, 'SKILL.md'), 'utf8');
const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
assert.ok(frontmatter, 'SKILL.md must start with YAML frontmatter');
assert.match(frontmatter[1], /^name: design-taste-frontend$/m, 'native skill name mismatch');
assert.match(frontmatter[1], /^description: >-\s*$/m, 'native skill description missing');
assert.ok(!/'disable-model-invocation'\s*:\s*true|'disableModelInvocation'\s*:\s*true/.test(frontmatter[1]), 'skill must remain model-invocable');
assert.match(source, /1440, 768 and 390|1440 \/ 768 \/ 390/, 'three-width inspection is not documented');
assert.ok(readFileSync(join(SKILL, 'UPSTREAM.md'), 'utf8').includes(COMMIT), 'immutable upstream commit missing');
assert.ok(readFileSync(join(SKILL, 'LICENSE'), 'utf8').includes('Copyright (c) 2026 Leonxlnx'), 'upstream license attribution missing');

const files = walk(SKILL);
const jsonFiles = files.filter((path) => extname(path) === '.json');
assert.ok(jsonFiles.length >= 10, 'bundled JSON resources are incomplete');
for (const path of jsonFiles) JSON.parse(readFileSync(path, 'utf8'));
const directions = JSON.parse(readFileSync(join(SKILL, 'library/directions.json'), 'utf8'));
const sites = JSON.parse(readFileSync(join(SKILL, 'library/sites.json'), 'utf8'));
const photos = JSON.parse(readFileSync(join(SKILL, 'library/photos.json'), 'utf8'));
assert.equal(directions.length, 20, 'art-direction library is incomplete');
assert.equal(sites.length, 202, 'studied-site reference library is incomplete');
assert.ok(Object.keys(photos.sets).length > 0, 'reference-image metadata is empty');
assert.ok(Object.values(photos.sets).every((set) => set.photos.length > 0), 'reference-image set is empty');

const textExtensions = new Set(['.md', '.json', '.js', '.mjs', '.css']);
const mojibake = /Ã[\u0080-¿]|Â[\u0080-¿]|â€|�/;
for (const path of files.filter((path) => textExtensions.has(extname(path)))) {
  assert.ok(!mojibake.test(readFileSync(path, 'utf8')), `possible text-encoding damage: ${relative(ROOT, path)}`);
}
for (const path of files.filter((path) => ['.js', '.mjs'].includes(extname(path)))) {
  succeeded(run(['--check', path]), `syntax check ${relative(ROOT, path)}`);
}

succeeded(run(['--test', 'tests/taste-skill/inspection-files.mjs', 'tests/taste-skill/profile-cleanup.mjs']), 'upstream unit tests');

const temporary = mkdtempSync(join(tmpdir(), 'taste-skill-package-'));
try {
  const nativeSkills = join(temporary, '.agents', 'skills');
  const installed = join(nativeSkills, 'design-taste-frontend');
  mkdirSync(nativeSkills, { recursive: true });
  symlinkSync(SKILL, installed, 'dir');
  assert.ok(existsSync(join(installed, 'SKILL.md')), 'native directory-form discovery cannot see SKILL.md');
  assert.equal(realpathSync(installed), realpathSync(SKILL), 'native installation does not preserve the complete package');
  for (const path of ['references/critique.md', 'library/photos.json', 'scripts/inspect.mjs', 'assets/base.css']) {
    assert.ok(existsSync(join(installed, path)), `native installation loses ${path}`);
  }

  const drawOut = join(temporary, 'draw');
  const draw = run([
    join(SKILL, 'scripts/draw.mjs'), '--sector', 'saas',
    '--brief', 'Native package smoke test', '--sections', 'features,cta,footer',
    '--seed', '3803', '--out', drawOut,
  ], { env: { ...process.env, TASTE_SKILL_HISTORY: join(temporary, 'history.json') } });
  succeeded(draw, 'seeded art-direction draw');
  const sheet = JSON.parse(readFileSync(join(drawOut, 'direction.json'), 'utf8'));
  assert.ok(sheet.direction?.id, 'draw did not use the direction library');
  assert.ok(sheet.hero?.id, 'draw did not use the hero library');
  assert.ok(sheet.type && sheet.palette, 'draw did not use type and palette libraries');
  assert.equal(sheet.sections.length, 3, 'draw did not use the section library');

  if (process.argv.includes('--browser')) {
    const fixture = join(temporary, 'index.html');
    writeFileSync(fixture, '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Package smoke</title><style>body{margin:0;background:#111;color:#eee;font:18px/1.5 system-ui}main{padding:48px;max-width:1100px;margin:auto}h1{font-size:64px;line-height:1;margin:0 0 32px}section{padding:80px 0}p{max-width:60ch}</style></head><body><main><h1>Native package smoke</h1><p>A local fixture for exercising the real-browser inspector and its three viewport reports.</p><section><h2>Companion resources</h2><p>The inspector measures this page and saves screenshots without downloading any asset.</p></section></main></body></html>');
    const inspectOut = join(temporary, 'inspect');
    const inspection = run([
      join(SKILL, 'scripts/inspect.mjs'), fixture,
      '--widths', '1440,768,390', '--out', inspectOut,
    ], { env: { ...process.env, TASTE_SKILL_TMP: temporary }, timeout: 120000 });
    assert.equal(inspection.error, undefined, `browser inspection: ${inspection.error?.message}`);
    assert.ok([0, 1].includes(inspection.status), `browser inspection could not run (${inspection.status})\n${inspection.stdout}\n${inspection.stderr}`);
    const reportPath = join(inspectOut, 'report.json');
    assert.ok(existsSync(reportPath), `browser inspection produced no report\n${inspection.stdout}\n${inspection.stderr}`);
    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    assert.deepEqual(report.viewports.map((viewport) => viewport.width), [1440, 768, 390], 'browser inspection did not cover all widths');
    for (const label of ['desktop', 'tablet', 'mobile']) {
      const screenshot = join(inspectOut, `${label}-fold.jpg`);
      assert.ok(existsSync(screenshot), `missing ${label} screenshot`);
      assert.ok(statSync(screenshot).size > 1000, `${label} screenshot is empty`);
    }
    console.log('ok - real-browser inspection produced desktop, tablet, and mobile screenshots');
  }
} finally {
  rmSync(temporary, { recursive: true, force: true });
}

console.log(`ok - ${required.length} packaged files, ${jsonFiles.length} JSON resources, native layout, unit tests, and art-direction draw validated at ${COMMIT}`);
