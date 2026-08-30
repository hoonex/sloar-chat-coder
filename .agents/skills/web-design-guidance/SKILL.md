---
name: web-design-guidance
description: Design, build, or review user-facing web UI with repository-aware visual direction, reusable design-system discovery, responsive and accessible interaction states, anti-generic-AI heuristics, and rendered visual verification. Use for substantial web UI/UX work unless the repository or user explicitly supplies a stronger design workflow. Repository and user design rules always win.
license: MIT
metadata:
  version: "0.7.0"
---

# Web Design Guidance Companion

This is an optional design-engineering companion bundled with Sloar Chat Coder. Sloar owns repository continuity, exact state, recovery, verification evidence, and publication safety. This companion owns only **web UI design reasoning and visual acceptance guidance**.

Use it for substantial user-facing web work: new pages, redesigns, dashboards, landing pages, auth/onboarding, settings, navigation, responsive shells, component systems, or visual/interaction audits. Do not activate it for backend-only work, trivial copy edits, or when the repository already defines a more specific design workflow that fully covers the task.

## Precedence

Design decisions follow this order:

```text
explicit user direction
> repository design rules / design system / brand guidance
> shipped UI patterns, tokens, components, assets
> this companion's fallback guidance
```

Never replace a coherent existing design system merely because another style is fashionable. Never treat a generic design catalog as more authoritative than the product itself.

## 1. Discover before designing

Before a substantial UI change, inspect the repository for durable design evidence:

- `DESIGN.md`, `DESIGN_SYSTEM.md`, brand docs, ADRs, product specs, screenshots, Storybook, component docs;
- CSS variables, Tailwind/theme config, token files, typography setup, icon library, component primitives;
- repeated layout, radius, shadow, density, color, motion, and interaction conventions in shipped screens;
- responsive breakpoints and existing accessibility constraints.

Read [references/design-discovery.md](references/design-discovery.md) for the discovery contract.

Do not create a new persistent design-system document by default. If the repository already owns one, update it only when the task legitimately changes the system. If no design memory exists, keep a compact in-turn Design Read; create durable design documentation only when the user asks or the repository's workflow calls for it.

## 2. Produce a compact Design Read

For new or materially redesigned surfaces, establish these facts before implementation:

```text
surface: product | dashboard | landing | auth/onboarding | settings | content | commerce | other
primary user job:
visual tone:
density: compact | balanced | spacious
existing system to preserve:
signature decision:
responsive risk:
interaction/state risk:
```

The **signature decision** is one intentional visual/compositional choice that makes the surface feel designed rather than assembled from defaults. It can be restrained. Utility-heavy product UI should not invent spectacle merely to be distinctive.

If the user already supplied enough direction, infer the Design Read silently rather than asking a questionnaire. Ask only for a decision that materially blocks implementation.

## 3. Build the system before decoration

Establish or preserve the visual hierarchy in this order:

1. content and user journey;
2. layout/composition and information hierarchy;
3. typography and density;
4. semantic color and contrast;
5. components and interaction states;
6. responsive behavior;
7. motion/material/detail.

Do not use effects to compensate for weak hierarchy. A blur, gradient, large radius, shadow, or animation is not a design system.

Read [references/surface-recipes.md](references/surface-recipes.md) for surface-specific defaults and anti-patterns.

## 4. Anti-generic-AI rules

Avoid the recurring patterns that make unrelated generated products look interchangeable unless the product specifically calls for them:

- defaulting every landing page to text-left / decorative-card-right hero;
- purple/pink glow gradients as generic "AI" branding;
- excessive bento cards when the content has no card-shaped information architecture;
- oversized rounded rectangles around every section;
- glassmorphism used as decoration instead of spatial hierarchy;
- random floating blobs, sparkles, fake charts, or meaningless dashboard widgets;
- using emojis where the repository already has a coherent icon system;
- giant low-information hero whitespace in dense product contexts;
- centering all copy and CTAs by default;
- animating every element independently.

The solution is not to ban a style. Use these patterns when they are justified by product context, existing brand language, or an explicit user request.

## 5. Text and responsive resilience are release criteria

UI must survive real content, not just ideal mock copy.

- headings and labels may wrap naturally across viewport widths and locales;
- long names, URLs, IDs, chips, badges, tables, and buttons must not silently clip essential information;
- components must remain usable under browser zoom and text scaling;
- use wrapping, disclosure, scrolling, truncation with an accessible full-value path, or layout adaptation intentionally;
- test narrow mobile, intermediate/tablet, ordinary desktop, and wide desktop widths appropriate to the repository rather than one screenshot size only;
- do not hard-code a line break solely to make one captured viewport look perfect unless the content itself owns that break.

## 6. Every interactive surface needs states

A polished component is not only its default screenshot. Cover states relevant to the task:

```text
default
hover (where pointer exists)
active/pressed
focus-visible
selected/current
loading
empty
error
success
 disabled (only when semantically necessary)
```

Do not add state variants that the component cannot actually enter. Keyboard and touch behavior are part of the component contract, not optional polish.

## 7. Motion must explain or respond

Motion should communicate causality, continuity, hierarchy, or direct manipulation. Prefer a few coherent transitions over unrelated effects.

- immediate press/interaction feedback matters more than decorative entrance animation;
- motion attached to direct manipulation should be interruptible when practical;
- avoid long choreography that delays the user's next action;
- respect `prefers-reduced-motion`;
- use compositor-friendly properties for hot paths;
- do not add a dependency solely for visual motion if the repository can meet the interaction requirement with its existing stack.

If Apple-like gesture/material behavior is explicitly requested and the bundled `apple-web-design` companion exists, read that specialized skill after this one. Its rules refine interaction behavior; they do not replace the broader product-design discovery here.

## 8. Accessibility and clarity outrank aesthetics

- maintain semantic structure and native controls where practical;
- preserve visible keyboard focus;
- do not encode state or meaning by color alone;
- maintain readable contrast over images, gradients, translucency, and disabled states;
- touch targets and spacing must remain operable on small screens;
- avoid motion/transparency choices that destroy usability under user accessibility preferences;
- form errors must identify what failed and how to recover.

Repository-specific accessibility standards take precedence when stricter.

## 9. Visual verification is mandatory for visual claims when available

Code inspection, DOM geometry, unit tests, and a green build do not prove that a UI looks correct.

For material UI changes, use rendered evidence when the environment provides a browser/screenshot path. Inspect at least the changed surface and the responsive/state risks relevant to the task. Compare against repository references or the established Design Read, not against a generic aesthetic preference.

Read [references/visual-verification.md](references/visual-verification.md) for the acceptance contract.

If rendered evidence is unavailable, say that visual correctness remains unverified rather than upgrading code-level evidence into a visual success claim.

## 10. Preserve design memory without polluting the project

When a project already has durable design memory, reuse it. Useful forms include:

- repository-owned design-system docs;
- design tokens/theme files;
- Storybook/component examples;
- accepted screenshot baselines;
- current-status/product-history records that explain visual decisions.

Do not create parallel Sloar-owned design history merely to impose a convention. Sloar can checkpoint the current Design Read as hot state when continuity matters, while the repository remains the durable source of product design truth.

## 11. Completion report

For substantial UI work, report only what materially helps review:

- the design direction actually used or preserved;
- the surface/component scope changed;
- rendered visual checks that actually ran and the viewport/state coverage;
- accessibility/responsive limitations still unverified;
- deliberate design boundaries (what was not redesigned).

Do not present a style name or component-library choice as proof of quality. Quality is supported by product fit, coherent system usage, real states, and rendered evidence.
