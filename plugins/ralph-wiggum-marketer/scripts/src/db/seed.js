import Database from 'better-sqlite3';

const db = new Database('./data/content.db');

// Clear existing data (in reverse order of dependencies)
const tables = [
  'agent_log', 'published', 'critique_results', 'drafts', 'content_plan',
  'content_ideas', 'research_briefs', 'content_patterns', 'voice_profile',
  'communications', 'research', 'trends', 'competitor_content', 'founder_content'
];
tables.forEach(t => {
  try { db.exec(`DELETE FROM ${t}`); } catch (e) { /* table may not exist */ }
});

// ===========================================
// FOUNDER CONTENT (for voice analysis)
// ===========================================
const insertFounderContent = db.prepare(`
  INSERT INTO founder_content (source, title, content, url, engagement_score, analyzed)
  VALUES (?, ?, ?, ?, ?, FALSE)
`);

const founderContent = [
  {
    source: 'blog',
    title: 'Why We Rebuilt Our Entire Product in 6 Weeks',
    content: `Here's the thing about technical debt: it's not actually the code that kills you. It's the decision paralysis.

We had 47,000 lines of legacy code. Every feature request turned into a 3-day archaeology expedition. "Where does this connect to that? Who wrote this? Why is there a comment that just says 'DO NOT TOUCH'?"

So we did the unthinkable. We started fresh.

Not a refactor. Not a "gradual migration." We opened a new repo and rebuilt from scratch.

The results:
- 6 weeks to feature parity
- 12,000 lines instead of 47,000
- Deploy time: 45 minutes → 3 minutes
- Bug reports: down 73%

Was it risky? Absolutely. Would I do it again? In a heartbeat.

Here's what I learned...`,
    url: 'https://example.com/blog/rebuild',
    engagement: 450
  },
  {
    source: 'twitter',
    title: 'Thread on AI tools',
    content: `I've tested 47 AI writing tools in the last 6 months.

Most of them produce garbage.

Here are the 3 that actually work (and why): 🧵

1/ First, let's talk about what "works" means.

It doesn't mean "generates text."
It means "generates text I'd actually publish."

Big difference.

2/ Tool #1: [redacted]
Why it works: It doesn't try to be creative. It's a research assistant that happens to write.
Best for: First drafts where you need structure.
Weakness: Zero personality. You'll rewrite 60%.

3/ The pattern I noticed...`,
    url: 'https://twitter.com/example/thread',
    engagement: 2340
  },
  {
    source: 'linkedin',
    title: 'The hiring mistake I keep making',
    content: `I've made the same hiring mistake 4 times now.

Hired for skills. Ignored working style.

Every time, the person was technically brilliant. And every time, it didn't work out.

Here's what I mean by "working style":
- Do they need structure or autonomy?
- How do they handle ambiguity?
- What's their communication frequency?
- How do they respond to feedback?

Skills can be taught. Working style is baked in.

Now I spend 70% of interviews on working style, 30% on skills.

The difference has been night and day.`,
    url: 'https://linkedin.com/posts/example',
    engagement: 890
  }
];

founderContent.forEach(c => insertFounderContent.run(
  c.source, c.title, c.content, c.url, c.engagement
));

// ===========================================
// VOICE PROFILE (extracted from content)
// ===========================================
db.prepare(`
  INSERT INTO voice_profile (
    profile_name, tone, formality, sentence_patterns, paragraph_style,
    signature_phrases, hook_patterns, data_usage_style, storytelling_style,
    cta_style, controversial_tendency, emoji_usage, vocabulary_notes, avoid_patterns
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`).run(
  'founder',
  'Direct, confident, occasionally self-deprecating',
  'Casual professional - contractions OK, no jargon',
  JSON.stringify([
    'Short sentences for impact',
    'Lists with specific numbers',
    'Questions to create curiosity',
    'One-line paragraphs for emphasis'
  ]),
  'Short paragraphs (1-3 sentences), lots of white space, frequent line breaks',
  JSON.stringify([
    "Here's the thing",
    "Let me be direct",
    "The results:",
    "Would I do it again?",
    "Here's what I learned"
  ]),
  JSON.stringify([
    'Counterintuitive statement',
    'Specific number + surprising outcome',
    'Direct challenge to common belief',
    'Personal failure/mistake admission'
  ]),
  'Leads with specific numbers, always cites source or personal experience',
  'Personal anecdotes to illustrate points, admits mistakes openly',
  'Soft ask, value-first, often ends with question or reflection',
  'High - takes clear positions, not afraid to say "most X is garbage"',
  'Minimal - occasional 🧵 for threads, otherwise text-only',
  JSON.stringify([
    'Uses "actually" for emphasis',
    'Numbered lists for clarity',
    'Rhetorical questions'
  ]),
  JSON.stringify([
    '"In today\'s rapidly evolving..."',
    '"It\'s important to note..."',
    '"In conclusion..."',
    'Passive voice',
    'Corporate jargon'
  ])
);

