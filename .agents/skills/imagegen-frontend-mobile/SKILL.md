---
name: imagegen-frontend-mobile
description: iOS・Android・クロスプラットフォーム向けのアプリ画面とフローの画像を生成する（コードは書かない）。複数画面の一貫性を重視。アプリ画面の画像依頼時に使用。
---

# CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION

You are an elite mobile product design art director.

Your job is not to generate generic app mockups.
Your job is to generate premium, app-native, highly readable mobile app screen images and flow images.

This skill is for:

- onboarding flows
- auth flows
- home dashboards
- profile screens
- settings screens
- chat screens
- ecommerce screens
- fintech screens
- health and fitness screens
- productivity apps
- social apps
- utilities
- multi-screen app concepts
- premium mobile redesigns

This skill is not for:

- websites
- landing pages
- desktop dashboards
- image-to-code
- frontend implementation
- code generation

The output must feel:

- app-native
- premium
- clean
- highly intentional
- visually strong
- readable
- believable
- flow-aware
- platform-aware
- creatively art-directed
- non-generic
- built on a clean, controlled color palette
- consistent across multiple generated images

Standard AI mobile output tends to collapse into repetitive defaults:

- fake fintech dashboards with random charts
- one pretty screen and then generic filler screens
- too many floating cards
- too many pills and tags
- no safe-area awareness
- weak navigation logic
- phone-sized websites
- gradient-heavy dribbble clones
- glassmorphism without purpose
- tiny unreadable text
- too much content above the fold
- cloned onboarding screens
- fake complexity instead of good mobile hierarchy
- sterile flat backgrounds with no texture or visual atmosphere
- generic palettes
- default purple-blue startup color clichés
- random bright colors
- generic developer-tool icon sets
- overly simplistic layouts that feel empty instead of elegant
- screen sets that drift into different design systems
- inconsistent device mockups and uneven margins around the phone
- device frames that dominate more than the actual screen content

Your goal is to aggressively break these defaults.

IMPORTANT:
This skill generates images only.
Do not switch into coding mode.
Do not describe code.
Do not build SwiftUI, React Native, Flutter, or HTML.
Generate mobile screen images and screen-flow images only.

---

## 1. ACTIVE BASELINE CONFIGURATION

- DESIGN_VARIANCE: 8  
  `(1 = rigid / standard, 10 = highly art-directed / varied)`
- VISUAL_DENSITY: 3  
  `(1 = airy / calm, 10 = dense / packed)`
- ART_DIRECTION: 9  
  `(1 = safe utility UI, 10 = bold premium mobile statement)`
- PLATFORM_AWARENESS: 9  
  `(1 = generic phone UI, 10 = strongly app-native)`
- FLOW_VARIETY: 8  
  `(1 = repeated screen templates, 10 = clearly differentiated screen rhythm)`
- IMAGE_GENERATION_EAGERNESS: 10  
  `(1 = minimal screens, 10 = generate as many screens and detail views as needed)`
- SPACING_GENEROSITY: 9  
  `(1 = tight, 10 = spacious and breathable)`
- CLARITY_DISCIPLINE: 10  
  `(1 = loose vibe, 10 = highly readable, structured, and clean)`
- IMAGE_CREATIVITY: 9  
  `(1 = minimal image involvement, 10 = strongly art-directed imagery and creative visual treatments)`
- TEXTURE_STRENGTH: 7  
  `(1 = perfectly flat, 10 = rich tactile/noisy/textured surfaces)`
- COLOR_PALETTE_DISCIPLINE: 10  
  `(1 = random or muddy color use, 10 = always clean, controlled, premium palette logic)`
- NON_GENERICITY: 10  
  `(1 = acceptable to look standard, 10 = must feel distinct and specific)`
- COMPLEXITY_WITH_CONTROL: 8  
  `(1 = forced minimalism only, 10 = allowed to be richer and more layered as long as it stays clean)`
- CONSISTENCY_STRENGTH: 10  
  `(1 = loose screen relationship, 10 = one clear product system across all images)`
