# User Interface Guidelines

Date: 2026-02-22  
Project: BuzzPoint Pages  
Status: Active implementation baseline

---

## Navigation Rules

1. Navigation labels render in Title Case (first letter uppercase).
2. Top navigation supports a maximum of 5 page links.
3. Theme mode icon is always present and is not counted as a page link.
4. If exported navigation has more than 5 links:
   - First 4 links render directly.
   - The 5th top-nav item is rendered as a dropdown trigger.
   - Dropdown shows up to 5 overflow links.
   - If overflow exceeds 5, the final dropdown link is `More` pointing to `/pages`.
5. `Events` link route is forced to `/<orgId>/calendar`.

## Home Section Rules

1. Home content sections render from `site.Data.home.sections`.
2. Source file for SiteCMS export is `data/home/sections.yaml`.
3. Sections are sorted by `order`.
4. Sections with `active != true` are skipped.
5. `columns` controls section mode:
   - `1` = single column
   - `2` = two-column split layout
6. `layout` controls two-column behavior:
   - `image_left_content_right`
   - `content_left_image_right`
   - `image_left_image_right`
   - `content_left_content_right`
7. `left` and `right` side payloads are used for split sections when present.
8. Side `type` supports:
   - `image`
   - `content`
9. `items` is the repeatable list payload for section root and/or side payload.
10. `config` is optional per-section renderer configuration.
11. If no sections are present, no placeholder content is auto-generated.

## Hero Rules

1. Hero renders from exported data only.
2. Hero supports single-image or multi-slide carousel.
3. Multi-slide hero uses vanilla JS (no jQuery) with indicator dots.
4. Hero is constrained to `main.page-main` width and sits directly under header border.

## Branding Color Rules

1. Brand colors are sourced from export metadata:
   - `site.Data.meta.site.settings.theme.primaryColor`
   - `site.Data.meta.site.settings.theme.accentColor`
   - with fallback to `site.Data.meta.site.org.branding.*`
2. Header navigation links use the brand primary color in light mode.
3. Dark mode keeps accessibility contrast by using brand accent for nav links/icon.
4. Footer background uses brand primary and footer text/icons use brand accent.

## Footer Rules

1. Footer minimum height is `300px`.
2. Footer links are always underlined and include a hover emphasis state.
3. If social URLs are present in exported org data, render icon links.
4. Social icons use the same inline SVG icon style family as theme icons.
