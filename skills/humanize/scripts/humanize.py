#!/usr/bin/env python3
"""
humanize.py - Remove AI artifacts and make content sound human
"""

import argparse
import re
import sys
from pathlib import Path

# AI tells to detect
AI_TELLS = [
    # Overused AI words
    r'\bdelve\b', r'\bdelving\b', r'\bdelves\b',
    r'\blandscape\b(?=.*\b(the|a|this)\b)',  # "the landscape" not "mountain landscape"
    r'\bleverage\b', r'\bleveraging\b',
    r'\bit\'?s important to note\b',
    r'\bin conclusion\b',
    r'\bgame-changing\b', r'\bgame changer\b',
    r'\brevolutionary\b',
    r'\btransformative\b',
    r'\bcutting-edge\b',
    r'\bstate-of-the-art\b',
    r'\bparadigm shift\b',
    r'\bunlock\b(?=.*\b(potential|power|value)\b)',
    r'\bharness\b(?=.*\b(power|potential)\b)',
    r'\bseamlessly\b',
    r'\bempower\b',
    r'\brobust\b',
    r'\bscalable\b',
    r'\binnovative\b',
    r'\bcomprehensive\b',
    r'\bholistic\b',
    r'\bsynergy\b', r'\bsynergies\b',
    r'\bworld-class\b',
    r'\bbest-in-class\b',
    r'\bnext-generation\b',
    r'\bgroundbreaking\b',
    
    # Hedging patterns
    r'\bit\'?s worth noting that\b',
    r'\bperhaps\b(?=.*\b(we|it|this)\b)',
    r'\bit\'?s possible that\b',
    r'\bmay or may not\b',
    r'\bto some extent\b',
    
    # Filler phrases
    r'\bin today\'?s (world|society|marketplace)\b',
    r'\bthe fact that\b',
    r'\bat the end of the day\b',
    r'\bneedless to say\b',
    r'\binterestingly\b,',
    r'\bnotably\b,',
]

# Contractions to use
CONTRACTIONS = {
    "it is": "it's",
    "it was": "it was",  # keep
    "that is": "that's",
    "there is": "there's",
    "here is": "here's",
    "what is": "what's",
    "who is": "who's",
    "how is": "how's",
    "where is": "where's",
    "when is": "when's",
    "why is": "why's",
    "I am": "I'm",
    "I have": "I've",
    "I will": "I'll",
    "I would": "I'd",
    "you are": "you're",
    "you have": "you've",
    "you will": "you'll",
    "you would": "you'd",
    "we are": "we're",
    "we have": "we've",
    "we will": "we'll",
    "we would": "we'd",
    "they are": "they're",
    "they have": "they've",
    "they will": "they'll",
    "they would": "they'd",
    "is not": "isn't",
    "are not": "aren't",
    "was not": "wasn't",
    "were not": "weren't",
    "have not": "haven't",
    "has not": "hasn't",
    "had not": "hadn't",
    "will not": "won't",
    "would not": "wouldn't",
    "could not": "couldn't",
    "should not": "shouldn't",
    "do not": "don't",
    "does not": "doesn't",
    "did not": "didn't",
    "cannot": "can't",
    "could've": "could've",
    "should've": "should've",
    "would've": "would've",
}

# Replacements for AI words
AI_REPLACEMENTS = {
    "delve": "dig into",
    "delving": "digging into",
    "delves": "digs into",
    "leverage": "use",
    "leveraging": "using",
    "game-changing": "major",
    "game changer": "game changer",  # keep, it's colloquial
    "revolutionary": "new",
    "transformative": "useful",
    "cutting-edge": "modern",
    "state-of-the-art": "modern",
    "paradigm shift": "shift",
    "unlock": "tap into",
    "harness": "use",
    "seamlessly": "",
    "empower": "help",
    "robust": "reliable",
    "scalable": "flexible",
    "innovative": "new",
    "comprehensive": "full",
    "holistic": "complete",
    "synergy": "combo",
    "synergies": "combos",
    "world-class": "great",
    "best-in-class": "top",
    "next-generation": "next",
    "groundbreaking": "new",
}


