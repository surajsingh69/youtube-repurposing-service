#!/usr/bin/env python3
"""
YouTube Content Repurposing Service v2
Improved content quality with better text processing.
Takes a YouTube URL and generates multiple content formats from the transcript.
Outputs: blog post, twitter thread, key quotes, summary.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print(
        "Error: youtube-transcript-api not installed. "
        "Use the isolated PM helper environment described in youtube-content/SKILL.md.",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """Extract the 11-character video ID from various YouTube URL formats."""
    url_or_id = url_or_id.strip()
    patterns = [
        r"(?:v=|youtu\.be/|shorts/|embed/|live/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_transcript(video_id: str, languages: list | None = None) -> str:
    """Fetch transcript using the youtube-transcript-api directly."""
    api = YouTubeTranscriptApi()
    if languages:
        segments = api.fetch(video_id, languages=languages)
    else:
        segments = api.fetch(video_id)

    full_text = " ".join(seg.text for seg in segments)
    return full_text.strip()


def clean_transcript(text: str) -> str:
    """Clean the transcript by removing music notes, artifacts, and normalizing whitespace."""
    # Remove music notes and audio artifacts
    text = re.sub(r'\[♪+.*?♪+\]', '', text, flags=re.DOTALL)
    text = re.sub(r'♪.*?♪', '', text, flags=re.DOTALL)
    
    # Remove speaker labels like "Speaker 1:" or "Host:"
    text = re.sub(r'^\s*(Speaker \d+|Host|Interviewer|Guest):\s*', '', text, flags=re.MULTILINE)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove timestamps if present (format: 00:00 or 0:00)
    text = re.sub(r'\b\d{1,2}:\d{2}\b', '', text)
    
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, handling common abbreviations."""
    # Protect common abbreviations
    text = text.replace('Mr.', 'Mr')
    text = text.replace('Mrs.', 'Mrs')
    text = text.replace('Dr.', 'Dr')
    text = text.replace('etc.', 'etc')
    text = text.replace('vs.', 'vs')
    text = text.replace('i.e.', 'ie')
    text = text.replace('e.g.', 'eg')
    text = text.replace('U.S.', 'US')
    text = text.replace('U.K.', 'UK')
    
    # Split on sentence endings
    sentences = re.split(r'[.!?]+', text)
    
    # Restore abbreviations and clean up
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    return sentences


def extract_key_points(sentences: list[str], num_points: int = 5) -> list[str]:
    """Extract key points from sentences using multiple strategies."""
    scored = []
    
    for i, sentence in enumerate(sentences):
        score = 0
        text_lower = sentence.lower()
        
        # Strategy 1: Look for indicator phrases
        indicators = [
            'the key is', 'the most important', 'what matters most',
            'the problem is', 'the solution is', 'remember that',
            'the truth is', 'in reality', 'the fact is',
            'this is crucial', 'what\'s important', 'the main point',
            'the bottom line', 'the takeaway', 'the lesson',
            'what we\'re going to do', 'the goal is', 'the hope is',
            'the question is', 'the answer is', 'the point is',
            'what this means', 'the idea is', 'the concept is',
            'important to understand', 'worth noting', 'keep in mind'
        ]
        
        for indicator in indicators:
            if indicator in text_lower:
                score += 10
        
        # Strategy 2: Look for action-oriented language
        action_words = ['create', 'build', 'make', 'develop', 'implement', 'design', 'improve', 'recognize', 'learn', 'train', 'feed', 'compute']
        for word in action_words:
            if word in text_lower:
                score += 3
        
        # Strategy 3: Look for contrast/comparison
        contrast_words = ['but', 'however', 'whereas', 'unlike', 'while', 'although', 'rather', 'instead']
        for word in contrast_words:
            if word in text_lower:
                score += 2
        
        # Strategy 4: Longer sentences often contain more detail
        if 50 < len(sentence) < 250:
            score += 1
        
        # Strategy 5: Position bonus - first and last sentences often contain key points
        if i < 3 or i > len(sentences) - 3:
            score += 2
        
        # Strategy 6: Definite/indefinite article starter bonus
        if sentence.startswith(('The ', 'A ', 'An ', 'This ', 'That ', 'These ', 'Those ')):
            score += 1
        
        if score > 0:
            scored.append((score, sentence))
    
    # Sort by score and return top points
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:num_points]]


