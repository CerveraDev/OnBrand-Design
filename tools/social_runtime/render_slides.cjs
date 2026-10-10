#!/usr/bin/env node

// Renders the slides of a built social package from the project's scaffold.
//
// For each slide the scaffold page is loaded in Chromium, every frame but the
// slide's own is removed, the frame's image and text slots are filled, and the
// frame canvas is exported as a JPEG at the requested scale. Each text slot is
// measured after layout so the caller can check it against the frame's limits.
//
// Called by tools/social_runtime/render.py, which writes the job file:
//   node tools/social_runtime/render_slides.cjs --job <job.json>
// The result is printed to stdout as JSON.

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const VIEWPORT = { width: 1512, height: 900 };

async function main() {
  const jobIndex = process.argv.indexOf('--job');
  if (jobIndex < 0 || !process.argv[jobIndex + 1]) {
    throw new Error('Usage: render_slides.cjs --job <job.json>');
  }
  const job = JSON.parse(fs.readFileSync(process.argv[jobIndex + 1], 'utf8'));
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  const slides = [];
  try {
    const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: job.scale });
    const page = await context.newPage();
    for (const slide of job.slides) {
      await page.goto(pathToFileURL(job.scaffold_html).href, { waitUntil: 'domcontentloaded' });
      const measured = await page.evaluate(fillInPage, slide);
      if (!measured.error) {
        fs.mkdirSync(path.dirname(slide.output), { recursive: true });
        await page.locator(`[data-frame-id="${slide.frame}"] [data-frame-canvas]`)
          .screenshot({ path: slide.output, type: 'jpeg', quality: job.quality });
      }
      slides.push({ output: slide.output, ...measured });
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify({ slides }) + '\n');
}

function loadPlaywright() {
  const candidates = [
    process.env.ONBRAND_PLAYWRIGHT_MODULE,
    path.join(__dirname, '..', 'email_render_matrix', 'node_modules', 'playwright'),
  ].filter(Boolean);
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (error) {
      // Try the next location.
    }
  }
  throw new Error('Playwright is not installed. See tools/email_render_matrix/README.md.');
}

// Runs in the page. Fills one frame and measures the result.
async function fillInPage(slide) {
  const frame = document.querySelector(`[data-frame-id="${slide.frame}"]`);
  const canvas = frame && frame.querySelector('[data-frame-canvas]');
  if (!canvas) return { error: `frame ${slide.frame} is not in the scaffold` };
  for (const other of document.querySelectorAll('[data-frame-id]')) {
    if (other !== frame) other.remove();
  }
  // Scaffold containers transition their backgrounds; a swap must land at once.
  const still = document.createElement('style');
  still.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
  document.head.append(still);
  const slotElement = (name) =>
    canvas.matches(`[data-slot="${name}"]`) ? canvas : canvas.querySelector(`[data-slot="${name}"]`);
  const layersOf = (value) => {
    const layers = [];
    let depth = 0;
    let current = '';
    for (const char of value) {
      if (char === '(') depth += 1;
      if (char === ')') depth -= 1;
      if (char === ',' && depth === 0) {
        layers.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    layers.push(current.trim());
    return layers;
  };

  const images = [];
  for (const image of slide.images) {
    const element = slotElement(image.slot);
    if (!element) return { error: `image slot '${image.slot}' is not in frame ${slide.frame}` };
    const style = getComputedStyle(element);
    const layers = layersOf(style.backgroundImage);
    const index = layers.findIndex((layer) => layer.startsWith('url('));
    if (index < 0) return { error: `image slot '${image.slot}' has no background image in the scaffold` };
    const probe = new Image();
    probe.src = image.url;
    try {
      await probe.decode();
    } catch (error) {
      return { error: `image for slot '${image.slot}' could not be loaded` };
    }
    layers[index] = `url(${JSON.stringify(image.url)})`;
    const sizes = layersOf(style.backgroundSize);
    const positions = layersOf(style.backgroundPosition);
    // Every image area cover-fits, whatever sizing the scaffold gives it.
    if (sizes[index] !== 'cover') {
      sizes[index] = 'cover';
      positions[index] = '50% 50%';
    }
    element.style.setProperty('background-image', layers.join(', '), 'important');
    element.style.setProperty('background-size', sizes.join(', '), 'important');
    element.style.setProperty('background-position', positions.join(', '), 'important');
    images.push({ slot: image.slot, natural_width: probe.naturalWidth, natural_height: probe.naturalHeight });
  }

  for (const entry of slide.text) {
    const element = slotElement(entry.slot);
    if (!element) return { error: `text slot '${entry.slot}' is not in frame ${slide.frame}` };
    element.replaceChildren();
    entry.value.split('\n').forEach((line, lineIndex) => {
      if (lineIndex) element.append(document.createElement('br'));
      // In a slot with an italic accent, *word* is set in italics.
      const parts = entry.italic_accent ? line.split(/\*([^*]+)\*/) : [line];
      parts.forEach((part, partIndex) => {
        if (!part) return;
        if (partIndex % 2) {
          const accent = document.createElement('em');
          accent.textContent = part;
          element.append(accent);
        } else {
          element.append(part);
        }
      });
    });
  }

  await document.fonts.ready;
  await Promise.all([...canvas.querySelectorAll('img')].map((img) => img.decode().catch(() => null)));
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  const bounds = canvas.getBoundingClientRect();
  const inside = (rect) =>
    rect.left >= bounds.left - 1 && rect.right <= bounds.right + 1 &&
    rect.top >= bounds.top - 1 && rect.bottom <= bounds.bottom + 1;
  const text = {};
  for (const entry of slide.text) {
    const element = slotElement(entry.slot);
    const range = document.createRange();
    range.selectNodeContents(element);
    const rects = [...range.getClientRects()].filter((rect) => rect.width > 0);
    const step = parseFloat(getComputedStyle(element).fontSize) / 2;
    const lines = [];
    for (const rect of rects) {
      const middle = (rect.top + rect.bottom) / 2;
      if (!lines.some((line) => Math.abs(line - middle) < step)) lines.push(middle);
    }
    text[entry.slot] = {
      lines: lines.length,
      inside_canvas: inside(element.getBoundingClientRect()) && rects.every(inside),
    };
  }
  const logo = canvas.querySelector('img[data-slot="logo"]');
  return { images, text, logo_loaded: logo ? logo.naturalWidth > 0 : null };
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exit(1);
});
