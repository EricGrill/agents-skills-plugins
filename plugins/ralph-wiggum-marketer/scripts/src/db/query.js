/**
 * Database query utilities for Ralph the Copywriter
 * Usage: node src/db/query.js <command> [args]
 *
 * Commands:
 *   trends [active|used|all]     - List trends
 *   research [available|used]    - List research
 *   comms [pending|assigned]     - List communications
 *   plan [status]                - List content plan
 *   drafts [plan_id]             - List drafts
 *   published                    - List published content
 */

import Database from 'better-sqlite3';

const db = new Database('./data/content.db');
const command = process.argv[2];
const arg = process.argv[3];

function printTable(rows, title) {
  console.log(`\n${title}`);
  console.log('─'.repeat(60));
  if (rows.length === 0) {
    console.log('No results');
    return;
  }
  rows.forEach((row, i) => {
    console.log(`\n[${i + 1}] ID: ${row.id}`);
    Object.entries(row).forEach(([key, value]) => {
      if (key !== 'id') {
        // Truncate long values
        const display = String(value).length > 100
          ? String(value).substring(0, 100) + '...'
          : value;
        console.log(`    ${key}: ${display}`);
      }
    });
  });
}

switch (command) {
  case 'trends': {
    const status = arg || 'active';
    const query = status === 'all'
      ? 'SELECT * FROM trends ORDER BY relevance_score DESC'
      : 'SELECT * FROM trends WHERE status = ? ORDER BY relevance_score DESC';
    const rows = status === 'all' ? db.prepare(query).all() : db.prepare(query).all(status);
    printTable(rows, `🔥 TRENDS (${status})`);
    break;
  }

  case 'research': {
    const status = arg || 'available';
    const rows = db.prepare('SELECT id, title, summary, category, status FROM research WHERE status = ?').all(status);
    printTable(rows, `🔬 RESEARCH (${status})`);
    break;
  }

  case 'comms': {
    const status = arg || 'pending';
    const rows = db.prepare('SELECT id, type, title, priority, target_audience, status FROM communications WHERE status = ? ORDER BY priority').all(status);
    printTable(rows, `📢 COMMUNICATIONS (${status})`);
    break;
  }

  case 'plan': {
    const status = arg;
    const query = status
      ? 'SELECT * FROM content_plan WHERE status = ? ORDER BY priority'
      : 'SELECT * FROM content_plan ORDER BY status, priority';
    const rows = status ? db.prepare(query).all(status) : db.prepare(query).all();
    printTable(rows, `📝 CONTENT PLAN${status ? ` (${status})` : ''}`);
    break;
  }

  case 'drafts': {
    const planId = arg;
    const query = planId
      ? `SELECT d.*, cp.title as plan_title FROM drafts d
         JOIN content_plan cp ON d.plan_id = cp.id
         WHERE d.plan_id = ? ORDER BY d.version DESC`
      : `SELECT d.*, cp.title as plan_title FROM drafts d
         JOIN content_plan cp ON d.plan_id = cp.id
         ORDER BY d.updated_at DESC`;
    const rows = planId ? db.prepare(query).all(planId) : db.prepare(query).all();
    printTable(rows, `✏️  DRAFTS${planId ? ` (plan ${planId})` : ''}`);
    break;
  }

  case 'published': {
    const rows = db.prepare(`
      SELECT p.id, cp.title, p.meta_description, p.published_at
      FROM published p
      JOIN content_plan cp ON p.plan_id = cp.id
      ORDER BY p.published_at DESC
    `).all();
    printTable(rows, '✅ PUBLISHED CONTENT');
    break;
  }

  default:
    console.log(`
📚 Database Query Tool

Usage: node src/db/query.js <command> [args]

Commands:
  trends [active|used|all]     List trends
  research [available|used]    List research items
  comms [pending|assigned]     List communications
  plan [status]                List content plan items
  drafts [plan_id]             List drafts
  published                    List published content

Examples:
  node src/db/query.js trends active
  node src/db/query.js comms pending
  node src/db/query.js plan writing
`);
}

db.close();
