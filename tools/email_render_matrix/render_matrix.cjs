#!/usr/bin/env node

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const MATRIX = [
  { id: 'desktop-light', width: 1440, height: 1200, colorScheme: 'light' },
  { id: 'mobile-light', width: 390, height: 844, colorScheme: 'light' },
  { id: 'desktop-dark', width: 1440, height: 1200, colorScheme: 'dark' },
  { id: 'mobile-dark', width: 390, height: 844, colorScheme: 'dark' },
];

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = path.resolve(args.input);
  const output = path.resolve(args.output);
  if (!fs.existsSync(input) || !fs.statSync(input).isFile()) {
    throw new Error(`Input HTML does not exist: ${input}`);
  }
  fs.mkdirSync(output, { recursive: true });
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const entry of MATRIX) {
      results.push(await renderEntry(browser, input, output, entry));
    }
  } finally {
    await browser.close();
  }
  const report = {
    schema_version: '1.0',
    tool: 'onbrand-email-render-matrix',
    browser_engine: 'chromium',
    input: {
      filename: path.basename(input),
      sha256: sha256File(input),
      byte_size: fs.statSync(input).size,
    },
    matrix: results,
    passed: results.every((item) => item.passed),
    scope: 'browser-preview-only',
    human_review: 'pending',
  };
  fs.writeFileSync(path.join(output, 'render-report.json'), `${JSON.stringify(report, null, 2)}\n`);
  fs.writeFileSync(path.join(output, 'visual-review.md'), reviewWorksheet(report));
  process.stdout.write(`${JSON.stringify({ passed: report.passed, entries: results.length, output }, null, 2)}\n`);
  process.exitCode = report.passed ? 0 : 1;
}

async function renderEntry(browser, input, output, entry) {
  const context = await browser.newContext({
    viewport: { width: entry.width, height: entry.height },
    colorScheme: entry.colorScheme,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const requestFailures = [];
  const pageErrors = [];
  const consoleErrors = [];
  page.on('requestfailed', (request) => requestFailures.push({ url: request.url(), error: request.failure()?.errorText || 'unknown' }));
  page.on('pageerror', (error) => pageErrors.push(String(error)));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  await page.goto(pathToFileURL(input).href, { waitUntil: 'load' });
  await page.waitForTimeout(250);
  const diagnostics = await page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const images = Array.from(document.images);
    const brokenImages = images
      .filter((image) => !image.complete || image.naturalWidth === 0)
      .map((image) => image.getAttribute('src') || '');
    return {
      title: document.title,
      document_width: root.scrollWidth,
      document_height: Math.max(root.scrollHeight, body ? body.scrollHeight : 0),
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      horizontal_overflow_px: Math.max(0, root.scrollWidth - window.innerWidth),
      image_count: images.length,
      loaded_image_count: images.length - brokenImages.length,
      broken_images: brokenImages,
      body_text_characters: body ? body.innerText.trim().length : 0,
    };
  });
  const screenshotName = `${entry.id}.jpg`;
  const screenshotPath = path.join(output, screenshotName);
  await page.screenshot({ path: screenshotPath, type: 'jpeg', quality: 82, fullPage: true });
  await context.close();
  const checks = {
    nonempty_document: diagnostics.document_height > 0 && diagnostics.body_text_characters > 0,
    no_horizontal_overflow: diagnostics.horizontal_overflow_px === 0,
    all_images_loaded: diagnostics.broken_images.length === 0,
    no_request_failures: requestFailures.length === 0,
    no_page_errors: pageErrors.length === 0 && consoleErrors.length === 0,
    screenshot_nonempty: fs.statSync(screenshotPath).size > 0,
  };
  return {
    id: entry.id,
    viewport: { width: entry.width, height: entry.height },
    color_scheme: entry.colorScheme,
    screenshot: {
      filename: screenshotName,
      sha256: sha256File(screenshotPath),
      byte_size: fs.statSync(screenshotPath).size,
    },
    diagnostics,
    request_failures: requestFailures,
    page_errors: pageErrors,
    console_errors: consoleErrors,
    checks,
    passed: Object.values(checks).every(Boolean),
  };
}

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (error) {
    const supplied = process.env.ONBRAND_PLAYWRIGHT_MODULE;
    if (supplied) return require(path.join(path.resolve(supplied), 'playwright'));
    throw new Error('Playwright is unavailable. Run npm install in tools/email_render_matrix or set ONBRAND_PLAYWRIGHT_MODULE.');
  }
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!['--input', '--output'].includes(key) || !value) throw new Error('Usage: render_matrix.cjs --input FILE --output DIRECTORY');
    args[key.slice(2)] = value;
  }
  if (!args.input || !args.output) throw new Error('Usage: render_matrix.cjs --input FILE --output DIRECTORY');
  return args;
}

function sha256File(filename) {
  return crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
}

function reviewWorksheet(report) {
  const rows = report.matrix.map((item) => `| ${item.id} | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |`).join('\n');
  return `# Visual Review Worksheet\n\n**Input:** \`${report.input.filename}\`\n\n**Input SHA-256:** \`${report.input.sha256}\`\n\n**Automated browser-preview result:** ${report.passed ? 'PASS' : 'FAIL'}\n\n**Human review status:** Pending\n\nThis worksheet is for screenshot review only. It is not Outlook, Gmail, Apple Mail, native mobile-client, accessibility, legal, or brand certification.\n\n| Matrix entry | Hierarchy | Copy readable | Image crop | Alignment | Footer | No overlap |\n| --- | --- | --- | --- | --- | --- | --- |\n${rows}\n\n## Reviewer Record\n\n- Reviewer:\n- Review date:\n- Decision: Pending\n- Notes:\n`;
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
