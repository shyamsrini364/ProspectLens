# Codex instructions — ProspectLens

When working in this repository, read `DESIGN_SYSTEM.md` before changing UI. Use `tokens.css` as the source of truth for colour, spacing, type, radii, shadows and theme-specific styling. See `preview.html` for a self-contained illustrative UI sample.

## Mandatory conventions
- New ProspectLens UI must conform to **Celestial Pearl** in light mode and **Pearl Nocturne** in dark mode.
- Use semantic CSS custom properties (`--pl-*`) rather than embedding hex colours in components.
- Implement theme switching via `[data-theme="light"]` / `[data-theme="dark"]` on an app wrapper or root. Follow the host app's established theme mechanism if one exists, mapping semantic values appropriately.
- Use Lexend for headings and Inter for interface/body text with fallback stacks.
- Use 8px-derived spacing, 22px standard card radius, 28px hero radius and 14–16px control radius.
- Employ atmospheric gradients and glass effects selectively; keep data tables and busy content on readable, mostly opaque surfaces.
- AI insight panels may use faint lens arcs and glow. Ordinary cards should not all receive decorative lens effects.
- Keep light/dark components structurally identical; do not make one mode a different product.
- Ensure contrast, keyboard focus, reduced-motion support and semantic labels.
- Do not overwrite existing app logic, data fetching, routes, or product behaviour in the name of a redesign.

## Workflow for UI tasks
1. Inspect the existing app framework/components and current theme strategy.
2. Read `DESIGN_SYSTEM.md` and `tokens.css`; identify needed semantic mappings.
3. Extend/reuse shared components rather than styling pages independently.
4. Implement and test both themes (including empty/loading/error states where relevant).
5. Validate responsive behaviour, focus rings, contrast and readability.
6. In your summary, identify any deviations from the design system and why they were needed.

## Screen priorities
- Dashboard overview: metrics, opportunity cards, charts, AI Lens Insights and recent activity.
- Prospect Explorer: density, scanning and filtering above atmospheric decoration.
- Prospect Detail: clear research hierarchy and actionable signals.

## Do not
- Introduce unrelated vivid colours as branding.
- Reproduce the reference personal assistant UI or its blue gradient verbatim.
- Turn every panel into transparent glass.
- Ship unreadable lavender-on-lavender text or dark-mode contrast failures.
- Invent real prospect insights or imply demo metrics are production data.
