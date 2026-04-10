# Plugin Quality Scoring System

## Overview

The plugin quality scoring system provides objective metrics to help users identify well-maintained, tested, and documented plugins. Scores are calculated automatically and displayed as badges.

## Scoring Criteria

| Category | Weight | Max Points | Description |
|----------|--------|------------|-------------|
| **Documentation** | 30% | 30 | README completeness, examples, troubleshooting |
| **Functionality** | 25% | 25 | Works as advertised, tested with Claude Code |
| **Code Quality** | 20% | 20 | Follows best practices, no security issues |
| **Maintenance** | 15% | 15 | Recent activity, issue response time |
| **Community** | 10% | 10 | Stars, forks, contributor count |
| **Total** | **100%** | **100** | Aggregate quality score |

## Detailed Scoring Rubric

### Documentation (30 points)

| Criteria | Points | Requirements |
|----------|--------|--------------|
| README completeness | 10 | Has all required sections |
| Usage examples | 8 | At least 3 concrete examples |
| Installation guide | 5 | Clear installation steps |
| Troubleshooting | 4 | Common issues documented |
| Changelog | 3 | Version history maintained |

### Functionality (25 points)

| Criteria | Points | Requirements |
|----------|--------|--------------|
| Core features work | 12 | All advertised features functional |
| Edge cases handled | 7 | Handles errors gracefully |
| Claude Code tested | 6 | Verified with actual Claude Code |

### Code Quality (20 points)

| Criteria | Points | Requirements |
|----------|--------|--------------|
| Security review | 8 | No hardcoded secrets, safe commands |
| Best practices | 6 | Follows established patterns |
| Manifest valid | 4 | plugin.json passes schema validation |
| No conflicts | 2 | No known plugin conflicts |

### Maintenance (15 points)

| Criteria | Points | Requirements |
|----------|--------|--------------|
| Recent commits | 5 | Activity within 6 months |
| Issue response | 5 | Responds to issues promptly |
| Version updates | 3 | Keeps dependencies current |
| Deprecated handling | 2 | Graceful deprecation process |

### Community (10 points)

| Criteria | Points | Requirements |
|----------|--------|--------------|
| GitHub stars | 4 | 10+ stars |
| Forks | 3 | 2+ forks |
| Contributors | 3 | 2+ contributors |

## Quality Badges

Plugins receive one of four quality badges based on their score:

| Badge | Score Range | Description |
|-------|-------------|-------------|
| ![Platinum](https://img.shields.io/badge/quality-platinum-9cf) | 90-100 | Exceptional quality, actively maintained |
| ![Gold](https://img.shields.io/badge/quality-gold-yellow) | 75-89 | High quality, recommended |
| ![Silver](https://img.shields.io/badge/quality-silver-lightgrey) | 60-74 | Good quality, stable |
| ![Bronze](https://img.shields.io/badge/quality-bronze-orange) | 40-59 | Acceptable quality |
| ![Needs Work](https://img.shields.io/badge/quality-needs%20work-red) | 0-39 | Needs improvement |

## Automated Scoring

Quality scores are calculated weekly via GitHub Actions:

```yaml
# .github/workflows/quality-score.yml
name: Calculate Plugin Quality Scores

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  score:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Calculate Scores
        run: |
          python scripts/calculate-quality-scores.py
      - name: Update Badges
        run: |
          python scripts/update-quality-badges.py
```

## Manual Review

Plugins can also receive manual quality designations:

- **Curated** - Hand-picked by maintainers for exceptional quality
- **Community Favorite** - High community engagement
- **Maintainer Recommended** - Suggested for new users

## Improving Your Score

### Quick Wins

1. **Add a comprehensive README** (+10-15 points)
2. **Include 3+ usage examples** (+8 points)
3. **Create a CHANGELOG.md** (+3 points)
4. **Fix any JSON syntax errors** (+4 points)
5. **Respond to open issues** (+5 points)

### Long-term Improvements

1. **Regular updates** - Keep dependencies current
2. **Community building** - Encourage stars and contributions
3. **Expand functionality** - Add more features and skills
4. **Thorough testing** - Test with various Claude Code versions

## Score API

Access plugin scores programmatically:

```bash
# Get score for a specific plugin
curl https://agents-skills-plugins.dev/api/scores/{plugin-name}

# Get all scores
curl https://agents-skills-plugins.dev/api/scores

# Get top-rated plugins
curl https://agents-skills-plugins.dev/api/scores?sort=rating&limit=10
```

## Score History

Track score changes over time:

```json
{
  "plugin": "superpowers",
  "currentScore": 95,
  "history": [
    {"date": "2025-03-01", "score": 92},
    {"date": "2025-02-01", "score": 88},
    {"date": "2025-01-01", "score": 85}
  ]
}
```

## Reporting Issues

If you believe a quality score is inaccurate:

1. Open an issue with label `quality-score`
2. Provide evidence of the discrepancy
3. Allow 48 hours for review

## Future Enhancements

Planned improvements to the scoring system:

- User ratings and reviews
- Automated security scanning
- Performance benchmarks
- Compatibility testing across platforms
