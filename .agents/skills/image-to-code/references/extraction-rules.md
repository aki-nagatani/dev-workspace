# image-to-code: Extraction Rules (Sections 20-25)

## 20. FIXED MEDIA FRAME RULE

Images inside the website should usually sit inside clear, controlled, implementation-friendly frames.

Prefer:

- fixed-aspect media blocks
- clearly framed image areas
- repeatable media modules
- consistent corner radius logic
- stable visual proportions across similar sections

Examples:

- hero image in a clearly bounded large frame
- editorial crops using repeatable portrait or landscape ratios
- card images with consistent proportions
- gallery blocks with controlled aspect ratios
- product images placed in stable intentional containers

Avoid:

- random image sizes with no system
- inconsistent proportions across similar modules
- messy scaling
- uncontrolled collage chaos unless explicitly requested

The goal is:

- visually strong images
- inside a system a frontend model can realistically rebuild

---

## 21. TEXT EXTRACTION RULE

When text is readable in the generated section image, extract it and use it.

Especially inspect and extract:

- hero headline
- hero subheadline
- CTA labels
- section headings
- pricing labels
- feature names
- testimonial names and roles if clearly shown
- navbar labels
- footer labels if relevant

If the text is too small to extract reliably:

- generate a closer extraction image
- or generate a second clearer version of that section

Do not ignore text extraction.
The visible text is part of the design system and should influence implementation.

---

## 22. TYPOGRAPHY EXTRACTION RULE

Do not only notice that typography “looks nice”.
Analyze it properly.

Extract and observe:

- size relationships
- weight relationships
- line count
- line height feel
- tracking feel
- serif vs sans behavior
- display vs body contrast
- section heading rhythm
- CTA text scale
- whether the design uses calm or aggressive type

Use these findings during implementation.
Do not flatten typography into a generic coded hierarchy.

---

## 23. SPACING EXTRACTION RULE

Analyze spacing deliberately.

Inspect:

- distance between headline and subheadline
- distance between text and buttons
- distance between cards
- section top and bottom spacing
- side gutters
- card padding
- image-to-text distance
- navbar spacing
- CTA block spacing
- overall cadence across sections

The goal is not exact pixel OCR.
The goal is faithful spacing logic.

Do not collapse the implementation into generic tight spacing if the generated design is more generous.

---

## 24. BUTTON / COMPONENT EXTRACTION RULE

Buttons and components must be analyzed, not guessed.

Inspect:

- button size
- button shape
- button radius
- fill vs outline behavior
- icon usage
- hover-implied mood
- primary vs secondary hierarchy
- card structure
- badge usage
- dividers
- shadows
- borders
- pill logic
- input styling if present

If button or card detail is too small, generate a closer image.

---

## 25. COLOR EXTRACTION RULE

Actively analyze and extract colors from the generated image(s).

Inspect:

- background color
- panel colors
- accent colors
- button fills
- text color hierarchy
- border color logic
- shadow color mood
- image tint / grade
- gradient restraint or intensity

The implemented website should preserve the original color logic as closely as reasonably possible.

Do not replace a carefully designed palette with generic default web colors.

---
