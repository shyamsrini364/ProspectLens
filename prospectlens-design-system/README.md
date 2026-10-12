# ProspectLens — Codex design reference

This package is the agreed ProspectLens **Celestial Pearl / Pearl Nocturne** design system.

## Files
- `AGENTS.md` — Codex instructions and UI implementation conventions.
- `DESIGN_SYSTEM.md` — brand rationale, semantic roles, components and design rules.
- `tokens.css` — ready-to-use light/dark CSS tokens and utility classes.
- `preview.html` — open in a browser for a sample dashboard and working theme toggle (illustrative data).

## How to give it to Codex
1. Copy `AGENTS.md`, `DESIGN_SYSTEM.md` and `tokens.css` to the root of your ProspectLens repository. Optionally put `preview.html` in `design/` (update its CSS link if relocated).
2. Ask Codex: **“Read AGENTS.md and DESIGN_SYSTEM.md. Use tokens.css to implement the ProspectLens design system across the existing app. Start by inspecting our component architecture and theme setup; preserve business logic. Implement Celestial Pearl light mode and Pearl Nocturne dark mode and test both.”**
3. Review both themes before rolling the styling out to every screen.

Do not replace your app's framework, existing workflows, or real data with the static preview. Fonts in `tokens.css` load from Google Fonts if internet is available; bundle or use local equivalents if your environment requires offline/self-hosted assets.