def detect_ai_tells(text: str) -> list:
    """Detect AI-generated patterns in text."""
    tells = []
    text_lower = text.lower()
    
    for pattern in AI_TELLS:
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        for match in matches:
            tells.append({
                "pattern": pattern,
                "match": match.group(),
                "position": match.start()
            })
    
    return tells


def analyze_structure(text: str) -> dict:
    """Analyze text structure for AI patterns."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Check sentence starting patterns
    sentence_starts = []
    for s in sentences:
        words = s.split()[:3]
        if words:
            sentence_starts.append(' '.join(words).lower())
    
    # Count repetitive starts
    from collections import Counter
    start_counts = Counter(sentence_starts)
    repetitive_starts = sum(1 for c in start_counts.values() if c > 1)
    
    # Check paragraph length variety
    para_lengths = [len(p.split()) for p in paragraphs]
    avg_para_len = sum(para_lengths) / len(para_lengths) if para_lengths else 0
    len_variance = max(para_lengths) - min(para_lengths) if para_lengths else 0
    
    # Check for perfectly parallel lists
    lists = re.findall(r'(?:^|\n)(?:[-•*]|\d+\.)\s+.+', text, re.MULTILINE)
    list_items = [re.sub(r'^[-•*\d.]\s*', '', item).strip() for item in lists]
    
    parallel_lists = 0
    for i in range(len(list_items) - 1):
        # Check if items start with same word type
        if list_items[i].split() and list_items[i+1].split():
            if list_items[i].split()[0].lower() == list_items[i+1].split()[0].lower():
                parallel_lists += 1
    
    return {
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "repetitive_starts": repetitive_starts,
        "avg_paragraph_length": round(avg_para_len, 1),
        "paragraph_length_variance": len_variance,
        "parallel_list_items": parallel_lists,
        "ai_tells": len(detect_ai_tells(text))
    }


def humanize_text(text: str, channel: str = None, show_diff: bool = False) -> str:
    """Rewrite text to sound more human."""
    result = text
    
    # Track changes for diff
    changes = []
    
    # Step 1: Replace AI words
    for ai_word, replacement in AI_REPLACEMENTS.items():
        # Handle special case: if replacement ends with preposition, check for duplicate
        prepositions = ['into', 'to', 'for', 'with', 'on', 'at']
        for prep in prepositions:
            if replacement.endswith(' ' + prep):
                # Match word + preposition (to avoid double preposition)
                pattern = r'\b' + ai_word + r'\s+' + prep + r'\b'
                if re.search(pattern, result, re.IGNORECASE):
                    matches = list(re.finditer(pattern, result, re.IGNORECASE))
                    for match in reversed(matches):
                        old_phrase = match.group()
                        # Preserve capitalization
                        if old_phrase[0].isupper():
                            new_phrase = replacement[0].upper() + replacement[1:]
                        else:
                            new_phrase = replacement
                        result = result[:match.start()] + new_phrase + result[match.end():]
                        changes.append(f"'{old_phrase}' → '{new_phrase}'")
                    break
        else:
            # Normal replacement
            pattern = r'\b' + ai_word + r'\b'
            matches = list(re.finditer(pattern, result, re.IGNORECASE))
            for match in reversed(matches):  # reversed to maintain positions
                old_word = match.group()
                # Preserve capitalization
                if old_word[0].isupper():
                    new_word = replacement[0].upper() + replacement[1:]
                else:
                    new_word = replacement
                
                if new_word:  # Only if there's a replacement
                    result = result[:match.start()] + new_word + result[match.end():]
                    if old_word.lower() != new_word.lower():
                        changes.append(f"'{old_word}' → '{new_word}'")
    
    # Clean up double prepositions that might have slipped through
    result = re.sub(r'\b(into|to|for|with|on|at)\s+\1\b', r'\1', result, flags=re.IGNORECASE)
    
    # Step 2: Remove filler phrases
    filler_patterns = [
        (r'\bIt\'?s important to note that\b', ''),
        (r'\bIt\'?s worth noting that\b', ''),
        (r'\bIn today\'?s (world|society|marketplace)\b,?\s*', ''),
        (r'\bThe fact that\b', ''),
        (r'\bAt the end of the day\b,?\s*', ''),
        (r'\bNeedless to say\b,?\s*', ''),
        (r'\bIn conclusion\b,?\s*', ''),
        (r'\bTo sum up\b,?\s*', ''),
        (r'\bseamlessly\s+', ''),  # Often filler
    ]
    
    for pattern, replacement in filler_patterns:
        matches = list(re.finditer(pattern, result, re.IGNORECASE))
        for match in reversed(matches):
            removed_text = match.group().strip()
            result = result[:match.start()] + replacement + result[match.end():]
            if removed_text:
                changes.append(f"Removed: '{removed_text}'")
    
    # Step 3: Add contractions (for natural speech)
    for full, contraction in CONTRACTIONS.items():
        pattern = r'\b' + full + r'\b'
        if re.search(pattern, result, re.IGNORECASE):
            result = re.sub(pattern, contraction, result, flags=re.IGNORECASE)
    
    # Step 4: Clean up double spaces and orphaned punctuation
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s+([.,!?;:])', r'\1', result)
    result = re.sub(r'([.,!?;:])\s*', r'\1 ', result)
    
    # Step 5: Channel-specific tuning
    if channel == 'twitter':
        # Make punchy - prefer shorter sentences
        result = re.sub(r'\s*-\s*', ' - ', result)  # Clean dashes
        # Remove "I think" and similar
        result = re.sub(r'\bI think that\s*', '', result, flags=re.IGNORECASE)
        result = re.sub(r'\bI believe that\s*', '', result, flags=re.IGNORECASE)
        
    elif channel == 'linkedin':
        # Professional but not stiff
        # Keep some formality but remove buzzwords
        pass
        
    elif channel == 'email':
        # Brief and action-oriented
        result = re.sub(r'\bPlease feel free to\b', 'Feel free to', result, flags=re.IGNORECASE)
        result = re.sub(r'\bI wanted to reach out\b', 'Reaching out', result, flags=re.IGNORECASE)
        
    elif channel == 'blog':
        # More personal, casual
        pass
    
    if show_diff and changes:
        print("\nChanges made:")
        for c in changes[:10]:  # Show first 10
            print(f"  • {c}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more")
        print()
    
    return result.strip()


def main():
    parser = argparse.ArgumentParser(description="Humanize AI-generated text")
    parser.add_argument("text", nargs="?", help="Text to humanize")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--channel", "-c", 
                       choices=["twitter", "linkedin", "blog", "email"],
                       help="Target channel for style tuning")
    parser.add_argument("--diff", "-d", action="store_true", 
                       help="Show what changed")
    parser.add_argument("--analyze", "-a", action="store_true",
                       help="Just analyze, don't rewrite")
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        return
    
    if not text.strip():
        print("Error: No text provided")
        sys.exit(1)
    
    # Analyze only mode
    if args.analyze:
        analysis = analyze_structure(text)
        tells = detect_ai_tells(text)
        
        print(f"AI Detection Analysis\n{'='*40}")
        print(f"Sentence count: {analysis['sentence_count']}")
        print(f"Paragraph count: {analysis['paragraph_count']}")
        print(f"Repetitive sentence starts: {analysis['repetitive_starts']}")
        print(f"Paragraph length variance: {analysis['paragraph_length_variance']} words")
        print(f"Parallel list items: {analysis['parallel_list_items']}")
        print(f"\nAI tells found: {len(tells)}")
        
        if tells:
            print("\nTop tells:")
            for tell in tells[:5]:
                print(f"  • '{tell['match']}'")
        
        # AI probability score
        score = min(100, len(tells) * 10 + analysis['repetitive_starts'] * 5)
        print(f"\nAI-likelihood score: {score}%")
        return
    
    # Humanize
    result = humanize_text(text, channel=args.channel, show_diff=args.diff)
    print(result)


if __name__ == "__main__":
    main()