// ===========================================
// COMPETITOR CONTENT (for gap analysis)
// ===========================================
const insertCompetitor = db.prepare(`
  INSERT INTO competitor_content (competitor_name, title, url, summary, angle, engagement_notes, gap_opportunity)
  VALUES (?, ?, ?, ?, ?, ?, ?)
`);

const competitors = [
  {
    name: 'Competitor A',
    title: '10 Ways AI is Transforming Content Marketing',
    url: 'https://competitor-a.com/blog/ai-content',
    summary: 'Generic listicle about AI tools, no specific data',
    angle: 'Obvious "AI is changing everything" take',
    engagement: 'High shares but low comments - people share without reading',
    gap: 'No specific results or case studies. Opportunity: Real numbers from real usage'
  },
  {
    name: 'Competitor B',
    title: 'The Complete Guide to AI Content Strategy',
    url: 'https://competitor-b.com/guide',
    summary: '5000 word guide that tries to cover everything',
    angle: 'Comprehensive but overwhelming',
    engagement: 'Good SEO traffic but high bounce rate',
    gap: 'Too broad. Opportunity: Specific, actionable playbook for ONE use case'
  }
];

competitors.forEach(c => insertCompetitor.run(
  c.name, c.title, c.url, c.summary, c.angle, c.engagement, c.gap
));

// ===========================================
// TRENDS
// ===========================================
const insertTrend = db.prepare(`
  INSERT INTO trends (topic, description, source, relevance_score, data_points, status)
  VALUES (?, ?, ?, ?, ?, 'active')
`);

const trends = [
  {
    topic: 'AI Agents Replacing SaaS Tools',
    description: 'The shift from "AI-assisted tools" to "AI agents that use tools" is accelerating. Companies moving from AI features to AI-first architectures.',
    source: 'a16z Research + HN discussions',
    relevance: 95,
    data: JSON.stringify([
      '340% increase in "AI agent" job postings (LinkedIn)',
      '67% of SaaS companies adding agent capabilities (Gartner)',
      'Agent frameworks (LangChain, CrewAI) growing 500%+ YoY'
    ])
  },
  {
    topic: 'Context Engineering > Prompt Engineering',
    description: 'The conversation is shifting from "write better prompts" to "provide better context." System design > clever prompting.',
    source: 'Anthropic blog + Twitter discourse',
    relevance: 88,
    data: JSON.stringify([
      'Anthropic\'s context engineering blog: 50k+ views in 48h',
      'Prompt engineering courses plateauing',
      'RAG and memory systems becoming standard'
    ])
  },
  {
    topic: 'Vibe Coding Movement',
    description: 'Developers letting AI handle implementation while focusing on architecture and intent. "I describe what I want, AI writes it."',
    source: 'Twitter/X, dev communities',
    relevance: 82,
    data: JSON.stringify([
      'Cursor and Claude Code growing 400%+ MoM',
      '"Vibe coding" mentions up 1200% in 3 months',
      'Traditional IDE usage declining in AI-heavy workflows'
    ])
  }
];

trends.forEach(t => insertTrend.run(t.topic, t.description, t.source, t.relevance, t.data));

// ===========================================
// RESEARCH
// ===========================================
const insertResearch = db.prepare(`
  INSERT INTO research (title, summary, key_findings, data_points, sources, category, credibility_score, status)
  VALUES (?, ?, ?, ?, ?, ?, ?, 'available')
`);