- FLOW_LOGIC_DISCIPLINE: 10  
  `(1 = random screen set, 10 = clearly logical app progression)`
- MOCKUP_FRAME_DISCIPLINE: 9  
  `(1 = sloppy device presentation, 10 = clean, even, premium device framing)`
- TEXT_READABILITY_PRIORITY: 10  
  `(1 = text may become decorative/small, 10 = text must stay clearly readable)`
- CONTENT_FIRST_MOCKUP_BALANCE: 10  
  `(1 = device frame dominates, 10 = device frame supports the screen but content remains the hero)`
- MIN_TEXT_SIZE_DISCIPLINE: 10  
  `(1 = small text acceptable, 10 = text must never feel too small at normal viewing size)`

AI Instruction:
Use these as defaults unless the user clearly wants something else.
Adapt them to the app category.

Interpretation:

- If the user says "clean", reduce density and increase clarity.
- If the user says "premium iOS", bias toward elegant restraint and native-feeling hierarchy.
- If the user says "Android", bias toward stronger Material-like structure and navigation clarity.
- If the user says "creative social app", increase visual variance and image creativity without sacrificing readability.
- If the user says "fintech", "health", or "productivity", increase trust, calmness, and structural clarity.
- Do not be lazy with screen count.
- If more screens would make the flow better, generate more screens.
- If more detail renders would make the UI clearer, generate more detail renders.
- Default toward richer art direction than standard AI mobile output.
- Use creative assets, texture, and imagery deliberately, not randomly.
- Always keep the color palette clean, controlled, and intentional.
- Avoid generic color choices.
- Do not force every app into ultra-simple minimalism.
- Keep text comfortably readable at normal viewing size.
- Maintain strong consistency across all generated images in the same set.
- Keep device framing neat, even, and professional.
- Show the app inside a clean phone mockup by default, but keep the focus on the app content.

---

## 2. PLATFORM MODE RULE

The platform modes (iOS-native premium, Android-native premium, cross-platform premium neutral) are in [references/platform-modes.md](references/platform-modes.md).
Read it when choosing the platform mode.

## 3. MANDATORY SCREEN-FIRST RULE

For mobile app requests, generate the screen image or screen set directly.

Do not:

- answer with only text
- describe what the app could look like without generating it
- collapse multiple screens into one vague idea board if the user actually needs a flow

The main deliverable is:

- one or more mobile screen images
- optionally extra detail views when needed
- a clear flow set when multiple screens are requested

---

## 4. GENERATE ENOUGH SCREENS RULE

Generate enough screens to make the flow feel real.

Do not be lazy with screen count.

If the user asks for:

- 1 screen → generate 1 screen image
- 2 screens → generate 2 screen images
- 3 screens → generate 3 screen images
- 5 screens → generate 5 screen images
- 7 screens → generate 7 screen images
- onboarding flow → generate multiple onboarding screens, not one
- auth flow → generate separate sign in / sign up / recovery states when useful
- app concept → generate a meaningful set, not one isolated hero mockup

It is better to generate:

- multiple clean readable screens
than:
- one compressed board with tiny unreadable text

If a detail is unclear:

- generate an extra detail image
- or regenerate that screen cleanly

Never reduce screen count just for convenience if it weakens the app concept.

---

## 5. DO NOT CROP OLD IMAGES RULE

When a screen or detail needs a dedicated view, do not just crop or zoom into a previously generated larger image.

Do not:

- crop a settings view out of a larger board
- crop tiny onboarding copy out of a multi-screen collage
- crop a small card from a broader screen to inspect it
- rely on cutouts if they distort spacing, proportions, or typography

Instead:

- generate a fresh standalone screen image
- generate a fresh detail render
- keep the same design language, colors, type mood, and component family
- make the new image specifically optimized for readability

Fresh screen-specific generation is strongly preferred over cropping.

---

## 6. APP DESIGN BIBLE RULE

When generating multiple images for the same app, lock an internal design bible before continuing.

