# Segmentation Strategies

Advanced patterns for splitting books into training chunks while preserving narrative coherence.

## The Segmentation Problem

Books present unique challenges for training data creation:

1. **Variable paragraph length**: Some authors write single paragraphs spanning 1000+ words
2. **Dialogue-heavy sections**: Short exchanges that individually are too small
3. **Scene boundaries**: Natural break points that don't align with word counts
4. **Stylistic variations**: Authors shift voice between narrative, dialogue, and exposition

Poor segmentation teaches the model to produce:
- Incomplete thoughts
- Abrupt endings
- Incoherent transitions
- Fragmented style

## Two-Tier Strategy

### Tier 1: Paragraph-Based Accumulation

The default approach for well-structured text:

```python
class Tier1Segmenter:
    def __init__(self, min_words: int = 250, max_words: int = 650):
        self.min_words = min_words
        self.max_words = max_words
    
    def segment(self, text: str) -> list[Chunk]:
        paragraphs = self._split_paragraphs(text)
        chunks = []
        current = ChunkBuilder()
        
        for para in paragraphs:
            word_count = len(para.split())
            
            # Check if single paragraph exceeds max
            if word_count > self.max_words:
                # Finalize current chunk if exists
                if current.word_count > 0:
                    chunks.append(current.build())
                    current = ChunkBuilder()
                
                # Mark for Tier 2 processing
                chunks.append(Chunk(
                    text=para,
                    requires_tier2=True,
                    word_count=word_count
                ))
                continue
            
            # Would this paragraph overflow current chunk?
            if current.word_count + word_count > self.max_words:
                if current.word_count >= self.min_words:
                    chunks.append(current.build())
                    current = ChunkBuilder()
            
            current.add(para)
        
        # Don't forget the last chunk
        if current.word_count > 0:
            chunks.append(current.build())
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> list[str]:
        # Split on double newlines, preserve single newlines within
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
```

### Tier 2: LLM-Assisted Segmentation

For oversized paragraphs that cannot be split at paragraph boundaries:

```python
class Tier2Segmenter:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.prompt_template = self._load_prompt()
    
    async def segment(self, oversized_chunk: Chunk) -> list[Chunk]:
        """Split an oversized paragraph using LLM."""
        
        response = await self._call_llm(
            self.prompt_template.format(text=oversized_chunk.text)
        )
        
        segments = self._parse_segments(response)
        
        # Validate zero-deletion
        original_words = len(oversized_chunk.text.split())
        segmented_words = sum(len(s.split()) for s in segments)
        
        if abs(original_words - segmented_words) > 5:  # Allow tiny variance
            raise SegmentationError(
                f"Word count mismatch: {original_words} -> {segmented_words}"
            )
        
        return [
            Chunk(text=s, requires_tier2=False, word_count=len(s.split()))
            for s in segments
        ]
    
    def _load_prompt(self) -> str:
        return """Segment this text into excerpts of minimum 300-350 words.

Requirements:
- Each excerpt must be grammatically complete from start
- Each excerpt must not feel abruptly cut off
- Zero deletion - maintain original word count exactly
- Break at grammatically natural places:
  * After complete dialogue exchanges
  * At scene transitions
  * After complete thoughts or descriptions
  * Where a paragraph break would naturally occur
- Avoid breaking into too many small excerpts
- Start directly with the excerpts
- Separate excerpts with ===SEGMENT===

Text to segment:
{text}
"""
    
    def _parse_segments(self, response: str) -> list[str]:
        segments = response.split("===SEGMENT===")
        return [s.strip() for s in segments if s.strip()]
```

## Scene-Aware Segmentation

For higher-quality results, detect scene boundaries:

```python
class SceneAwareSegmenter:
    """Prefer breaking at scene boundaries when within word limits."""
    
    SCENE_MARKERS = [
        r'\n\n\* \* \*\n\n',      # Asterisk dividers
        r'\n\n---\n\n',            # Dash dividers
        r'\n\n###\n\n',            # Hash dividers
        r'\n\nCHAPTER \d+',        # Chapter headings
        r'\n\n[A-Z]{3,}\n\n',      # All-caps scene breaks
    ]
    
    def find_scene_breaks(self, text: str) -> list[int]:
        """Find character positions of scene breaks."""
        breaks = []
        for pattern in self.SCENE_MARKERS:
            for match in re.finditer(pattern, text):
                breaks.append(match.start())
        return sorted(set(breaks))
    
    def segment_with_scenes(self, text: str) -> list[Chunk]:
        scene_breaks = self.find_scene_breaks(text)
        
        # If scene breaks exist, prefer them over arbitrary paragraph breaks
        if scene_breaks:
            return self._segment_at_scenes(text, scene_breaks)
        else:
            return Tier1Segmenter().segment(text)
```

