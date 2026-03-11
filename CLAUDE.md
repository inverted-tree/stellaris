# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Stellaris is a Hugo theme for technical writing and blogging. It's distributed as a Hugo module (no compilation step). The example site lives in the repo root alongside the theme files.

## Development Commands

```bash
# Start local dev server
hugo server

# Production build
hugo --minify

# Update Hugo module dependencies
hugo mod get -u
```

Requirements: Hugo >= 0.146.0 (standard build, extended NOT required), Go (for module management).

## Architecture

Hugo theme structure with these key areas:

**Layouts** (`/layouts/`): Templates drive all rendering.
- `baseof.html` — top-level shell (header + sidebar + main + footer)
- `home.html` — bento grid homepage (featured project, latest post, posts list, project ticker)
- `page.html` — individual post/article with optional series strip
- `section.html` — section index showing subsection cards + post lists
- `_partials/` — reusable fragments (head, header, sidebar, toc, math, project-posts)
- `shortcodes/code.html` — syntax-highlighted code block with optional filename label

**Assets** (`/assets/`): Processed by Hugo Pipes.
- `css/main.css` — all styles (~1500 lines); uses CSS custom properties for theming
- `js/main.js` — TOC scroll highlighting via IntersectionObserver

**Content model**: Two content types:
- `/content/posts/` — standalone posts (flat)
- `/content/projects/<slug>/` — project series; `_index.md` defines the project, numbered files are the posts. A "series strip" appears on posts when a project has 2+ entries.

## Key Configuration (`hugo.toml`)

Notable `[params]`:
- `accentColor` — CSS accent color (hex)
- `featuredProject` — slug of the project pinned in the homepage bento grid
- `fontSans` / `fontMono` — font family names (must be available in `/static/fonts/` or system)
- `heroTitle` — text after "your next" on the homepage hero

Syntax highlighting uses Chroma with `noClasses = false` — highlight classes map to CSS tokens defined in `main.css`. Math rendering uses self-hosted KaTeX (opt-in per page with `math = true` in front matter).

## Styling Conventions

- All colors, spacing, and typography via CSS custom properties on `:root`
- Responsive breakpoints: ≤1199px drops TOC, ≤767px collapses sidebar to overlay drawer (CSS-only via `:has()`)
- Catppuccin-inspired syntax token palette defined in `main.css`
- No external CDNs — fonts and KaTeX are fully self-hosted in `/static/`
