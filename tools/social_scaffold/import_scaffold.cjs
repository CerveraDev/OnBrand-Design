#!/usr/bin/env node

// Imports an owner-authored social scaffold page (built in Elementor) into a
// project as a clean, self-contained HTML/CSS pair plus a frame catalog.
//
// The page is loaded in Chromium, every frame and slot is annotated with a
// stable data attribute, and only the markup and CSS rules that actually style
// the scaffold are kept. WordPress, theme, and plugin scripts, unused rules,
// unused custom properties, unused classes, and media rules that do not apply
// at the import viewport are dropped. The cleaned copy is then reloaded and
// compared element by element against the live page; the import fails if any
// box or computed style differs.
//
// Usage, from the repository root:
//   node tools/social_scaffold/import_scaffold.cjs \
//     --url http://start-up.local/social-scaffolding/ \
//     --output projects/the-rider/social/scaffold

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const VIEWPORT = { width: 1512, height: 900 };
const FAMILIES = {
  post: { prefix: 'SP', title: 'Single posts' },
  carousel: { prefix: 'SC', title: 'Carousel frames' },
  gallery: { prefix: 'SG', title: 'Photo gallery set' },
};
const IMAGE_COUNTS = { ONE: 1, TWO: 2, THREE: 3, FOUR: 4, FIVE: 5, SIX: 6, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6 };
const COMPARE_PROPS = [
  'display', 'position', 'box-sizing', 'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
  'border-top-style', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
  'border-top-left-radius', 'background-color', 'background-image', 'background-size', 'background-position',
  'background-repeat', 'background-attachment', 'mix-blend-mode', 'opacity', 'overflow-x', 'overflow-y',
  'flex-direction', 'flex-wrap', 'flex-grow', 'flex-shrink', 'flex-basis', 'justify-content', 'align-items',
  'align-self', 'row-gap', 'column-gap', 'grid-template-columns', 'grid-template-rows',
  'font-family', 'font-size', 'font-weight', 'font-style', 'line-height', 'letter-spacing', 'text-align',
  'text-transform', 'text-decoration-line', 'color', 'white-space', 'vertical-align', 'object-fit', 'transform',
];

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const output = path.resolve(args.output);
  const imported = args.date || new Date().toISOString().slice(0, 10);
  fs.mkdirSync(path.join(output, 'previews'), { recursive: true });
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
    const live = await context.newPage();
    const response = await live.goto(args.url, { waitUntil: 'networkidle' });
    const rawSha = sha256(await response.body());
    await live.evaluate(() => document.fonts.ready);
    const corrections = await live.evaluate(annotateInPage);
    const extracted = await live.evaluate(extractInPage);
    const liveSnapshot = await live.evaluate(snapshotInPage, COMPARE_PROPS);

    const htmlPath = path.join(output, 'scaffold.html');
    const cssPath = path.join(output, 'scaffold.css');
    fs.writeFileSync(cssPath, extracted.css);
    fs.writeFileSync(htmlPath, buildHtml(extracted));

    const clean = await context.newPage();
    await clean.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });
    await clean.evaluate(() => document.fonts.ready);
    const cleanSnapshot = await clean.evaluate(snapshotInPage, COMPARE_PROPS);
    const differences = compareSnapshots(liveSnapshot, cleanSnapshot);

    const frames = await clean.evaluate(catalogInPage);
    finishFrames(frames, corrections);
    for (const frame of frames) {
      await clean
        .locator(`[data-frame-id="${frame.id}"] [data-frame-canvas]`)
        .screenshot({ path: path.join(output, 'previews', `${frame.id}.jpg`), type: 'jpeg', quality: 82 });
    }
    const catalog = {
      schema_version: '1.0',
      tool: 'onbrand-social-scaffold-import',
      source: { url: args.url, imported, raw_page_sha256: rawSha, viewport: VIEWPORT },
      files: {
        'scaffold.html': { sha256: sha256(fs.readFileSync(htmlPath)), byte_size: fs.statSync(htmlPath).size },
        'scaffold.css': { sha256: sha256(fs.readFileSync(cssPath)), byte_size: fs.statSync(cssPath).size },
      },
      cleaning: extracted.stats,
      verification: {
        method: 'element-by-element box and computed-style comparison against the live page',
        elements_compared: liveSnapshot.length,
        properties_compared: COMPARE_PROPS.length,
        differences: differences.length,
      },
      owner_review: 'pending',
      frames,
    };
    fs.writeFileSync(path.join(output, 'frame-catalog.json'), `${JSON.stringify(catalog, null, 2)}\n`);
    fs.writeFileSync(path.join(output, 'frame-catalog.md'), buildMarkdown(catalog));
    console.log(JSON.stringify({ frames: frames.length, cleaning: extracted.stats, verification: catalog.verification }, null, 2));
    if (differences.length) {
      console.error(differences.slice(0, 25).join('\n'));
      throw new Error(`Cleaned scaffold differs from the live page in ${differences.length} place(s)`);
    }
  } finally {
    await browser.close();
  }
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    args[argv[i].replace(/^--/, '')] = argv[i + 1];
  }
  if (!args.url || !args.output) {
    throw new Error('Usage: import_scaffold.cjs --url <page-url> --output <directory> [--date YYYY-MM-DD]');
  }
  return args;
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

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

