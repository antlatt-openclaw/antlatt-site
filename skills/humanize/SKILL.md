# AI Content Humanization

Remove AI-generated artifacts and make content sound human.

## Usage

```bash
# Basic humanization
python3 scripts/humanize.py "Your text here..."

# With channel tuning
python3 scripts/humanize.py "Your text..." --channel twitter
python3 scripts/humanize.py "Your text..." --channel linkedin
python3 scripts/humanize.py "Your text..." --channel blog
python3 scripts/humanize.py "Your text..." --channel email

# Read from file
python3 scripts/humanize.py --file input.txt

# Show what changed
python3 scripts/humanize.py "Your text..." --diff
```

## Detection

Scans for AI tells:
- Overused words: "delve", "landscape", "leverage", "it's important to note", "in conclusion", "game-changing", "revolutionary", "transformative"
- Tone inflation
- Generic phrasing
- Repetitive sentence structures
- Excessive hedging
- Too-perfect lists
- Identical paragraph rhythms

## Rewrite

- Replace vague qualifiers with concrete language
- Vary sentence length
- Use contractions and fragments naturally
- Remove filler
- Add human cadence

## Channels

| Channel | Style |
|---------|-------|
| twitter | Punchy, <280 chars, direct |
| linkedin | Professional but conversational |
| blog | Longer, personal anecdotes OK |
| email | Brief, clear, action-oriented |