def create_blog_post(transcript: str, video_id: str) -> str:
    """Create a well-structured blog post from the transcript."""
    sentences = split_into_sentences(transcript)
    clean_text = clean_transcript(transcript)
    
    if not sentences:
        return "# Video Insights & Summary\n\nThe transcript for this video is unavailable or could not be processed.\n"
    
    # Extract key information
    key_points = extract_key_points(sentences, num_points=5)
    
    # Build introduction from early substantive sentences that introduce the topic
    intro_sentences = [s for s in sentences[:12] if len(s) > 50 and not s.lower().startswith(('but', 'and', 'so', 'the goal is', 'what we\'re going to do'))]
    if not intro_sentences:
        intro_sentences = [s for s in sentences[:8] if len(s) > 40]
    introduction = intro_sentences[0] if intro_sentences else "This post summarizes key insights from a recent video."
    
    # Build the blog post
    blog = "# Video Insights & Summary\n\n## Overview\n\n" + introduction + "\n\n"
    
    # Group key points into thematic sections for better structure
    if len(key_points) >= 2:
        blog += "## Key Points\n\n"
        # Pair key points into sections where possible
        paired = []
        for i in range(0, len(key_points), 2):
            if i + 1 < len(key_points):
                paired.append((key_points[i], key_points[i+1]))
            else:
                paired.append((key_points[i], None))
        
        for idx, (point1, point2) in enumerate(paired, 1):
            blog += f"**{idx}. {point1}**\n"
            if point2:
                blog += f"{point2}\n\n"
            else:
                blog += "\n"
    else:
        blog += "## Key Takeaways\n\n"
        for i, point in enumerate(key_points, 1):
            if point and len(point) > 20:
                blog += f"{i}. {point}\n"
        blog += "\n"
    
    blog += "## Discussion\n\n"
    
    # Build body from key points with nearby supporting context
    if clean_text:
        used_indices = set()
        body_paragraphs = []
        
        for point in key_points:
            if len(point) < 20:
                continue
            try:
                point_idx = next(i for i, s in enumerate(sentences) if s == point)
            except StopIteration:
                continue
            
            paragraph_sentences = [point]
            used_indices.add(point_idx)
            
            # Collect 1-2 sentences after the point for context
            for j in range(point_idx + 1, min(point_idx + 3, len(sentences))):
                if j not in used_indices and len(sentences[j]) > 30:
                    paragraph_sentences.append(sentences[j])
                    used_indices.add(j)
            
            # Collect 0-1 sentences before the point for lead-in
            for j in range(point_idx - 1, max(point_idx - 2, -1), -1):
                if j not in used_indices and len(sentences[j]) > 30:
                    paragraph_sentences.insert(0, sentences[j])
                    used_indices.add(j)
            
            paragraph = ' '.join(paragraph_sentences)
            if paragraph not in body_paragraphs:
                body_paragraphs.append(paragraph)
        
        # Add 1-2 fallback paragraphs from remaining content if needed
        if len(body_paragraphs) < 2:
            fallback = []
            for i, sentence in enumerate(sentences):
                if i not in used_indices and len(sentence) > 40:
                    fallback.append(sentence)
                    used_indices.add(i)
                    if len(fallback) >= 2:
                        break
            if fallback:
                body_paragraphs.append(' '.join(fallback))
        
        for para in body_paragraphs[:5]:
            blog += para + '\n\n'
    
    blog += "## Conclusion\n\n"
    
    # Find a substantive concluding sentence from the end of the transcript
    conclusion_candidates = [s for s in sentences[-12:] if len(s) > 40 and not s.lower().startswith(('but', 'and', 'so', 'the goal is'))]
    if conclusion_candidates:
        conclusion = conclusion_candidates[-1]
    else:
        # Use the highest-scoring key point as a closing thought
        conclusion = key_points[0] if key_points else "This video explored an important topic in depth."
    
    blog += conclusion + "\n\n---\n*This summary was automatically generated from the video transcript.*\n"
    
    return blog