// Runs in the page. Marks each frame, its export canvas, and its slots.
function annotateInPage() {
  const root = document.querySelector('[data-elementor-type="wp-page"]');
  const prefixes = { post: 'SP', carousel: 'SC', gallery: 'SG' };
  const counts = {};
  const used = new Set();
  const corrections = {};
  for (const section of [...root.children]) {
    const lines = (p) => p.innerText.split('\n').map((line) => line.trim()).filter(Boolean);
    const paragraphs = [...section.querySelectorAll('p')];
    const marker = paragraphs.find((p) => /^START\b/.test(p.innerText.trim()));
    if (!marker) throw new Error('Scaffold section without a START marker');
    const size = marker.innerText.match(/(\d+)\s*X\s*(\d+)\s*PIXELS/i);
    if (!size) throw new Error(`Marker has no pixel size: ${marker.innerText}`);
    const [width, height] = [Number(size[1]), Number(size[2])];
    const canvas = [...section.querySelectorAll('*')].find((el) => {
      const rect = el.getBoundingClientRect();
      return Math.round(rect.width) === width && Math.round(rect.height) === height;
    });
    if (!canvas) throw new Error(`No ${width}x${height} canvas after marker: ${marker.innerText}`);
    const label = paragraphs.find((p) => p !== marker && !canvas.contains(p) && !/^END\b/.test(p.innerText.trim()));
    const labelLines = label ? lines(label) : [];
    const family = /CAROUSEL FRAME/i.test(marker.innerText)
      ? 'carousel'
      : labelLines.some((line) => /PHOTO GALLERY/i.test(line)) ? 'gallery' : 'post';
    counts[family] = (counts[family] || 0) + 1;
    // An owner-written "ID: SP-07" label line wins over positional numbering.
    const explicit = labelLines.map((line) => line.match(/^ID[:\s-]+([A-Z]{2}-\d{2})$/)).find(Boolean);
    const id = explicit ? explicit[1] : `${prefixes[family]}-${String(counts[family]).padStart(2, '0')}`;
    if (used.has(id)) throw new Error(`Duplicate frame id ${id}`);
    used.add(id);
    section.setAttribute('data-frame-id', id);
    section.setAttribute('data-frame-family', family);
    canvas.setAttribute('data-frame-canvas', `${width}x${height}`);

    const slotCounts = {};
    const name = (base) => {
      slotCounts[base] = (slotCounts[base] || 0) + 1;
      return slotCounts[base] === 1 ? base : `${base}-${slotCounts[base]}`;
    };
    const canvasArea = width * height;
    let imageIndex = 0;
    for (const el of [canvas, ...canvas.querySelectorAll('*')]) {
      const style = getComputedStyle(el);
      if (el.tagName === 'IMG') {
        el.setAttribute('data-slot', name('logo'));
      } else if (/^(H[1-6]|P)$/.test(el.tagName) && el.innerText.trim()) {
        const role = el.tagName === 'P'
          ? 'footer-line'
          : el.tagName === 'H2' ? 'subheading' : parseFloat(style.fontSize) <= 16 ? 'copy' : 'heading';
        el.setAttribute('data-slot', name(role));
      } else if (style.backgroundImage.includes('url(')) {
        const rect = el.getBoundingClientRect();
        if ((rect.width * rect.height) / canvasArea >= 0.8) {
          el.setAttribute('data-slot', name('background'));
        } else {
          imageIndex += 1;
          el.setAttribute('data-slot', `image-${imageIndex}`);
        }
      }
    }

    // A label that says radial over a linear scrim is rewritten to name the
    // scrim the CSS actually draws. The owner's wording is kept in the catalog.
    const gradients = [...canvas.querySelectorAll('[data-slot^="background"]'), canvas]
      .map((el) => getComputedStyle(el).backgroundImage.match(/(linear|radial)-gradient\((.*?)\)(?=,\s*url|$)/))
      .filter(Boolean);
    const linear = gradients.find((gradient) => gradient[1] === 'linear');
    if (label && linear && !gradients.some((gradient) => gradient[1] === 'radial')) {
      const alphas = [...linear[2].matchAll(/rgba?\(([^)]+)\)/g)].map((m) => {
        const parts = m[1].split(',');
        return parts.length === 4 ? Number(parts[3]) : 1;
      });
      const walker = document.createTreeWalker(label, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (!/RADIAL/.test(node.nodeValue) || alphas[0] === alphas[alphas.length - 1]) continue;
        const from = node.nodeValue.trim();
        const to = `LINEAR SCRIM GRADIENT OVERLAY ON BACKGROUND IMAGE - DARKEST AT ${alphas[0] > alphas[alphas.length - 1] ? 'TOP' : 'BOTTOM'}`;
        node.nodeValue = to;
        corrections[id] = [...(corrections[id] || []), { from, to }];
      }
    }
  }
  return corrections;
}

