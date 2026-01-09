import Database from 'better-sqlite3';

const db = new Database('./data/content.db', { readonly: true });

console.log('\n📊 CONTENT PIPELINE STATUS');
console.log('═'.repeat(50));

// Trends
const trendsActive = db.prepare('SELECT COUNT(*) as count FROM trends WHERE status = ?').get('active');
const trendsUsed = db.prepare('SELECT COUNT(*) as count FROM trends WHERE status = ?').get('used');
console.log(`\n🔥 TRENDS`);
console.log(`   Active: ${trendsActive.count} | Used: ${trendsUsed.count}`);

// Research
const researchAvailable = db.prepare('SELECT COUNT(*) as count FROM research WHERE status = ?').get('available');
const researchUsed = db.prepare('SELECT COUNT(*) as count FROM research WHERE status = ?').get('used');
console.log(`\n🔬 RESEARCH`);
console.log(`   Available: ${researchAvailable.count} | Used: ${researchUsed.count}`);

// Communications
const commsPending = db.prepare('SELECT COUNT(*) as count FROM communications WHERE status = ?').get('pending');
const commsAssigned = db.prepare('SELECT COUNT(*) as count FROM communications WHERE status = ?').get('assigned');
const commsCompleted = db.prepare('SELECT COUNT(*) as count FROM communications WHERE status = ?').get('completed');
console.log(`\n📢 COMMUNICATIONS`);
console.log(`   Pending: ${commsPending.count} | Assigned: ${commsAssigned.count} | Completed: ${commsCompleted.count}`);

// Content Plan
const planStatuses = db.prepare(`
  SELECT status, COUNT(*) as count
  FROM content_plan
  GROUP BY status
`).all();
console.log(`\n📝 CONTENT PLAN`);
if (planStatuses.length === 0) {
  console.log('   No content planned yet');
} else {
  planStatuses.forEach(s => console.log(`   ${s.status}: ${s.count}`));
}

// Drafts
const draftCount = db.prepare('SELECT COUNT(*) as count FROM drafts').get();
const latestDrafts = db.prepare(`
  SELECT d.id, cp.title, d.version, d.word_count, d.updated_at
  FROM drafts d
  JOIN content_plan cp ON d.plan_id = cp.id
  ORDER BY d.updated_at DESC
  LIMIT 3
`).all();
console.log(`\n✏️  DRAFTS (${draftCount.count} total)`);
if (latestDrafts.length > 0) {
  latestDrafts.forEach(d => {
    console.log(`   - "${d.title}" v${d.version} (${d.word_count} words)`);
  });
}

// Published
const publishedCount = db.prepare('SELECT COUNT(*) as count FROM published').get();
console.log(`\n✅ PUBLISHED: ${publishedCount.count} pieces`);

// Recent Activity
const recentLogs = db.prepare(`
  SELECT action, details, created_at
  FROM agent_log
  ORDER BY created_at DESC
  LIMIT 5
`).all();
console.log(`\n📋 RECENT ACTIVITY`);
if (recentLogs.length === 0) {
  console.log('   No activity yet');
} else {
  recentLogs.forEach(log => {
    const time = new Date(log.created_at).toLocaleString();
    console.log(`   [${time}] ${log.action}`);
  });
}

console.log('\n' + '═'.repeat(50));
db.close();