def create_twitter_thread(transcript: str, max_posts: int = 8) -> list[str]:
    """Create an engaging Twitter/X thread from the transcript."""
    sentences = split_into_sentences(transcript)
    
    if not sentences:
        return ["Transcript unavailable or too short to create a thread."]
    
    selected = []
    
    # 1. Hook: find an engaging, self-contained opening statement
    for sentence in sentences[:12]:
        text_lower = sentence.lower()
        if any(word in text_lower for word in [
            'imagine', 'what if', 'think about', 'consider this',
            'here\'s the thing', 'the truth is', 'what matters',
            'the problem', 'the solution', 'the key', 'important',
            'surprising', 'secret', 'strategy', 'create',
            'build', 'design', 'change', 'success', 'fail', 'learn',
            'appreciate', 'crazy', 'daunting', 'cool', 'pretty cool'
        ]):
            if 60 < len(sentence) < 240 and not any(s == sentence for s in selected):
                selected.append(sentence)
                break
    
    # 2. Body: select explanatory sentences that add new information
    # Avoid sentences that are too similar to already selected ones
    for sentence in sentences:
        if len(selected) >= max_posts - 1:
            break
        text_lower = sentence.lower()
        if any(word in text_lower for word in [
            'but', 'however', 'whereas', 'unlike', 'while', 'rather',
            'means', 'represents', 'corresponds', 'picks up', 'recognize',
            'detect', 'combine', 'break down', 'layer', 'abstract'
        ]):
            if 60 < len(sentence) < 240 and sentence not in selected:
                # Avoid near-duplicates by checking first 40 chars
                existing_starts = [s[:40] for s in selected]
                if sentence[:40] not in existing_starts:
                    selected.append(sentence)
    
    # 3. Closing: find a substantive closing statement, not a fragment
    closing_keywords = [
        'next', 'future', 'follow', 'stay', 'thank', 'hope',
        'learn more', 'resources', 'watch', 'see', 'dig',
        'challenge', 'assumptions', 'space', 'possible'
    ]
    for sentence in reversed(sentences[-12:]):
        if len(selected) >= max_posts:
            break
        text_lower = sentence.lower()
        if any(word in text_lower for word in closing_keywords):
            if 50 < len(sentence) < 240 and sentence not in selected:
                selected.append(sentence)
                break
    
    # 4. Fallback: if still short, add diverse substantive sentences
    if len(selected) < 3:
        seen_starts = set()
        for sentence in sentences:
            if len(sentence) > 80 and sentence not in selected:
                start = sentence[:40]
                if start not in seen_starts:
                    selected.append(sentence)
                    seen_starts.add(start)
                if len(selected) >= max_posts:
                    break
    
    # Ensure we have posts, limit to max_posts
    posts = selected[:max_posts]
    
    # Filter out any posts that are clearly fragments or too short
    posts = [p for p in posts if len(p) >= 50]
    
    # Ensure we have at least one post
    if not posts and sentences:
        posts = [sentences[0]]
    
    return posts


def extract_key_quotes(transcript: str, max_quotes: int = 5) -> list[str]:
    """Extract notable, quotable sentences from the transcript."""
    sentences = split_into_sentences(transcript)
    
    # Score sentences based on quotability
    scored = []
    
    for sentence in sentences:
        score = 0
        text_lower = sentence.lower()
        
        # Quotable phrases
        if any(phrase in text_lower for phrase in [
            'the truth is', 'what matters', 'the key is', 'remember',
            'the problem is', 'the solution', 'the secret', 'the strategy',
            'in reality', 'the fact is', 'the bottom line', 'the takeaway',
            'the most important', 'the lesson', 'what i learned', 'the reality'
        ]):
            score += 10
        
        # Actionable advice
        if any(word in text_lower for word in ['create', 'build', 'make', 'do', 'start', 'stop', 'avoid']):
            score += 3
        
        # Good length for quotes
        if 60 < len(sentence) < 200:
            score += 2
        
        # Memorable structure
        if sentence.startswith(('The ', 'What ', 'Why ', 'How ', 'If ', 'Don\'t ', 'Never ', 'Always ')):
            score += 2
        
        if score > 0:
            scored.append((score, sentence))
    
    # Sort and return top quotes
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:max_quotes]]