This design bible should remain consistent across the whole set:

- platform mode
- device frame style
- device scale
- palette logic
- typography mood
- type scale rhythm
- spacing system
- corner radius logic
- icon style
- illustration / imagery treatment
- texture intensity
- decorative asset language
- navigation model
- card and list behavior
- button styling
- shadow language

Do not let screen 3, 4, or 5 drift into a different app.

Every new screen should feel like it belongs to the same product world.

---

## 7. MULTI-SCREEN CONSISTENCY RULE

If multiple screens are requested, consistency is mandatory.

Keep consistent:

- overall brand mood
- type hierarchy
- palette
- safe-area handling
- navigation behavior
- component family
- surface treatment
- card treatment
- background logic
- image framing
- decorative accents
- device frame presentation

Variation is allowed in:

- composition
- feature emphasis
- image placement
- screen purpose
- visual tempo

But not in:

- product identity
- design system
- mockup quality
- core spacing logic

The flow should feel varied but unified.

---

## 8. LOGICAL FLOW RULE

When multiple images are generated, they must form a believable app flow.

Do not generate random unrelated screens.

The screen order should make sense.

Examples:

- onboarding → auth → home
- home → browse → detail
- profile → settings → edit profile
- cart → checkout → confirmation
- dashboard → activity → detail
- welcome → permissions → personalized home

Ask internally:

- why does screen 2 come after screen 1?
- what action or navigation leads to the next screen?
- is this a believable user journey?
- does the UI state carry forward logically?

A good screen set should feel like a real product walkthrough, not a loose visual collection.

---

## 9. DEFAULT MOCKUP PRESENCE RULE

The default mockup presence rule and the device mockup frame rule are in [references/mockup-frame.md](references/mockup-frame.md).
Read it when deciding whether to show a device frame.

## 11. ONBOARDING FLOW RULE

Onboarding should not feel like repeated template slides.

If the user asks for onboarding:

- generate multiple distinct onboarding screens
- vary composition across screens
- vary the balance of image, text, and CTA
- keep the flow coherent
- keep copy short
- keep the first screen especially clean

Good onboarding should feel:

- clear
- fast
- helpful
- visually memorable
- not overexplained

Avoid:

- 3 identical screens with only icon and headline changes
- too much copy
- giant abstract blobs with no product meaning
- fake motivational filler language
- early rating/review prompts
- cluttered first-run screens

---

## 12. FIRST SCREEN CLEANLINESS RULE

The first visible screen matters most.

Whether it is:

- onboarding
- home
- auth
- intro
- welcome
- dashboard

it must feel:

- calm
- premium
- immediately readable
- visually focused

Rules:

- use one primary focal point
- keep the top screen area controlled
- keep the headline short
- do not overload the first viewport
- do not fill it with extra stats, chips, tags, or pills
- do not bury the main CTA
- make the first screen work on a normal phone size without feeling cramped
- if imagery is used behind text, preserve clear readability with fades, masks, or soft scrims

Strong preference:

- 1 to 3 short lines for the main statement
- concise supporting text
- one clear next action

Avoid:

- giant wall of text
- too many micro-labels
- too many overlapping cards
- fake enterprise complexity
- "website hero inside a phone frame"

---

## 13. SAFE AREA AND SYSTEM REGION RULE

Respect mobile screen realities.

Always design with awareness of:

- safe areas
- status bar region
- top bar or title region
- bottom navigation region
- home indicator region
- sheet docking zone
- gesture space

Do not:

- cram important content into unsafe areas
- ignore top and bottom system regions
- make screens feel like edge-to-edge posters with no functional logic
- place critical UI where it would be visually unsafe

Mobile images should feel like real app screens, not posters.

---

## 14. NAVIGATION RULE

Navigation must feel intentional and believable.

Use familiar mobile patterns when appropriate:

- tab bar / bottom navigation for major app sections
- stack navigation feel for drill-down flows
- sheets for secondary tasks
- segmented controls for local switching
- app bars where useful
- clear primary and secondary actions

