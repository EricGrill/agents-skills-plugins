import assert from 'node:assert/strict';
import { closeSync, existsSync, mkdirSync, mkdtempSync, openSync, readFileSync, rmSync, utimesSync, writeFileSync } from 'node:fs';
import { hostname, tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';

const OWNER = 'taste-skill-owner.json';
// A pid that is certainly gone: a child that has already exited.
const deadPid = () => spawnSync(process.execPath, ['-e', '']).pid;
const profile = (base, name, owner) => {
  const p = join(base, name);
  mkdirSync(p);
  writeFileSync(join(p, 'sentinel'), 'preserve');
  if (owner !== undefined) writeFileSync(join(p, OWNER), typeof owner === 'string' ? owner : JSON.stringify(owner));
  return p;
};

// Run in a child so Browser.launch()'s exit/signal handlers cannot leak into the test runner.
if (process.argv[2] === '--fixture') {
  const { Browser } = await import('../../skills/taste-skill/scripts/lib/cdp.mjs');
  globalThis.WebSocket = class {
    constructor() { queueMicrotask(() => this.onopen?.()); }
    send(raw) {
      const { id } = JSON.parse(raw);
      queueMicrotask(() => this.onmessage?.({ data: JSON.stringify({ id, result: {} }) }));
    }
    close() {}
  };
  const base = process.env.TASTE_SKILL_TMP;
  const profiles = ['ad-chrome-open-lock', 'ad-chrome-no-lock'].map(name => profile(base, name));
  const gone = deadPid();
  const abandoned = profile(base, 'ad-chrome-abandoned', { host: hostname(), pid: gone, chrome: gone });
  let lock;
  let browser;
  try {
    lock = openSync(join(profiles[0], 'lockfile'), 'w+');
    for (const p of [...profiles, abandoned]) {
      const old = new Date(Date.now() - 10 * 60 * 1000);
      utimesSync(p, old, old);
    }
    browser = await Browser.launch();
    for (const p of profiles) {
      assert.ok(existsSync(join(p, 'sentinel')), 'launch deleted another profile');
    }
    assert.equal(existsSync(abandoned), false, 'launch kept a profile whose owners are gone');
    const owner = JSON.parse(readFileSync(join(browser.dir, OWNER), 'utf8'));
    assert.deepEqual(owner, { host: hostname(), pid: process.pid, chrome: browser.proc.pid }, 'launch did not claim its profile');
  } finally {
    if (browser) await browser.close();
    if (lock !== undefined) closeSync(lock);
  }
  assert.equal(existsSync(browser.dir), false, 'close left the owned profile behind');
} else {
  test('launch preserves older foreign profiles and close removes its own', {
    skip: process.platform === 'win32' && 'POSIX fake browser fixture',
  }, () => {
    const base = mkdtempSync(join(tmpdir(), 'taste-profile-test-'));
    try {
      const fakeChrome = join(base, 'fake-chrome');
      // No real browser, network, or existing user profile is accessed.
      writeFileSync(fakeChrome, '#!/bin/sh\nprintf "DevTools listening on ws://fixture\\n" >&2\nexec tail -f /dev/null\n', { mode: 0o755 });
      const result = spawnSync(process.execPath, [fileURLToPath(import.meta.url), '--fixture'], {
        env: { ...process.env, CHROME_PATH: fakeChrome, TASTE_SKILL_TMP: base },
        encoding: 'utf8',
        timeout: 15000,
      });
      assert.equal(result.error, undefined, result.error?.message);
      assert.equal(result.status, 0, result.stdout + result.stderr);
    } finally {
      rmSync(base, { recursive: true, force: true });
    }
  });

  test('sweep removes a profile only when its owner file says both processes are gone', async () => {
    const { sweepProfiles } = await import('../../skills/taste-skill/scripts/lib/cdp.mjs');
    const base = mkdtempSync(join(tmpdir(), 'taste-sweep-test-'));
    try {
      const gone = deadPid();
      const here = hostname();
      const abandoned = profile(base, 'ad-chrome-abandoned', { host: here, pid: gone, chrome: gone });
      const kept = [
        profile(base, 'ad-chrome-run-alive', { host: here, pid: process.pid, chrome: gone }),
        profile(base, 'ad-chrome-chrome-alive', { host: here, pid: gone, chrome: process.pid }),
        profile(base, 'ad-chrome-other-machine', { host: `${here}-elsewhere`, pid: gone, chrome: gone }),
        profile(base, 'ad-chrome-no-owner'),
        profile(base, 'ad-chrome-torn-owner', '{"host":'),
        profile(base, 'ad-chrome-bad-pid', { host: here, pid: 'x', chrome: gone }),
        profile(base, 'not-a-profile', { host: here, pid: gone, chrome: gone }),
      ];
      sweepProfiles(base);
      assert.equal(existsSync(abandoned), false, 'sweep kept a profile whose owners are gone');
      for (const p of kept) assert.ok(existsSync(join(p, 'sentinel')), `sweep removed ${p}`);
      sweepProfiles(join(base, 'missing')); // a missing base is not an error
    } finally {
      rmSync(base, { recursive: true, force: true });
    }
  });
}