// Runs in the page. Returns the scaffold markup and only the CSS it uses.
function extractInPage() {
  const root = document.querySelector('[data-elementor-type="wp-page"]');
  const scope = [document.documentElement, document.body, root, ...root.querySelectorAll('*')];
  const stats = { rules_seen: 0, rules_kept: 0, media_blocks_dropped: 0, custom_properties_dropped: 0 };

  const splitTop = (text, separator) => {
    const parts = [];
    let depth = 0;
    let quote = null;
    let current = '';
    for (let i = 0; i < text.length; i += 1) {
      const ch = text[i];
      if (quote) {
        if (ch === '\\') { current += ch + text[i + 1]; i += 1; continue; }
        if (ch === quote) quote = null;
      } else if (ch === '"' || ch === "'") {
        quote = ch;
      } else if (ch === '(' || ch === '[') {
        depth += 1;
      } else if (ch === ')' || ch === ']') {
        depth -= 1;
      } else if (ch === separator && depth === 0) {
        parts.push(current);
        current = '';
        continue;
      }
      current += ch;
    }
    if (current.trim()) parts.push(current);
    return parts.map((part) => part.trim()).filter(Boolean);
  };

  const STATE = /:(hover|focus|focus-visible|focus-within|active|visited|target|checked|disabled|enabled|invalid|placeholder-shown)\b/;
  const PSEUDO_ELEMENT = /::?(before|after)\b/;
  const OTHER_PSEUDO_ELEMENT = /::(?!before|after)[\w-]+|:(first-letter|first-line)\b/;
  const selectorApplies = (selector) => {
    if (STATE.test(selector) || OTHER_PSEUDO_ELEMENT.test(selector)) return false;
    const pseudo = selector.match(PSEUDO_ELEMENT);
    let base = selector.replace(/::?(before|after)\b/g, '').trim();
    if (!base || /[>+~]$/.test(base)) base += '*';
    try {
      return scope.some((el) => {
        if (!el.matches(base)) return false;
        return !pseudo || getComputedStyle(el, `::${pseudo[1]}`).content !== 'none';
      });
    } catch (error) {
      return false;
    }
  };

  const usedFonts = new Map();
  for (const el of scope) {
    const style = getComputedStyle(el);
    const family = style.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    if (!usedFonts.has(family)) usedFonts.set(family, new Set());
    usedFonts.get(family).add(`${style.fontWeight}${style.fontStyle === 'italic' ? 'italic' : ''}`);
  }

  const kept = [];
  const walk = (rules, wrappers) => {
    for (const rule of rules) {
      if (rule instanceof CSSStyleRule) {
        stats.rules_seen += 1;
        const selectors = splitTop(rule.selectorText, ',').filter(selectorApplies);
        if (selectors.length) {
          const declarations = splitTop(rule.style.cssText, ';').map((declaration) => {
            const colon = declaration.indexOf(':');
            return { name: declaration.slice(0, colon).trim(), value: declaration.slice(colon + 1).trim() };
          });
          kept.push({ wrappers, selectors, declarations });
        }
      } else if (rule instanceof CSSMediaRule) {
        if (/\bprint\b/.test(rule.conditionText) || !window.matchMedia(rule.conditionText).matches) {
          stats.media_blocks_dropped += 1;
        } else {
          walk(rule.cssRules, [...wrappers, `@media ${rule.conditionText}`]);
        }
      } else if (rule instanceof CSSFontFaceRule) {
        const family = rule.style.getPropertyValue('font-family').replace(/^["']|["']$/g, '');
        if (usedFonts.has(family)) kept.push({ wrappers, raw: rule.cssText });
      } else if (rule.cssRules && !(rule instanceof CSSKeyframesRule)) {
        walk(rule.cssRules, [...wrappers, rule.cssText.slice(0, rule.cssText.indexOf('{')).trim()]);
      }
    }
  };
  const fontLinks = [];
  for (const sheet of document.styleSheets) {
    let rules;
    try {
      rules = sheet.cssRules;
    } catch (error) {
      // Cross-origin font sheets cannot be read; keep a trimmed link instead.
      const match = sheet.href && sheet.href.match(/fonts\.googleapis\.com\/css\?family=([^:&]+)/);
      const family = match && decodeURIComponent(match[1].replace(/\+/g, ' '));
      if (family && usedFonts.has(family)) {
        const variants = [...usedFonts.get(family)].sort().join(',');
        fontLinks.push(`https://fonts.googleapis.com/css?family=${match[1]}:${variants}&display=swap`);
      }
      continue;
    }
    walk(rules, []);
  }

  // Keep a custom property only when a kept declaration reads it.
  const referenced = new Set();
  let grew = true;
  while (grew) {
    grew = false;
    for (const rule of kept) {
      for (const declaration of rule.declarations || []) {
        if (declaration.name.startsWith('--') && !referenced.has(declaration.name)) continue;
        for (const match of declaration.value.matchAll(/var\(\s*(--[\w-]+)/g)) {
          if (!referenced.has(match[1])) { referenced.add(match[1]); grew = true; }
        }
      }
    }
  }
  const lines = [];
  let openWrappers = [];
  const setWrappers = (wrappers) => {
    if (wrappers.join('|') === openWrappers.join('|')) return;
    lines.push(...openWrappers.map(() => '}'));
    lines.push(...wrappers.map((wrapper) => `${wrapper} {`));
    openWrappers = wrappers;
  };
  const selectorText = [];
  for (const rule of kept) {
    if (rule.raw) { setWrappers(rule.wrappers); lines.push(rule.raw); continue; }
    const declarations = rule.declarations.filter((declaration) => {
      const keep = !declaration.name.startsWith('--') || referenced.has(declaration.name);
      if (!keep) stats.custom_properties_dropped += 1;
      return keep;
    });
    if (!declarations.length) continue;
    setWrappers(rule.wrappers);
    stats.rules_kept += 1;
    selectorText.push(...rule.selectors);
    const body = declarations.map((declaration) => `${declaration.name}: ${declaration.value};`).join(' ');
    lines.push(`${rule.selectors.join(', ')} { ${body} }`);
  }
  setWrappers([]);

  const allSelectors = selectorText.join(' ');
  const classes = new Set([...allSelectors.matchAll(/\.((?:\\.|[\w-])+)/g)].map((m) => m[1].replace(/\\/g, '')));
  const ids = new Set([...allSelectors.matchAll(/#((?:\\.|[\w-])+)/g)].map((m) => m[1].replace(/\\/g, '')));
  const attributeNames = new Set([...allSelectors.matchAll(/\[\s*([\w-]+)/g)].map((m) => m[1]));
  const KEEP = new Set(['data-frame-id', 'data-frame-family', 'data-frame-canvas', 'data-slot', 'src', 'alt', 'width', 'height', 'srcset', 'sizes', 'href', 'lang', 'dir']);
  // Non-breaking spaces are content, so only ASCII whitespace is collapsed.
  const escapeText = (text) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\u00a0/g, '&nbsp;');
  const isBlank = (text) => /^[ \t\n\r\f]*$/.test(text);
  const attributes = (el) => {
    const out = [];
    const classList = [...el.classList].filter((token) => classes.has(token));
    if (classList.length) out.push(`class="${classList.join(' ')}"`);
    for (const attr of el.attributes) {
      if (attr.name === 'class') continue;
      const keep = KEEP.has(attr.name) || attributeNames.has(attr.name) || (attr.name === 'id' && ids.has(attr.value));
      if (keep) out.push(`${attr.name}="${escapeText(attr.value).replace(/"/g, '&quot;')}"`);
    }
    return out.length ? ` ${out.join(' ')}` : '';
  };
  const SKIP = new Set(['SCRIPT', 'STYLE', 'LINK', 'NOSCRIPT', 'TEMPLATE']);
  const VOID = new Set(['IMG', 'BR', 'HR']);
  const inline = (node) => {
    if (node.nodeType === 3) return escapeText(node.nodeValue.replace(/[ \t\n\r\f]+/g, ' '));
    if (node.nodeType !== 1 || SKIP.has(node.tagName)) return '';
    const tag = node.tagName.toLowerCase();
    if (VOID.has(node.tagName)) return `<${tag}${attributes(node)}>`;
    return `<${tag}${attributes(node)}>${[...node.childNodes].map(inline).join('')}</${tag}>`;
  };
  const block = (el, depth) => {
    const pad = '  '.repeat(depth);
    const tag = el.tagName.toLowerCase();
    const open = `<${tag}${attributes(el)}>`;
    if (VOID.has(el.tagName)) return `${pad}${open}`;
    const children = [...el.childNodes].filter((node) => (node.nodeType === 1 && !SKIP.has(node.tagName)) || (node.nodeType === 3 && !isBlank(node.nodeValue)));
    if (!children.length) return `${pad}${open}</${tag}>`;
    if (children.some((node) => node.nodeType === 3)) {
      return `${pad}${open}${[...el.childNodes].map(inline).join('').replace(/^ +| +$/g, '')}</${tag}>`;
    }
    const inner = children.map((child) => {
      const comment = child.hasAttribute('data-frame-id') ? `\n${pad}  <!-- ${child.getAttribute('data-frame-id')} -->\n` : '';
      return `${comment}${block(child, depth + 1)}`;
    });
    return `${pad}${open}\n${inner.join('\n')}\n${pad}</${tag}>`;
  };
  const tagAttributes = (el) => attributes(el);
  return {
    css: `${lines.join('\n')}\n`,
    body: block(root, 1),
    htmlAttributes: tagAttributes(document.documentElement),
    bodyAttributes: tagAttributes(document.body),
    fontLinks,
    title: document.title,
    stats,
  };
}

function buildHtml(extracted) {
  const links = extracted.fontLinks.map((href) => `  <link rel="stylesheet" href="${href.replace(/&/g, '&amp;')}">`);
  return [
    '<!doctype html>',
    `<html${extracted.htmlAttributes}>`,
    '<head>',
    '  <meta charset="utf-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    `  <title>${extracted.title}</title>`,
    ...links,
    '  <link rel="stylesheet" href="scaffold.css">',
    '</head>',
    `<body${extracted.bodyAttributes}>`,
    extracted.body,
    '</body>',
    '</html>',
    '',
  ].join('\n');
}

// Runs in the page. One record per scaffold element, positioned from the root.
function snapshotInPage(props) {
  const root = document.querySelector('.elementor');
  const origin = root.getBoundingClientRect();
  return [root, ...root.querySelectorAll('*')].map((el) => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    const record = {
      tag: el.tagName,
      frame: (el.closest('[data-frame-id]') || el).getAttribute('data-frame-id') || 'root',
      box: [rect.left - origin.left, rect.top - origin.top, rect.width, rect.height].map((n) => Math.round(n * 100) / 100).join(','),
    };
    for (const prop of props) record[prop] = style.getPropertyValue(prop);
    return record;
  });
}

function compareSnapshots(live, clean) {
  const differences = [];
  if (live.length !== clean.length) {
    return [`element count differs: live ${live.length}, clean ${clean.length}`];
  }
  live.forEach((expected, index) => {
    for (const key of Object.keys(expected)) {
      if (expected[key] !== clean[index][key]) {
        differences.push(`${expected.frame} <${expected.tag.toLowerCase()}> #${index} ${key}: live "${expected[key]}" clean "${clean[index][key]}"`);
      }
    }
  });
  return differences;
}

// Runs in the cleaned page. Describes each frame from what Chromium computed.
function catalogInPage() {
  const describeOverlay = (backgroundImage) => {
    const gradient = backgroundImage.match(/(linear|radial)-gradient\((.*?)\)(?=,\s*url|$)/);
    if (!gradient) return null;
    const alphas = [...gradient[2].matchAll(/rgba?\(([^)]+)\)/g)].map((m) => {
      const parts = m[1].split(',');
      return parts.length === 4 ? Number(parts[3]) : 1;
    });
    if (gradient[1] === 'radial') return { type: 'radial-scrim', max_opacity: Math.max(...alphas) };
    if (alphas.every((alpha) => alpha === alphas[0])) return { type: 'flat', opacity: alphas[0] };
    return {
      type: 'linear-scrim',
      darkest_at: alphas[0] > alphas[alphas.length - 1] ? 'top' : 'bottom',
      max_opacity: Math.max(...alphas),
    };
  };
  return [...document.querySelectorAll('[data-frame-id]')].map((section, order) => {
    const lines = (p) => p.innerText.split('\n').map((line) => line.trim()).filter(Boolean);
    const canvas = section.querySelector('[data-frame-canvas]');
    const origin = canvas.getBoundingClientRect();
    const outside = [...section.querySelectorAll('p')].filter((p) => !canvas.contains(p));
    const box = (el) => {
      const rect = el.getBoundingClientRect();
      return {
        x: Math.round(rect.left - origin.left),
        y: Math.round(rect.top - origin.top),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      };
    };
    const images = [];
    const text = [];
    let logo = null;
    for (const el of [canvas, ...canvas.querySelectorAll('[data-slot]')]) {
      const slot = el.getAttribute('data-slot');
      if (!slot) continue;
      const style = getComputedStyle(el);
      const rect = box(el);
      if (el.tagName === 'IMG') {
        logo = { slot, box: rect, src: el.getAttribute('src') };
      } else if (/^(background|image)/.test(slot)) {
        const ratio = rect.width / rect.height;
        images.push({
          slot,
          box: rect,
          shape: ratio > 1.05 ? 'landscape' : ratio < 0.95 ? 'portrait' : 'square',
          background_size: style.backgroundSize,
          background_position: style.backgroundPosition,
          overlay: describeOverlay(style.backgroundImage),
        });
      } else {
        const centre = rect.y + rect.height / 2;
        const range = document.createRange();
        range.selectNodeContents(el);
        const lineHeight = parseFloat(style.lineHeight) || parseFloat(style.fontSize) * 1.2;
        const tops = [...range.getClientRects()].filter((r) => r.width > 0).map((r) => r.top + r.height / 2).sort((a, b) => a - b);
        const renderedLines = tops.filter((top, i) => i === 0 || top - tops[i - 1] > lineHeight / 2).length;
        text.push({
          slot,
          tag: el.tagName.toLowerCase(),
          sample: el.innerText.split('\n').map((line) => line.trim()).filter(Boolean),
          italic_accent: Boolean(el.querySelector('em')),
          font_family: style.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, ''),
          font_size: style.fontSize,
          line_height: style.lineHeight,
          letter_spacing: style.letterSpacing,
          text_transform: style.textTransform,
          text_align: style.textAlign === 'start' ? 'left' : style.textAlign,
          color: style.color,
          rendered_lines: renderedLines,
          available_width: Math.round(el.parentElement.clientWidth - parseFloat(getComputedStyle(el.parentElement).paddingLeft) - parseFloat(getComputedStyle(el.parentElement).paddingRight) - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight)),
          vertical_zone: centre < origin.height / 3 ? 'top' : centre > (origin.height * 2) / 3 ? 'bottom' : 'middle',
          box: rect,
        });
      }
    }
    let border = null;
    for (const el of [canvas, ...canvas.querySelectorAll('*')]) {
      const style = getComputedStyle(el);
      const width = Math.max(...['left', 'right', 'bottom'].map((side) => parseFloat(style.getPropertyValue(`border-${side}-width`))));
      if (width >= 10 && (!border || width > border.width)) {
        border = { width, color: style.borderBottomColor };
      }
    }
    const [width, height] = canvas.getAttribute('data-frame-canvas').split('x').map(Number);
    return {
      id: section.getAttribute('data-frame-id'),
      order: order + 1,
      family: section.getAttribute('data-frame-family'),
      owner_label: {
        start_marker: outside[0] ? outside[0].innerText.trim() : '',
        description: outside[1] ? lines(outside[1]) : [],
        end_marker: outside[outside.length - 1].innerText.trim(),
      },
      canvas: { width, height, export_scale: 2, export_width: width * 2, export_height: height * 2 },
      observed: { framed: Boolean(border), border, logo, image_slots: images, text_slots: text },
    };
  });
}

// Adds the checks that need the whole set: label conflicts and shared labels.
function finishFrames(frames, corrections) {
  const byLabel = new Map();
  for (const frame of frames) {
    const key = frame.owner_label.description.join('|');
    byLabel.set(key, [...(byLabel.get(key) || []), frame.id]);
  }
  for (const frame of frames) {
    const description = frame.owner_label.description.join(' ');
    const overlays = frame.observed.image_slots.map((slot) => slot.overlay && slot.overlay.type).filter(Boolean);
    const notes = [];
    if (/RADIAL/.test(description) && !overlays.includes('radial-scrim')) {
      notes.push(`Label says radial gradient; the CSS uses ${overlays.join(', ') || 'no overlay'}.`);
    }
    if (!/RADIAL/.test(description) && overlays.includes('radial-scrim')) {
      notes.push('Label does not mention a radial gradient; the CSS uses one.');
    }
    const labelFramed = /^FRAMED/.test(frame.owner_label.description[0] || '');
    if (labelFramed !== frame.observed.framed) {
      notes.push(`Label says ${labelFramed ? 'framed' : 'unframed'}; the CSS ${frame.observed.framed ? 'draws a border' : 'draws no border'}.`);
    }
    const counted = frame.owner_label.description.map((line) => line.match(/^(\w+) .*\bIMAGES\b/)).find(Boolean);
    const expected = counted && IMAGE_COUNTS[counted[1]];
    const smallImages = frame.observed.image_slots.filter((slot) => slot.slot.startsWith('image-')).length;
    if (expected && expected !== smallImages) {
      notes.push(`Label describes ${expected} images; the CSS has ${smallImages} image area(s) besides the background.`);
    }
    const twins = byLabel.get(frame.owner_label.description.join('|')).filter((id) => id !== frame.id);
    frame.label_corrections = corrections[frame.id] || [];
    frame.same_label_as = twins;
    frame.review_notes = notes;
  }
}

function buildMarkdown(catalog) {
  const out = [
    '# The Rider Social Scaffold: Frame Catalog',
    '',
    '**Status:** Imported; owner review pending',
    '',
    'Generated by `tools/social_scaffold/import_scaffold.cjs`. Do not edit by hand; re-run the import instead.',
    '',
    `- Source: \`${catalog.source.url}\`, imported ${catalog.source.imported}`,
    `- Frames: ${catalog.frames.length}, each ${catalog.frames[0].canvas.width}x${catalog.frames[0].canvas.height} px, exported at 2x as ${catalog.frames[0].canvas.export_width}x${catalog.frames[0].canvas.export_height} px`,
    `- Cleaning: kept ${catalog.cleaning.rules_kept} of ${catalog.cleaning.rules_seen} CSS rules`,
    `- Verification: ${catalog.verification.elements_compared} elements compared against the live page on ${catalog.verification.properties_compared} computed properties plus box geometry, ${catalog.verification.differences} differences`,
    '',
    '## How To Read This',
    '',
    '- **ID** is assigned by position within each family: `SP` single posts, `SC` carousel frames, `SG` photo gallery set. Adding a line such as `ID: SP-07` to a frame\'s green label in Elementor pins that ID across re-imports.',
    '- **Slots** come from the CSS, not the label. `background` is an image covering the canvas, `image-N` is a smaller image area, and text slots are named by role.',
    '- **Label** is the owner\'s green-bar text. A scrim line that says radial over a linear scrim is rewritten on import to name the actual scrim; **Notes** records the original wording and any other place the label and the CSS disagree.',
    '- Every image slot currently points at one placeholder image.',
    `- ${catalog.frames.filter((frame) => /FRAME START/.test(frame.owner_label.end_marker)).length} of ${catalog.frames.length} END markers read "END - POST FRAME START"; frames are paired by position, so this does not affect the import.`,
    '',
  ];
  for (const [family, meta] of Object.entries(FAMILIES)) {
    const frames = catalog.frames.filter((frame) => frame.family === family);
    if (!frames.length) continue;
    out.push(`## ${meta.title} (${meta.prefix})`, '', '| ID | Preview | Layout | Slots | Label | Notes |', '| --- | --- | --- | --- | --- | --- |');
    for (const frame of frames) {
      const observed = frame.observed;
      const overlays = [...new Set(observed.image_slots.map((slot) => describeOverlayText(slot.overlay)).filter(Boolean))];
      const layout = [
        observed.framed ? `Framed, ${observed.border.width}px ${observed.border.color === 'rgb(255, 255, 255)' ? 'white' : 'black'} border` : 'Edge to edge',
        observed.logo ? `Logo ${zone(observed.logo.box, frame.canvas)}` : 'No logo',
        overlays.length ? `Overlay: ${overlays.join('; ')}` : 'No overlay',
      ];
      const slots = [
        ...observed.image_slots.map((slot) => `\`${slot.slot}\` ${slot.box.width}x${slot.box.height} ${slot.shape}`),
        ...observed.text_slots.map((slot) => `\`${slot.slot}\` ${slot.font_family} ${slot.font_size}${slot.italic_accent ? ', italic accent' : ''}, ${slot.vertical_zone} ${slot.text_align}`),
      ];
      const notes = [...frame.review_notes];
      for (const fix of frame.label_corrections) notes.push(`Label corrected on import; the page says "${fix.from}".`);
      if (frame.same_label_as.length) notes.push(`Same label as ${frame.same_label_as.join(', ')}.`);
      out.push(`| ${frame.id} | <img src="previews/${frame.id}.jpg" width="140" alt="${frame.id}"> | ${layout.join('<br>')} | ${slots.join('<br>')} | ${frame.owner_label.description.join('<br>')} | ${notes.join('<br>') || 'None'} |`);
    }
    out.push('');
  }
  return out.join('\n');
}

function describeOverlayText(overlay) {
  if (!overlay) return null;
  if (overlay.type === 'flat') return `flat black ${Math.round(overlay.opacity * 100)}%`;
  if (overlay.type === 'radial-scrim') return 'radial scrim';
  return `linear scrim, darkest at ${overlay.darkest_at}`;
}

function zone(box, canvas) {
  const y = box.y + box.height / 2;
  const x = box.x + box.width / 2;
  const vertical = y < canvas.height / 3 ? 'top' : y > (canvas.height * 2) / 3 ? 'bottom' : 'middle';
  const horizontal = x < canvas.width / 3 ? 'left' : x > (canvas.width * 2) / 3 ? 'right' : 'center';
  return `${vertical} ${horizontal}`;
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
