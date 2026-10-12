# ProspectLens Design System — v1.0

**Visual identity:** Ambient Intelligence  
**Default theme:** Celestial Pearl  
**Dark theme:** Pearl Nocturne

## Product intent
ProspectLens is an AI-powered prospect intelligence workspace for sales professionals, founders, consultants, and business development teams. It should feel calm, luminous and sophisticated at first glance, and precise, fast and useful during serious prospecting work. Avoid generic CRM visual density and decorative glass effects that compromise usability.

## Immutable brand anchors
1. Light-mode palette is **Celestial Pearl**; dark-mode palette is **Pearl Nocturne**.
2. Design language: pearlescent atmosphere, restrained glass, floating precision, subtle lens illumination.
3. Headings use **Lexend**; dense UI/body use **Inter**, with sensible fallbacks.
4. Stable spacing and typographic hierarchy are more important than decoration.
5. Light and dark themes share layout, component dimensions and information architecture.

## Colour tokens
Use semantic variables from `tokens.css`, not hardcoded colour values in components.

| Role | Celestial Pearl (light) | Pearl Nocturne (dark) |
|---|---|---|
| Canvas | `#F1F2FC` | `#171D35` |
| Atmospheric mist | `#C7D4F8` | `#333A5D` |
| Solid surface | `#FFFFFF` | `#252B46` |
| Foreground | `#2B3555` | `#F4F1FF` |
| Brand primary | `#6476B7` | `#A4B8F7` |
| Orchid accent | `#C0AEED` | `#C6A9EB` |

Extended tokens (muted text, borders, interactions, chart colours and semantic statuses) are pragmatic implementation choices defined in CSS. Validate contrast before production.

Leading bars use one consistent accent across both lenses: deep berry `#A12B83`
in light mode and Luminous Apricot `#FFD08A` in dark mode. Both `survey-highlight`
and the legacy `survey-iris` token map to this accent. Standard bars remain
periwinkle; category palettes, quadrant fills and heatmap intensity scales retain
their separate meanings. Trend series use periwinkle, the shared accent and teal
so different series do not collapse into the same colour.

AI-adoption charts and their legends share these category tokens. Use the active
theme's values consistently across industries; keep legend and hover text in the
foreground colour. Heatmaps use the separate intensity tokens because their
colour represents a percentage rather than an adoption category.

| Category token | Celestial Pearl | Pearl Nocturne |
|---|---|---|
| `--pl-ai-regular` | `#6476B7` | `#A4B8F7` |
| `--pl-ai-specific` | `#A779D0` | `#C6A9EB` |
| `--pl-ai-experimented` | `#2F969C` | `#65C5C4` |
| `--pl-ai-not-using` | `#AC7887` | `#D19BAA` |
| `--pl-ai-unsure` | `#CA923F` | `#D5A76E` |

## Surfaces & depth
- App canvas: subtle pearlescent radial gradients on a stable base colour; never distract from data.
- Standard cards: nearly opaque surfaces for readability (`--pl-surface`).
- Glass: optional, typically large hero/AI insight containers and floating navigation. Use backdrop blur **16–24px**, a subtle tinted border and low-opacity shadow.
- Never put long tables over busy gradients. Prefer solid surfaces for prospect lists, forms and detail panes.
- Avoid overly bright neon, heavy drop shadows, thick borders, gratuitous frosted effects.

## Component foundations
- Hero panel radius: **28px**.
- Standard card radius: **22px**.
- Button/input radius: **14–16px**.
- Pills: **999px**.
- Spacing rhythm: **8px scale** (`4, 8, 12, 16, 24, 32, 48, 64`).
- Focus: visible two-pixel outline or ring using semantic focus token.
- Hover: restrained lift and surface tint; transitions ~**180–240ms**; honour `prefers-reduced-motion`.
- Charts: muted base series, periwinkle primary, orchid secondary; semantic status colours must remain distinguishable.

## Typography
- Display / headings: `Lexend`, weights **500–600**.
- Body / data / UI: `Inter`, weights **400–600**.
- Numeric metrics: tabular numerals.
- Desktop hierarchy suggestion: page heading 28–32px; section heading 17–20px; card title 14–16px; body 14px; secondary metadata 12–13px. Do not use tiny, low-contrast copy.

## Signature brand motifs
**Lens Illumination:** Soft radial glow plus faint concentric arcs around search, AI insights and prospect scores only. Ring opacity should remain exceptionally subtle. Never add a lens ring behind every card.

**Pearlescent Glass:** Carefully differentiated elevations: background, panel, surface, overlay; maintain crisp content.

**Floating Precision:** Rounded nav and large containers contrast with exact table alignments, consistent metrics and clean row boundaries.

## Navigation & screen patterns
- Desktop: slim floating navigation or floating pill bar, whichever matches the app's current information architecture. Do not force a new navigation pattern if it undermines actual workflows.
- Overview: welcome/summary, 4 KPIs, prioritised opportunities, 6-month discovery trend, AI Lens Insights, recent activity.
- Prospect Explorer: high-density yet legible prospect table, search, filters, fit signals, sortable columns, saved views.
- Prospect Detail: company identity and key attributes, fit score, cited buying signals, suggested next steps, timeline/notes.
- AI Lens Insights: a visually identifiable yet readable insight container, with a clear primary action and explanation of why each prospect is recommended.

## Accessibility and quality gates
- Target **WCAG AA** contrast for normal text (4.5:1) and larger text (3:1), including dark mode; adjust extended tokens as necessary.
- Functional focus-visible for all controls; keyboard-accessible navigation and menu states.
- Never convey lead quality or status through colour alone; pair colours with labels/icons.
- Support dark mode and reduced motion, and check responsive layouts at 1440px, 1024px, 768px and 390px.
- Ensure buttons/inputs/tables remain functional; do not use screenshots as implementations.

## Fixed vs adaptable
**Fixed:** brand palette anchors; theme names; typography pairing; restrained luminous aesthetic; signature lens motif; radii/spacing approach.

**Adaptable:** exact navigation placement, information architecture within user requirements, chart library, component framework, breakpoint choices and optional interactions. Preserve existing business logic, accessibility and workflow conventions when integrating.

## Mock-data policy
Example numbers such as 2,847 prospects, 126 high-fit prospects and $84k pipeline are placeholders for demonstration only. Never present them as real customer data.