const research = [
  {
    title: 'AI Content Performance Study 2024',
    summary: 'Analysis of 10,000 blog posts: AI-generated vs human-written vs AI-assisted performance',
    findings: JSON.stringify([
      'Pure AI content: 23% lower engagement than human',
      'AI-assisted (human edited): 12% HIGHER engagement',
      'The gap is in specificity - AI lacks real examples',
      'Best performing: Human experience + AI research/structure'
    ]),
    data: JSON.stringify([
      { metric: 'AI-only engagement', value: '-23%' },
      { metric: 'AI-assisted engagement', value: '+12%' },
      { metric: 'Time to publish (AI-assisted)', value: '-65%' },
      { metric: 'Factual errors (AI-only)', value: '3.2x higher' }
    ]),
    sources: JSON.stringify(['Orbit Media Study', 'Content Marketing Institute']),
    category: 'content_performance',
    credibility: 85
  },
  {
    title: 'Developer Tool Adoption Patterns',
    summary: 'How developers evaluate and adopt new AI coding tools - from discovery to daily usage',
    findings: JSON.stringify([
      'Trial-to-adoption: 34% for AI tools vs 12% for traditional',
      'Primary adoption driver: "Does it actually save time?"',
      'Top complaint: "Confidently wrong" - hallucinates plausibly',
      'Retention killer: Context switching between tools'
    ]),
    data: JSON.stringify([
      { metric: 'AI tool trial rate', value: '73%' },
      { metric: 'Trial-to-paid conversion', value: '34%' },
      { metric: 'Daily active usage', value: '41% of adopters' },
      { metric: 'Top reason for churn', value: '"Too many hallucinations"' }
    ]),
    sources: JSON.stringify(['Stack Overflow Survey', 'GitHub Copilot metrics']),
    category: 'developer_tools',
    credibility: 90
  }
];

research.forEach(r => insertResearch.run(
  r.title, r.summary, r.findings, r.data, r.sources, r.category, r.credibility
));

// ===========================================
// COMMUNICATIONS (company news)
// ===========================================
const insertComm = db.prepare(`
  INSERT INTO communications (type, title, details, key_messages, target_audience, priority, status)
  VALUES (?, ?, ?, ?, ?, ?, 'pending')
`);

const communications = [
  {
    type: 'product_update',
    title: 'Launch: Voice DNA - AI That Writes Like You',
    details: 'New feature that analyzes your existing content library before writing. Learns your voice, references your past work, maintains consistency across all content.',
    messages: JSON.stringify([
      'Write content that sounds like you, not like AI',
      'Automatically references your past work for consistency',
      'Voice DNA technology learns your unique patterns',
      'Finally, AI that writes AS you, not FOR you'
    ]),
    audience: 'Content marketers, founders doing their own marketing, small marketing teams',
    priority: 1
  },
  {
    type: 'case_study',
    title: 'How Startup X Cut Content Time 70% While Improving Quality',
    details: 'Customer went from 1 blog post/month to 4/month. Quality scores (engagement, shares) actually improved. Key: They feed it their best performing content first.',
    messages: JSON.stringify([
      '70% reduction in content creation time',
      '4x content output with same team',
      'Engagement up 23% despite higher volume',
      'Secret: Quality of input determines quality of output'
    ]),
    audience: 'Startup founders, marketing leads, content managers',
    priority: 2
  }
];

communications.forEach(c => insertComm.run(
  c.type, c.title, c.details, c.messages, c.audience, c.priority
));

// ===========================================
// CONTENT PATTERNS (from founder analysis)
// ===========================================
const insertPattern = db.prepare(`
  INSERT INTO content_patterns (pattern_type, description, example, effectiveness_score)
  VALUES (?, ?, ?, ?)
`);

const patterns = [
  {
    type: 'hook',
    description: 'Counterintuitive opening that challenges common belief',
    example: '"Here\'s the thing about technical debt: it\'s not actually the code that kills you."',
    score: 92
  },
  {
    type: 'hook',
    description: 'Specific number + surprising outcome',
    example: '"I\'ve tested 47 AI writing tools. Most produce garbage. Here are the 3 that work."',
    score: 88
  },
  {
    type: 'structure',
    description: 'Problem → Counterintuitive solution → Results → Lessons',
    example: 'Rebuild post structure: Legacy problem → Did the scary thing → Specific results → What I learned',
    score: 85
  },
  {
    type: 'angle',
    description: 'Personal failure/mistake admission as credibility builder',
    example: '"I\'ve made the same hiring mistake 4 times now."',
    score: 90
  }
];

patterns.forEach(p => insertPattern.run(p.type, p.description, p.example, p.score));

// Log seeding
db.prepare(`INSERT INTO agent_log (phase, action, details) VALUES (?, ?, ?)`).run(
  'discover',
  'database_seeded',
  JSON.stringify({
    founder_content: founderContent.length,
    competitors: competitors.length,
    trends: trends.length,
    research: research.length,
    communications: communications.length,
    patterns: patterns.length
  })
);

console.log('✅ Database seeded with quality-focused sample data:');
console.log(`   - ${founderContent.length} founder content pieces (for voice analysis)`);
console.log(`   - 1 voice DNA profile extracted`);
console.log(`   - ${competitors.length} competitor gap analyses`);
console.log(`   - ${trends.length} market trends with data`);
console.log(`   - ${research.length} research studies`);
console.log(`   - ${communications.length} communications`);
console.log(`   - ${patterns.length} high-performing content patterns`);

db.close();