def create_summary(transcript: str, max_length: int = 500) -> str:
    """Create a concise summary of the video using the most important sentences."""
    sentences = split_into_sentences(transcript)
    if not sentences:
        return "Transcript unavailable or too short to summarize."

    # Score all sentences for importance
    key_points = extract_key_points(sentences, num_points=min(8, len(sentences)))
    key_set = set(key_points)

    scored = []
    for i, sentence in enumerate(sentences):
        score = 0
        text_lower = sentence.lower()

        # Boost sentences that are also key points
        if sentence in key_set:
            score += 15

        # Indicator phrases
        indicators = [
            'the key is', 'the most important', 'what matters most',
            'the problem is', 'the solution is', 'remember that',
            'the truth is', 'in reality', 'the fact is',
            'this is crucial', 'what\'s important', 'the main point',
            'the bottom line', 'the takeaway', 'the lesson',
            'what we\'re going to do', 'the goal is', 'the hope is',
            'the question is', 'the answer is', 'the point is',
            'what this means', 'the idea is', 'the concept is',
            'important to understand', 'worth noting', 'keep in mind'
        ]
        for indicator in indicators:
            if indicator in text_lower:
                score += 8

        # Action-oriented language
        action_words = ['create', 'build', 'make', 'develop', 'implement', 'design', 'improve', 'recognize', 'learn', 'train', 'feed', 'compute']
        for word in action_words:
            if word in text_lower:
                score += 3

        # Contrast/comparison
        contrast_words = ['but', 'however', 'whereas', 'unlike', 'while', 'although', 'rather', 'instead']
        for word in contrast_words:
            if word in text_lower:
                score += 2

        # Good length for summary sentences
        if 40 < len(sentence) < 220:
            score += 1

        # No position bonus for summary - avoid just picking intro sentences

        if score > 0:
            scored.append((score, i, sentence))

    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Select diverse sentences across the transcript
    selected = []
    seen_starts = set()
    
    # Always include the top-scoring sentence if it is substantive
    if scored:
        top = scored[0]
        if top[2] not in selected:
            selected.append(top[2])
            seen_starts.add(top[2][:40])
    
    # Add one strong sentence from early, middle, and late sections
    quarter = len(sentences) // 4
    sections = [
        (quarter, quarter * 2),
        (quarter * 2, quarter * 3),
        (quarter * 3, len(sentences))
    ]
    for start, end in sections:
        candidates = [(score, idx, s) for score, idx, s in scored if start <= idx < end and s not in selected and s[:40] not in seen_starts]
        if candidates:
            selected.append(candidates[0][2])
            seen_starts.add(candidates[0][2][:40])
    
    # Fill remaining slots with highest-scoring unused sentences
    for score, idx, sentence in scored:
        if len(selected) >= 6:
            break
        if sentence not in selected and sentence[:40] not in seen_starts:
            selected.append(sentence)
            seen_starts.add(sentence[:40])
    
    # Sort selected sentences by their original position in the transcript
    selected_ordered = []
    for sentence in selected:
        idx = next(i for i, s in enumerate(sentences) if s == sentence)
        selected_ordered.append((idx, sentence))
    selected_ordered.sort(key=lambda x: x[0])
    selected = [s for _, s in selected_ordered]

    # Build summary text
    summary = '. '.join(selected)
    if summary and not summary.endswith('.'):
        summary += '.'

    # Enforce max length
    if len(summary) > max_length:
        summary = summary[:max_length-3].rsplit('.', 1)[0] + '...'

    return summary


