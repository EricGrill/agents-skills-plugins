import Database from 'better-sqlite3';
import { mkdirSync } from 'fs';
import { dirname } from 'path';

const DB_PATH = './data/content.db';

// Ensure data directory exists
mkdirSync(dirname(DB_PATH), { recursive: true });

const db = new Database(DB_PATH);

// Enable foreign keys
db.pragma('foreign_keys = ON');

// Create tables
db.exec(`
  -- =============================================
  -- PHASE 1: DISCOVER - Input Sources
  -- =============================================

  -- Founder's existing content for voice analysis
  CREATE TABLE IF NOT EXISTS founder_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL CHECK(source IN ('blog', 'twitter', 'linkedin', 'newsletter', 'podcast', 'other')),
    title TEXT,
    content TEXT NOT NULL,
    url TEXT,
    engagement_score INTEGER DEFAULT 0,
    published_at DATETIME,
    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    analyzed BOOLEAN DEFAULT FALSE
  );

  -- Competitor content for gap analysis
  CREATE TABLE IF NOT EXISTS competitor_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competitor_name TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    summary TEXT,
    angle TEXT,
    engagement_notes TEXT,
    gap_opportunity TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- Market trends and data
  CREATE TABLE IF NOT EXISTS trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    description TEXT,
    source TEXT,
    relevance_score INTEGER DEFAULT 50,
    data_points TEXT,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'used', 'expired'))
  );

  -- Research and studies
  CREATE TABLE IF NOT EXISTS research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT,
    key_findings TEXT,
    data_points TEXT,
    sources TEXT,
    category TEXT,
    credibility_score INTEGER DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'available' CHECK(status IN ('available', 'used', 'archived'))
  );

  -- Company communications
  CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('product_update', 'announcement', 'milestone', 'feature', 'case_study', 'partnership')),
    title TEXT NOT NULL,
    details TEXT,
    key_messages TEXT,
    target_audience TEXT,
    priority INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deadline DATETIME,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'assigned', 'completed'))
  );

  -- =============================================
  -- PHASE 2: LEARN - Voice Analysis
  -- =============================================

  -- Voice DNA profile extracted from founder content
  CREATE TABLE IF NOT EXISTS voice_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_name TEXT NOT NULL DEFAULT 'founder',
    tone TEXT,
    formality TEXT,
    sentence_patterns TEXT,
    paragraph_style TEXT,
    signature_phrases TEXT,
    hook_patterns TEXT,
    data_usage_style TEXT,
    storytelling_style TEXT,
    cta_style TEXT,
    controversial_tendency TEXT,
    emoji_usage TEXT,
    vocabulary_notes TEXT,
    avoid_patterns TEXT,
    sample_excerpts TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- What makes content work (high engagement patterns)
  CREATE TABLE IF NOT EXISTS content_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN ('hook', 'structure', 'angle', 'cta', 'topic', 'format')),
    description TEXT NOT NULL,
    example TEXT,
    effectiveness_score INTEGER DEFAULT 50,
    source_content_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_content_id) REFERENCES founder_content(id)
  );

  -- =============================================
  -- PHASE 3: RESEARCH - Deep Dives
  -- =============================================

  -- Research briefs compiled before writing
  CREATE TABLE IF NOT EXISTS research_briefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    target_angle TEXT,
    key_stats TEXT,
    expert_quotes TEXT,
    case_studies TEXT,
    counter_arguments TEXT,
    unique_insights TEXT,
    competitor_gaps TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'complete', 'used'))
  );

  -- =============================================
  -- PHASE 4: IDEATE - Angle Discovery
  -- =============================================

  -- Content ideas with angle analysis
  CREATE TABLE IF NOT EXISTS content_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    obvious_angle TEXT,
    unique_angle TEXT NOT NULL,
    angle_justification TEXT,
    target_reader TEXT,
    hook_options TEXT,
    based_on_trend_id INTEGER,
    based_on_research_id INTEGER,
    based_on_comm_id INTEGER,
    uniqueness_score INTEGER DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'idea' CHECK(status IN ('idea', 'approved', 'writing', 'rejected')),
    FOREIGN KEY (based_on_trend_id) REFERENCES trends(id),
    FOREIGN KEY (based_on_research_id) REFERENCES research(id),
    FOREIGN KEY (based_on_comm_id) REFERENCES communications(id)
  );

  -- =============================================
  -- PHASE 5-7: WRITE, CRITIQUE, ITERATE
  -- =============================================

  -- Content plan (approved ideas ready for writing)
  CREATE TABLE IF NOT EXISTS content_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER,
    content_type TEXT NOT NULL CHECK(content_type IN ('blog', 'social', 'newsletter', 'case_study', 'landing_page', 'email_sequence', 'thread')),
    title TEXT NOT NULL,
    brief TEXT,
    target_keywords TEXT,
    voice_profile_id INTEGER DEFAULT 1,
    quality_bar TEXT DEFAULT 'high' CHECK(quality_bar IN ('standard', 'high', 'flagship')),
    priority INTEGER DEFAULT 5,
    planned_date DATE,
    status TEXT DEFAULT 'planned' CHECK(status IN ('planned', 'researching', 'writing', 'critiquing', 'iterating', 'review', 'published', 'cancelled')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES content_ideas(id),
    FOREIGN KEY (voice_profile_id) REFERENCES voice_profile(id)
  );

  -- Drafts with version tracking and critique
  CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    critique TEXT,
    critique_passed BOOLEAN DEFAULT FALSE,
    iteration_notes TEXT,
    voice_match_score INTEGER,
    uniqueness_score INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES content_plan(id)
  );

  -- Quality critique checklist results
  CREATE TABLE IF NOT EXISTS critique_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id INTEGER NOT NULL,
    hook_stops_scroll BOOLEAN,
    unique_angle BOOLEAN,
    data_backed BOOLEAN,
    sounds_like_founder BOOLEAN,
    worth_sharing BOOLEAN,
    actionable BOOLEAN,
    better_than_competitors BOOLEAN,
    overall_pass BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (draft_id) REFERENCES drafts(id)
  );

  -- Published content
  CREATE TABLE IF NOT EXISTS published (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    draft_id INTEGER NOT NULL,
    final_content TEXT NOT NULL,
    meta_description TEXT,
    final_version INTEGER,
    iterations_required INTEGER DEFAULT 1,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    performance_notes TEXT,
    FOREIGN KEY (plan_id) REFERENCES content_plan(id),
    FOREIGN KEY (draft_id) REFERENCES drafts(id)
  );

  -- Agent activity log
  CREATE TABLE IF NOT EXISTS agent_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase TEXT CHECK(phase IN ('discover', 'learn', 'research', 'ideate', 'write', 'critique', 'iterate', 'publish')),
    action TEXT NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

console.log('✅ Database initialized at', DB_PATH);
console.log('   Tables: founder_content, competitor_content, trends, research,');
console.log('           communications, voice_profile, content_patterns,');
console.log('           research_briefs, content_ideas, content_plan,');
console.log('           drafts, critique_results, published, agent_log');
db.close();
