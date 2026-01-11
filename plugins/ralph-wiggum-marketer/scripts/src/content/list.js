/**
 * List all available content sources for planning
 * Ralph uses this to see what's available to write about
 */

import Database from 'better-sqlite3';

const db = new Database('./data/content.db', { readonly: true });

console.log('\n🎯 AVAILABLE CONTENT SOURCES FOR RALPH');
console.log('═'.repeat(70));

// High priority communications first
console.log('\n📢 PENDING COMMUNICATIONS (by priority)');
console.log('─'.repeat(70));
const comms = db.prepare(`
  SELECT id, type, title, priority, target_audience
  FROM communications
  WHERE status = 'pending'
  ORDER BY priority ASC
`).all();

if (comms.length === 0) {
  console.log('   ✓ All communications handled!');
} else {
  comms.forEach(c => {
    console.log(`   [COMM-${c.id}] P${c.priority} | ${c.type.toUpperCase()}`);
    console.log(`            "${c.title}"`);
    console.log(`            Audience: ${c.target_audience}`);
    console.log('');
  });
}

// Hot trends
console.log('\n🔥 ACTIVE TRENDS (by relevance)');
console.log('─'.repeat(70));
const trends = db.prepare(`
  SELECT id, topic, description, relevance_score, source
  FROM trends
  WHERE status = 'active'
  ORDER BY relevance_score DESC
`).all();

if (trends.length === 0) {
  console.log('   No active trends');
} else {
  trends.forEach(t => {
    console.log(`   [TREND-${t.id}] Score: ${t.relevance_score}/100`);
    console.log(`            "${t.topic}"`);
    console.log(`            ${t.description.substring(0, 80)}...`);
    console.log(`            Source: ${t.source}`);
    console.log('');
  });
}

// Available research
console.log('\n🔬 AVAILABLE RESEARCH');
console.log('─'.repeat(70));
const research = db.prepare(`
  SELECT id, title, summary, category
  FROM research
  WHERE status = 'available'
  ORDER BY created_at DESC
`).all();

if (research.length === 0) {
  console.log('   No available research');
} else {
  research.forEach(r => {
    console.log(`   [RESEARCH-${r.id}] Category: ${r.category}`);
    console.log(`            "${r.title}"`);
    console.log(`            ${r.summary.substring(0, 80)}...`);
    console.log('');
  });
}

// Current content plan status
console.log('\n📝 CURRENT CONTENT PIPELINE');
console.log('─'.repeat(70));
const pipeline = db.prepare(`
  SELECT status, COUNT(*) as count
  FROM content_plan
  GROUP BY status
  ORDER BY
    CASE status
      WHEN 'writing' THEN 1
      WHEN 'review' THEN 2
      WHEN 'planned' THEN 3
      WHEN 'published' THEN 4
      ELSE 5
    END
`).all();

if (pipeline.length === 0) {
  console.log('   No content in pipeline - time to plan!');
} else {
  pipeline.forEach(p => {
    const emoji = {
      'planned': '📋',
      'writing': '✏️',
      'review': '👀',
      'published': '✅',
      'cancelled': '❌'
    }[p.status] || '📄';
    console.log(`   ${emoji} ${p.status}: ${p.count} items`);
  });
}

console.log('\n' + '═'.repeat(70));
console.log('💡 Ralph should prioritize: High-priority comms → Hot trends → Research');
console.log('═'.repeat(70) + '\n');

db.close();
