# YouTube Content Repurposing Service

Turn YouTube videos into blog posts, Twitter threads, and social media content.

## Local Testing

```bash
# Run the service
double-click run_service.bat

# Or from command line
python youtube_repurposer.py "https://www.youtube.com/watch?v=VIDEO_ID" --output ./output
```

## Files

- `youtube_repurposer.py` - Main automation script
- `run_service.bat` - Windows launcher
- `landing_page.html` - Public landing page
- `docs/` - SEO articles and guides
- `portfolio/` - Sample deliverables

## Requirements

- Python 3.8+
- youtube-transcript-api
- Windows (tested), also works on macOS/Linux

## Deployment

This site is configured for GitHub Pages. To deploy:

1. Create a new public GitHub repository named `youtube-repurposing-service` (or your preferred name)
2. Push these files to the repository's `main` branch
3. Enable GitHub Pages in repository settings (Settings → Pages → Source: `main` branch)
4. Your site will be live at `https://<your-username>.github.io/youtube-repurposing-service/`

## License

MIT
