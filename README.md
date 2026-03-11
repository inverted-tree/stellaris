<div align="center">
    <h1>stellaris.</h1>
    <p>A minimal Hugo theme for technical writing.</p>
</div>

Stellaris is built around two content types: standalone posts and multi-part project series. It includes a bento-grid home page, a scrolling projects ticker, KaTeX math rendering, syntax highlighting, and a contextual sidebar navigation that reflects the current page's location in the content hierarchy.

**Requirements:** Hugo 0.146.0 or later (standard build, extended not required).

## Getting Started

1. Copy the theme files into your Hugo site, or use this repository as a starting point.
2. Set your `baseURL` and `title` in `hugo.toml`.
3. Create content in `content/posts/` and `content/projects/`.
4. Run `hugo server` to preview locally.

## Content Structure

Stellaris organizes content into two sections:

```
content/
  posts/
    _index.md          # Section index (title, description)
    my-post.md         # Standalone post
  projects/
    _index.md          # Section index
    my-project/
      _index.md        # Project index (title, description, weight)
      01-intro.md      # First post in the series
      02-details.md    # Second post
```

### Standalone Posts

Posts in `content/posts/` appear in the posts feed and on the home page. They are independent — no series strip is shown.

```toml
---
title = 'My Post'
date = '2025-01-15'
draft = false
description = 'A short summary shown in post lists.'
tags = ['rust', 'graphics']
math = false
---
```

Set `math = true` to enable KaTeX rendering on that page.

### Project Series

A project is a subdirectory under `content/projects/`. Each project has an `_index.md` that defines the project metadata, and any number of post files that form the series.

**Project index (`_index.md`):**
```toml
---
title = 'Ray Tracer'
description = 'Building a ray tracer from scratch in Rust.'
weight = 10
draft = false
---
```

**Project post:**
```toml
---
title = 'Sphere Intersection'
date = '2025-02-01'
draft = false
description = 'Implementing the ray–sphere intersection test.'
tags = ['rust', 'math']
---
```

Posts within a project automatically display a series strip at the bottom of each page, listing all other posts in the project with their dates. The strip only appears when the project contains more than one post.

Use `weight` on the project `_index.md` to control the order projects appear in navigation and on the home page.

### Posts with Assets

To include images or other files alongside a post, use a leaf bundle:

```
content/posts/
  my-post/
    index.md
    photo.jpg
```

Reference the image in your markdown as `![Alt text](photo.jpg)`.

## Math Rendering

Stellaris bundles KaTeX for self-hosted math rendering. Enable it per-page with `math = true` in the front matter.

Supported delimiters:

| Style | Delimiter |
|---|---|
| Inline | `$...$` or `\(...\)` |
| Block | `$$...$$` or `\[...\]` |

The math partial loads KaTeX only on pages where it is needed.

## Shortcodes

### `code`

Renders a syntax-highlighted code block with an optional filename label.

```
{{</* code file="src/main.rs" lang="rust" */>}}
fn main() {
    println!("Hello, world!");
}
{{</* /code */>}}
```

| Parameter | Required | Description |
|---|---|---|
| `lang` | No | Language for syntax highlighting |
| `file` | No | Filename displayed above the block |

When `lang` is omitted, Hugo attempts to detect the language automatically.

## Configuration

All configuration lives in `hugo.toml`. The full set of available parameters is listed below.

### Site

```toml
baseURL = 'https://example.org/'
languageCode = 'en-US'
title = 'My Site'
```

### Theme Parameters

```toml
[params]
  # Displayed below the site title on the home page hero.
  description = 'A site about things I build.'

  # The animated text in the hero typewriter. Omit to show "Built for<br>[heroPrefix]".
  heroTitle = 'your next Hugo site.'

  # Primary accent color. Accepts any CSS color value.
  accentColor = '#6b9cf8'

  # Slug of the project to pin in the featured card on the home page.
  featuredProject = 'my-project'
```

### Labels and Text

