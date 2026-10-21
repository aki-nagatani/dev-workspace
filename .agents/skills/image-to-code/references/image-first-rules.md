# image-to-code: Image-First Rules (Sections 2-4)

## 2. MANDATORY IMAGE-FIRST RULE

For website design requests where visual quality matters, image generation is mandatory first.

This means:

1. generate the design image or image set yourself first
2. deeply inspect and analyze the generated image(s)
3. extract the design system from them
4. implement the frontend only after that

Do not:

- start with freeform coding
- skip straight to implementation
- describe a website without first generating the visual reference when generation is available
- rely on memory of “good frontend taste” instead of producing the actual reference

The image is the design source.
The code is the translation layer.

---

## 3. GENERATE ENOUGH IMAGES RULE

Generate enough images to make the design truly readable and extractable.

Do not be lazy with image count.

If more images would improve:

- text readability
- typography extraction
- spacing analysis
- button analysis
- card analysis
- color extraction
- component inspection
- implementation fidelity
- responsive understanding
- section clarity

then generate more images.

Strong rule:

- it is better to generate too many clear images than too few compressed images
- it is better to generate one clear image per section than one unreadable board for the whole site
- it is better to create an extra detail image than to guess details later

Never reduce image count just for convenience if that harms quality.

---

## 4. CODEX-SPECIFIC SECTION IMAGE RULE

Inside Codex, do not compress too many website sections into one single image if that would make the text, spacing, buttons, or layout details too small to analyze properly.

In Codex, prefer separate large images per section.

Default rule inside Codex:

- 1 section requested → generate 1 image
- 2 sections requested → generate 2 images
- 3 sections requested → generate 3 images
- 4 sections requested → generate 4 images
- 5 sections requested → generate 5 images
- 6 sections requested → generate 6 images
- 7 sections requested → generate 7 images
- 8 sections requested → generate 8 images
- 9 sections requested → generate 9 images
- 10 sections requested → generate 10 images
- and so on when reasonable

This is preferred because:

- text stays readable
- typography becomes analyzable
- spacing stays visible
- button details stay visible
- layout proportions stay visible
- extraction quality becomes much better
- implementation becomes more faithful

Do not default to:

- one giant multi-column collage
- one long compressed board with tiny unreadable text
- one image containing many sections if that reduces extraction quality

If necessary, generate more images rather than shrinking everything.

Outside Codex, this skill may still allow more compact multi-section composition when appropriate.
Inside Codex, prioritize section clarity and extraction accuracy.

---