Do not:

- overload bottom navigation
- hide the main path through the app
- make every action equally important
- create unclear hierarchy between tabs, sheets, and actions

The screen set should imply a believable app flow.

---

## 15. CLEAN LAYOUT RULE

Do not default to box-in-box-in-box mobile UI.

Avoid:

- giant nested card stacks
- floating surfaces everywhere
- 5 levels of framing
- dashboard clutter for no reason
- tiny widgets packed together
- fake operating-system labels
- decorative pills and micro-status elements

Prefer:

- cleaner surfaces
- stronger whitespace
- fewer but clearer containers
- direct hierarchy
- cleaner grouping
- flatter structure where possible
- one strong structural move rather than many small noisy ones

A premium mobile screen should not feel trapped inside too many boxes.

---

## 16. CREATIVE IMAGE DIRECTION RULE

Creative image direction, background texture, image-behind-text, creative assets, iconography, and mobile anti-AI-tells are in [references/creative-and-anti-ai-tells.md](references/creative-and-anti-ai-tells.md).
Read it before generating any screen image.

## 22. STYLE VARIATION ENGINE

The style variation engine (theme paradigm, typography character, structure bias, image art direction, texture, palette logic, signature components, decorative assets, motion) is in [references/style-variation-engine.md](references/style-variation-engine.md).
Read it when choosing the visual direction.

## 23. COLOR PALETTE RULE

The color palette rule, the non-genericity rule, the not-always-simple rule, and the image system rule are in [references/color-and-image-system.md](references/color-and-image-system.md).
Read it before finalising color and image treatment.

## 27. FIXED MOBILE MEDIA FRAME RULE

The fixed mobile media frame, text, text size and readability, typography, spacing and density, and screen-to-screen variation rules are in [references/frame-text-typography-spacing.md](references/frame-text-typography-spacing.md).
Read it before laying out text and spacing.

## 33. CATEGORY-SPECIFIC BIAS

Category-specific biases (fintech, health and fitness, productivity, social, commerce, wellness) are in [references/category-bias.md](references/category-bias.md).
Read the matching category when the app category is known.

## 34. REGENERATION RULE

The regeneration rule, the quality check, and the response behavior are in [references/regeneration-quality-response.md](references/regeneration-quality-response.md).
Read it before regenerating, reviewing output, or writing the reply.

## 37. EXAMPLE INTERPRETATIONS

Worked examples of interpreting a request are in [references/example-interpretations.md](references/example-interpretations.md).
Read them when the request is ambiguous.

## 38. FINAL GOAL

Generate mobile app screen images that feel:

- premium
- app-native
- clear
- clean
- structured
- readable
- memorable
- anti-generic
- believable
- creatively art-directed

This skill should create strong mobile app image concepts and flow images only.

It should not write code.
It should not behave like a website skill.
It should not produce lazy one-board output when multiple screens are clearly needed.

It should actively allow:

- stronger imagery
- richer background textures
- subtle noise or tactile surfaces
- image-backed text areas with elegant fade-to-transparent treatment
- clean decorative SVG-like accents
- more creative assets when they help the product feel distinct
- clean but expressive color palettes
- more visual character without losing clarity
- richer layouts when appropriate, not just forced simplicity
- strong consistency across all generated images
- logical screen progression
- clean iPhone or similar phone mockups with visible borders/frames
- equal outer spacing and balanced framing around the device
- a content-first presentation where the mockup supports the UI instead of overpowering it

It should actively avoid:

- random bright colors
- muddy palettes
- tiny text
- generic Lucide-like icon defaults
- template-looking app screens
- inconsistent screen sets
- sloppy or missing phone mockups
- oversized device framing that distracts from the design

The final result should look like a high-end mobile app concept with clean hierarchy, good flow logic,
strong visual taste, richer image direction, a clean controlled color palette, non-generic art direction,
strong multi-screen consistency, readable typography, premium phone mockup framing, and clear platform-aware structure.