Every user-visible string in the theme has a default and can be overridden.

```toml
[params]
  # Navigation
  homeLabel = 'Home'
  tagsLabel = 'Tags'

  # Hero buttons
  heroPrefix         = 'Built for'        # Shown before heroTitle when heroTitle is unset
  heroProjectsLabel  = 'Browse Projects'
  heroPostsLabel     = 'Read Posts'

  # Bento grid (home page cards)
  homeFeaturedLabel    = 'Featured Project'
  homeLatestPostLabel  = 'Latest Post'
  homeRecentPostsLabel = 'Recent Posts'
  homeProjectLabel     = 'Project'
  homeViewAllLabel     = 'View all →'
  homeNoPostsText      = 'No posts yet.'

  # Series strip at the bottom of project posts
  seriesLabel = 'Part of'

  # Footer
  footerText     = 'My Site'
  footerLinkText = 'Built with Hugo'
  footerLinkURL  = 'https://gohugo.io'

  # 404 page
  notFoundTitle    = 'Page not found'
  notFoundMessage  = "The page you're looking for doesn't exist or has been moved."
  notFoundLinkText = 'Go home'
```

Navigation labels for the Projects and Posts sections are read from the section `_index.md` `title` field, so renaming a section in its front matter is enough — no extra param needed.

### Accent Color

`accentColor` accepts any CSS color string. The theme derives hover, dim, and background tints from this value using `color-mix()`, so a single value controls the entire accent palette.

```toml
accentColor = '#f4845f'   # warm orange
accentColor = '#6b9cf8'   # deep-space blue (default)
accentColor = '#7ec8a4'   # muted green
```

### Markup

```toml
[markup.highlight]
  noClasses  = false      # Uses CSS classes for syntax colors; do not change
  codeFences = true
  lineNos    = false      # Set to true to show line numbers in code blocks
  tabWidth   = 2

[markup.tableOfContents]
  startLevel = 2          # H2 and below appear in the TOC
  endLevel   = 4
  ordered    = false
```

## Home Page Layout

The home page consists of a hero section followed by a three-row bento grid.

**Hero:** Displays the site title, an animated typewriter text (`heroTitle`), the site description, and two call-to-action buttons.

**Row 1:** A wide featured project card (set via `featuredProject`) and a narrow latest-post card side by side.

**Row 2:** A full-width recent posts list showing the four most recent posts after the latest post card. Each entry shows the title, date, and description.

**Row 3:** An auto-scrolling ticker showing all projects. The ticker loops seamlessly and slows as the number of projects grows.

## Syntax Highlighting

Syntax colors are defined in `assets/css/main.css` using Hugo's Chroma class names. The palette is Catppuccin-inspired:

| Element | Color |
|---|---|
| Keywords | `#cba6f7` |
| Strings | `#a6e3a1` |
| Comments | `#4d6478` |
| Numbers | `#fab387` |
| Functions | `#89b4fa` |
| Types | `#f9e2af` |

To use a different Chroma theme, replace the `.chroma` rules in `main.css` or generate a new stylesheet with `hugo gen chromastyles --style=monokai > chroma.css` and merge it in.

## Asset Pipeline

In development (`hugo server`), CSS and JS are served without processing. In production (`hugo`), both are minified, fingerprinted, and served with `integrity` attributes for subresource integrity.

KaTeX is fully self-hosted under `static/katex/` and does not load anything from a CDN.

## Customizing Styles

All design tokens are CSS custom properties in the `:root` block at the top of `assets/css/main.css`:

```css
--bg:           #111111;
--bg-sidebar:   #0c0c0c;
--bg-surface:   #181818;
--border:       #272727;
--text:         #c8c8c8;
--text-muted:   #707070;
--heading:      #e8e8e8;

--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;

--r-sm:   3px;
--r-md:   6px;
--r-lg:   10px;
--r-pill: 999px;
```

The `--accent` variable is injected at runtime from `params.accentColor` and should not be set in the CSS file directly.