## Dialogue Handling

Dialogue-heavy sections require special handling:

```python
class DialogueAwareSegmenter:
    """Group dialogue exchanges to maintain conversation coherence."""
    
    def is_dialogue_paragraph(self, para: str) -> bool:
        """Check if paragraph is primarily dialogue."""
        # Count dialogue markers
        quote_count = para.count('"') + para.count("'")
        word_count = len(para.split())
        
        # If more than 20% of words are in quotes, it's dialogue-heavy
        return quote_count > word_count * 0.2
    
    def segment(self, text: str) -> list[Chunk]:
        paragraphs = text.split('\n\n')
        chunks = []
        current = ChunkBuilder()
        in_dialogue_block = False
        
        for para in paragraphs:
            is_dialogue = self.is_dialogue_paragraph(para)
            
            # Don't break in the middle of a dialogue exchange
            if is_dialogue:
                in_dialogue_block = True
                current.add(para)
            else:
                if in_dialogue_block:
                    # End of dialogue block - good break point
                    in_dialogue_block = False
                    if current.word_count >= 250:
                        chunks.append(current.build())
                        current = ChunkBuilder()
                
                current.add(para)
                
                # Check if we've exceeded max
                if current.word_count > 650:
                    chunks.append(current.build())
                    current = ChunkBuilder()
        
        if current.word_count > 0:
            chunks.append(current.build())
        
        return chunks
```

## Validation Pipeline

Every segmentation result should pass validation:

```python
class SegmentationValidator:
    def validate(self, chunks: list[Chunk]) -> ValidationResult:
        errors = []
        warnings = []
        
        for i, chunk in enumerate(chunks):
            # Check word count bounds
            if chunk.word_count < 200:
                warnings.append(f"Chunk {i}: Only {chunk.word_count} words")
            if chunk.word_count > 700:
                errors.append(f"Chunk {i}: {chunk.word_count} words exceeds max")
            
            # Check sentence completeness
            if not self._ends_with_terminal(chunk.text):
                errors.append(f"Chunk {i}: Ends mid-sentence")
            
            if not self._starts_grammatically(chunk.text):
                errors.append(f"Chunk {i}: Starts mid-sentence")
            
            # Check for orphaned dialogue
            if chunk.text.count('"') % 2 != 0:
                warnings.append(f"Chunk {i}: Unbalanced quotes")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _ends_with_terminal(self, text: str) -> bool:
        text = text.strip()
        return text[-1] in '.!?"\'—'
    
    def _starts_grammatically(self, text: str) -> bool:
        text = text.strip()
        # Should start with capital or quote
        return text[0].isupper() or text[0] in '"\'—'
```

## Performance Considerations

| Strategy | Speed | Quality | Use Case |
|----------|-------|---------|----------|
| Tier 1 only | Fast | Moderate | Well-structured prose |
| Tier 1 + Tier 2 | Moderate | High | Mixed paragraph lengths |
| Scene-aware | Fast | High | Novels with clear scene breaks |
| Dialogue-aware | Moderate | High | Dialogue-heavy fiction |

## Edge Cases

**1. Stream-of-consciousness writing**
- Single "paragraphs" spanning pages
- Solution: Force Tier 2 with explicit sentence boundary detection

**2. Poetry or verse**
- Line breaks are semantic, not formatting
- Solution: Treat each stanza as atomic unit

**3. Non-fiction with lists/bullets**
- Bullet points break paragraph detection
- Solution: Pre-process to convert bullets to prose

**4. Multiple narrators**
- Voice shifts within chapters
- Solution: Detect narrator markers and prefer breaking there

## Integration with Pipeline

```python
class SegmentationAgent:
    def __init__(self, config: SegmentationConfig):
        self.tier1 = Tier1Segmenter(
            min_words=config.min_words,
            max_words=config.max_words
        )
        self.tier2 = Tier2Segmenter(model=config.tier2_model)
        self.validator = SegmentationValidator()
    
    async def segment(self, text: str) -> list[Chunk]:
        # Phase 1: Tier 1 segmentation
        chunks = self.tier1.segment(text)
        
        # Phase 2: Process oversized chunks with Tier 2
        final_chunks = []
        for chunk in chunks:
            if chunk.requires_tier2:
                sub_chunks = await self.tier2.segment(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        # Phase 3: Validate
        result = self.validator.validate(final_chunks)
        if not result.valid:
            raise SegmentationError(result.errors)
        
        if result.warnings:
            logger.warning(f"Segmentation warnings: {result.warnings}")
        
        return final_chunks
```

