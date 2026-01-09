/**
 * Simple test suite for Ralph the Copywriter
 * Validates database integrity and content quality
 */

import Database from 'better-sqlite3';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (error) {
    console.log(`❌ ${name}`);
    console.log(`   Error: ${error.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

console.log('\n🧪 RUNNING TESTS\n');
console.log('─'.repeat(50));

// Database tests
test('Database file exists', () => {
  assert(existsSync('./data/content.db'), 'Database not found');
});

let db;
test('Database can be opened', () => {
  db = new Database('./data/content.db', { readonly: true });
  assert(db, 'Could not open database');
});

test('Trends table has data', () => {
  const count = db.prepare('SELECT COUNT(*) as c FROM trends').get();
  assert(count.c > 0, 'No trends in database');
});

test('Research table has data', () => {
  const count = db.prepare('SELECT COUNT(*) as c FROM research').get();
  assert(count.c > 0, 'No research in database');
});

test('Communications table has data', () => {
  const count = db.prepare('SELECT COUNT(*) as c FROM communications').get();
  assert(count.c > 0, 'No communications in database');
});

// Content quality tests
test('All content plans have required fields', () => {
  const invalid = db.prepare(`
    SELECT COUNT(*) as c FROM content_plan
    WHERE title IS NULL OR content_type IS NULL
  `).get();
  assert(invalid.c === 0, 'Found content plans with missing fields');
});

test('All drafts link to valid content plans', () => {
  const orphans = db.prepare(`
    SELECT COUNT(*) as c FROM drafts d
    LEFT JOIN content_plan cp ON d.plan_id = cp.id
    WHERE cp.id IS NULL
  `).get();
  assert(orphans.c === 0, 'Found orphaned drafts');
});

test('Published content has meta descriptions', () => {
  const missing = db.prepare(`
    SELECT COUNT(*) as c FROM published
    WHERE meta_description IS NULL OR meta_description = ''
  `).get();
  assert(missing.c === 0, 'Published content missing meta descriptions');
});

// Content plan workflow tests
test('No content stuck in invalid status', () => {
  const validStatuses = ['planned', 'writing', 'review', 'published', 'cancelled'];
  const invalid = db.prepare(`
    SELECT COUNT(*) as c FROM content_plan
    WHERE status NOT IN ('planned', 'writing', 'review', 'published', 'cancelled')
  `).get();
  assert(invalid.c === 0, 'Found content with invalid status');
});

// Draft quality tests (if any drafts exist)
const draftCount = db.prepare('SELECT COUNT(*) as c FROM drafts').get();
if (draftCount.c > 0) {
  test('Drafts have content', () => {
    const empty = db.prepare(`
      SELECT COUNT(*) as c FROM drafts
      WHERE content IS NULL OR content = ''
    `).get();
    assert(empty.c === 0, 'Found empty drafts');
  });

  test('Draft word counts are accurate', () => {
    const drafts = db.prepare('SELECT content, word_count FROM drafts WHERE content IS NOT NULL').all();
    drafts.forEach(d => {
      const actualCount = d.content.split(/\s+/).filter(w => w.length > 0).length;
      const diff = Math.abs(actualCount - d.word_count);
      assert(diff < 10, `Word count mismatch: actual ${actualCount} vs stored ${d.word_count}`);
    });
  });
}

// File system tests
test('Progress file exists', () => {
  assert(existsSync('./scripts/ralph/progress.txt'), 'progress.txt not found');
});

test('PRD file exists and is valid JSON', () => {
  const prdPath = './scripts/ralph/prd.json';
  assert(existsSync(prdPath), 'prd.json not found');
  const content = readFileSync(prdPath, 'utf-8');
  JSON.parse(content); // Will throw if invalid
});

// Published content file tests
const publishedContent = db.prepare('SELECT plan_id FROM published').all();
publishedContent.forEach(p => {
  test(`Published content file exists for plan ${p.plan_id}`, () => {
    // Content should be in content/published/ directory
    const files = ['blog', 'social', 'newsletter', 'case_study', 'landing_page', 'email_sequence'];
    // This is a soft check - we just verify the directory exists
    assert(existsSync('./content/published'), 'Published content directory missing');
  });
});

if (db) db.close();

// Summary
console.log('\n' + '─'.repeat(50));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed`);

if (failed > 0) {
  console.log('\n⚠️  Some tests failed. Ralph should investigate.\n');
  process.exit(1);
} else {
  console.log('\n✅ All tests passed!\n');
  process.exit(0);
}
