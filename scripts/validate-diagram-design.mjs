#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SKILL = join(ROOT, 'skills', 'diagram-design');
const COMMIT = '0cf73c3fcc56667ad91a9a04c439ac6ccfabc9d1';
const PYTHON = process.env.PYTHON || 'python3';
const LOCAL_FILES = new Set(['README.md', 'SEVEN.md', 'UPSTREAM.md']);
const required = [
  'SKILL.md', 'README.md', 'SEVEN.md', 'UPSTREAM.md', 'LICENSE', 'THIRD_PARTY_LICENSES.md',
  'references/style-guide.md', 'references/semantic-patterns.md', 'references/primitives-core.md',
  'references/layout-budget.md', 'references/output-spec.md', 'references/export.md',
  'assets/index.html', 'assets/icons.html', 'assets/template.html', 'assets/template-dark.html',
  'assets/template-full.html', 'assets/template-motion.html', 'assets/template-terminal.html',
  'scripts/drawio_extract.py', 'scripts/excalidraw_extract.py', 'scripts/mermaid_extract.py',
  'scripts/export_png.py', 'scripts/export_svg.py', 'scripts/self_check.py',
];
const walk = (dir) => readdirSync(dir).flatMap((name) => {
  const path = join(dir, name);
  return statSync(path).isDirectory() ? walk(path) : [path];
});
const runPython = (args) => spawnSync(PYTHON, args, {
  cwd: ROOT,
  encoding: 'utf8',
  maxBuffer: 16 * 1024 * 1024,
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
assert.match(frontmatter[1], /^name: diagram-design$/m, 'native skill name mismatch');
assert.match(frontmatter[1], /^description: .+$/m, 'native skill description missing');
assert.match(frontmatter[1], /^license: MIT$/m, 'upstream license metadata missing');
assert.ok(!/'disable-model-invocation'\s*:\s*true|'disableModelInvocation'\s*:\s*true/.test(frontmatter[1]), 'skill must remain model-invocable');
assert.ok(readFileSync(join(SKILL, 'UPSTREAM.md'), 'utf8').includes(COMMIT), 'immutable upstream commit missing');
assert.ok(readFileSync(join(SKILL, 'LICENSE'), 'utf8').includes('Copyright (c) 2025 Cathryn Lavery'), 'upstream license attribution missing');

const files = walk(SKILL);
const upstreamFiles = files.filter((path) => !LOCAL_FILES.has(relative(SKILL, path)));
assert.equal(upstreamFiles.length, 292, 'complete upstream skill, license, or third-party notices are missing');
const typeReferences = readdirSync(join(SKILL, 'references')).filter((name) => /^type-.+\.md$/.test(name)).sort();
assert.equal(typeReferences.length, 45, 'the 45 visual-type references are incomplete');
const smokeHtml = [];
for (const reference of typeReferences) {
  const type = reference.slice(5, -3);
  for (const suffix of ['', '-dark', '-full']) {
    const asset = join(SKILL, 'assets', `example-${type}${suffix}.html`);
    assert.ok(existsSync(asset), `missing ${suffix || 'light'} example for ${type}`);
    assert.ok(statSync(asset).size > 0, `empty ${suffix || 'light'} example for ${type}`);
  }
  smokeHtml.push(join(SKILL, 'assets', `example-${type}.html`));
}
for (const name of ['template.html', 'template-dark.html', 'template-full.html', 'template-motion.html', 'template-terminal.html']) {
  smokeHtml.push(join(SKILL, 'assets', name));
}

const markdownFiles = files.filter((path) => path.endsWith('.md'));
for (const file of markdownFiles) {
  const text = readFileSync(file, 'utf8');
  for (const match of text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const raw = match[1].trim();
    if (!raw || raw.startsWith('#') || /^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.startsWith('<')) continue;
    const target = decodeURIComponent(raw.split('#')[0].split(/\s+/)[0]);
    if (!target || target.startsWith('/')) continue;
    const resolved = resolve(dirname(file), target);
    assert.ok(resolved === SKILL || resolved.startsWith(`${SKILL}${sep}`), `link leaves skill package: ${relative(ROOT, file)} -> ${raw}`);
    assert.ok(existsSync(resolved), `broken companion link: ${relative(ROOT, file)} -> ${raw}`);
  }
}

succeeded(runPython(['-c', 'import ast, pathlib, sys; [ast.parse(pathlib.Path(name).read_text(encoding="utf-8"), filename=name) for name in sys.argv[1:]]', ...files.filter((path) => path.endsWith('.py'))]), 'Python syntax checks');

const temporary = mkdtempSync(join(tmpdir(), 'diagram-design-package-'));
try {
  const nativeSkills = join(temporary, '.agents', 'skills');
  const installed = join(nativeSkills, 'diagram-design');
  mkdirSync(nativeSkills, { recursive: true });
  symlinkSync(SKILL, installed, 'dir');
  assert.ok(existsSync(join(installed, 'SKILL.md')), 'native directory-form discovery cannot see SKILL.md');
  assert.equal(realpathSync(installed), realpathSync(SKILL), 'native installation does not preserve the complete package');
  assert.match(readFileSync(join(installed, 'references', 'type-architecture.md'), 'utf8'), /Architecture/, 'native install cannot load a type reference');
  assert.match(readFileSync(join(installed, 'references', 'style-guide.md'), 'utf8'), /Contrast/, 'native install cannot load the design system');
  assert.match(readFileSync(join(installed, 'assets', 'template.html'), 'utf8'), /<svg/, 'native install cannot load a template');

  for (const html of smokeHtml) {
    const installedHtml = join(installed, relative(SKILL, html));
    succeeded(runPython([join(installed, 'scripts', 'self_check.py'), installedHtml]), `self-check ${relative(SKILL, html)}`);
  }

  const exported = join(temporary, 'architecture.svg');
  succeeded(runPython([
    join(installed, 'scripts', 'export_svg.py'),
    join(installed, 'assets', 'example-architecture.html'),
    exported,
    '--system-fonts',
  ]), 'native SVG export smoke test');
  assert.ok(statSync(exported).size > 1000, 'SVG export is empty');
  succeeded(runPython(['-c', 'import sys, xml.etree.ElementTree as ET; root = ET.parse(sys.argv[1]).getroot(); assert root.tag.endswith("svg"); assert root.attrib.get("role") == "img"', exported]), 'exported SVG validation');
} finally {
  rmSync(temporary, { recursive: true, force: true });
}

console.log(`ok - ${upstreamFiles.length} upstream files, ${typeReferences.length} diagram types, ${smokeHtml.length} self-checks, native discovery, companion links, and SVG export validated at ${COMMIT}`);