def generate_all_formats(video_url: str, output_dir: Path, languages: list | None = None):
    """Generate all content formats from a YouTube video."""
    
    # Extract video ID
    match = re.search(r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})', video_url)
    if not match:
        raise ValueError(f"Could not extract video ID from URL: {video_url}")
    video_id = match.group(1)
    
    print(f"Fetching transcript for video: {video_id}")
    raw_transcript = fetch_transcript(video_id, languages)
    print(f"Transcript fetched: {len(raw_transcript)} characters")
    
    # Clean the transcript
    transcript = clean_transcript(raw_transcript)
    print(f"Cleaned transcript: {len(transcript)} characters")
    
    # Fallback to raw transcript if cleaning removed everything
    if not transcript and raw_transcript:
        transcript = raw_transcript
        print("Cleaning produced empty text; falling back to raw transcript.")
    
    # Content warnings
    warnings = []
    music_artifacts = len(re.findall(r'\[♪+.*?♪+\]|♪.*?♪', raw_transcript, re.DOTALL))
    if music_artifacts > 3:
        warnings.append("This video appears to contain music or copyrighted audio content. Review for copyright restrictions before delivering to clients.")
    
    if len(transcript) < 500:
        warnings.append("Transcript is very short. Output quality may be limited.")
    
    if not warnings:
        warnings.append("No issues detected.")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate formats
    print("\nGenerating content formats...")
    
    # 1. Blog post
    blog = create_blog_post(transcript, video_id)
    blog_path = output_dir / "blog_post.md"
    blog_path.write_text(blog, encoding='utf-8')
    print(f"✓ Blog post: {blog_path}")
    
    # 2. Twitter thread
    thread = create_twitter_thread(transcript)
    thread_path = output_dir / "twitter_thread.md"
    with open(thread_path, 'w', encoding='utf-8') as f:
        f.write("# Twitter/X Thread\n\n")
        for i, post in enumerate(thread, 1):
            f.write(f"**Tweet {i}** ({len(post)} chars)\n\n{post}\n\n---\n\n")
    print(f"✓ Twitter thread: {thread_path}")
    
    # 3. Key quotes
    quotes = extract_key_quotes(transcript)
    quotes_path = output_dir / "key_quotes.md"
    with open(quotes_path, 'w', encoding='utf-8') as f:
        f.write("# Key Quotes\n\n")
        for i, quote in enumerate(quotes, 1):
            f.write(f'{i}. "{quote}"\n\n')
    print(f"✓ Key quotes: {quotes_path}")
    
    # 4. Summary
    summary = create_summary(transcript)
    summary_path = output_dir / "summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# Video Summary\n\n{summary}\n")
    print(f"✓ Summary: {summary_path}")
    
    # 5. Raw transcript
    raw_path = output_dir / "transcript.txt"
    raw_path.write_text(transcript, encoding='utf-8')
    print(f"✓ Raw transcript: {raw_path}")
    
    # 6. Content warnings
    warnings_path = output_dir / "warnings.txt"
    with open(warnings_path, 'w', encoding='utf-8') as f:
        f.write("Content Warnings\n\n")
        for warning in warnings:
            f.write(f"- {warning}\n")
    print(f"✓ Warnings: {warnings_path}")
    
    # Create package info
    info = {
        "video_id": video_id,
        "transcript_length": len(transcript),
        "formats_generated": ["blog_post.md", "twitter_thread.md", "key_quotes.md", "summary.md", "transcript.txt", "warnings.txt"],
        "output_directory": str(output_dir),
        "warnings": warnings
    }
    info_path = output_dir / "package_info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    print(f"✓ Package info: {info_path}")
    
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Content Repurposing Service v2 - Generate multiple content formats from a video"
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument(
        "--output", "-o",
        default=str(Path.home() / "youtube_content_output"),
        help="Output directory (default: ~/youtube_content_output)"
    )
    parser.add_argument(
        "--language", "-l",
        default="en",
        help="Comma-separated language codes (default: en)"
    )
    parser.add_argument(
        "--text",
        help="Path to a transcript text file to process directly (skips YouTube fetch)"
    )
    
    args = parser.parse_args()
    
    languages = [l.strip() for l in args.language.split(",")]
    output_dir = Path(args.output)
    
    try:
        if args.text:
            transcript_path = Path(args.text)
            if not transcript_path.exists():
                print(f"Error: transcript file not found: {transcript_path}", file=sys.stderr)
                sys.exit(1)
            raw_transcript = transcript_path.read_text(encoding="utf-8")
            video_id = "text_input"
            transcript = clean_transcript(raw_transcript)
            if not transcript and raw_transcript:
                transcript = raw_transcript
            warnings = []
            music_artifacts = len(re.findall(r'\[♪+.*?♪+\]|♪.*?♪', raw_transcript, flags=re.DOTALL))
            if music_artifacts > 3:
                warnings.append("The transcript appears to contain music or copyrighted audio content markers.")
            if len(transcript) < 500:
                warnings.append("Transcript is very short. Output quality may be limited.")
            if not warnings:
                warnings.append("No issues detected.")
        else:
            if not args.url:
                parser.error("provide a YouTube URL or use --text <transcript_file>")
            result_dir = generate_all_formats(args.url, output_dir, languages)
            print(f"\n✅ Success! All content formats generated in:")
            print(f"   {result_dir}")
            print(f"\nYou can now:")
            print(f"  1. Review the generated content")
            print(f"  2. Edit and customize it")
            print(f"  3. Deliver to a client")
            print(f"  4. Package multiple videos for a content repurposing service")
            return
        
        # Shared output generation for transcript-only mode
        print(f"Processing transcript: {transcript_path}")
        print(f"Transcript length: {len(raw_transcript)} characters")
        print(f"Cleaned transcript: {len(transcript)} characters")
        print("\nGenerating content formats...")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        blog = create_blog_post(transcript, video_id)
        blog_path = output_dir / "blog_post.md"
        blog_path.write_text(blog, encoding="utf-8")
        print(f"✓ Blog post: {blog_path}")
        
        thread = create_twitter_thread(transcript)
        thread_path = output_dir / "twitter_thread.md"
        with open(thread_path, 'w', encoding='utf-8') as f:
            f.write("# Twitter/X Thread\n\n")
            for i, post in enumerate(thread, 1):
                f.write(f"**Tweet {i}** ({len(post)} chars)\n\n{post}\n\n---\n\n")
        print(f"✓ Twitter thread: {thread_path}")
        
        quotes = extract_key_quotes(transcript)
        quotes_path = output_dir / "key_quotes.md"
        with open(quotes_path, 'w', encoding='utf-8') as f:
            f.write("# Key Quotes\n\n")
            for i, quote in enumerate(quotes, 1):
                f.write(f'{i}. "{quote}"\n\n')
        print(f"✓ Key quotes: {quotes_path}")
        
        summary = create_summary(transcript)
        summary_path = output_dir / "summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# Video Summary\n\n{summary}\n")
        print(f"✓ Summary: {summary_path}")
        
        raw_path = output_dir / "transcript.txt"
        raw_path.write_text(transcript, encoding='utf-8')
        print(f"✓ Cleaned transcript: {raw_path}")
        
        warnings_path = output_dir / "warnings.txt"
        with open(warnings_path, 'w', encoding='utf-8') as f:
            f.write("Content Warnings\n\n")
            for warning in warnings:
                f.write(f"- {warning}\n")
        print(f"✓ Warnings: {warnings_path}")
        
        info = {
            "video_id": video_id,
            "transcript_length": len(transcript),
            "formats_generated": ["blog_post.md", "twitter_thread.md", "key_quotes.md", "summary.md", "transcript.txt", "warnings.txt"],
            "output_directory": str(output_dir),
            "warnings": warnings,
            "mode": "transcript-only"
        }
        info_path = output_dir / "package_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        print(f"✓ Package info: {info_path}")
        print(f"\n✅ Success! All content formats generated in:")
        print(f"   {output_dir}")
        print(f"\nYou can now:")
        print(f"  1. Review the generated content")
        print(f"  2. Edit and customize it")
        print(f"  3. Deliver to a client")
        print(f"  4. Package multiple videos for a content repurposing service")
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
