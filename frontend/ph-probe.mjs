import { chromium } from 'playwright';

const url = process.argv[2] || 'https://zumud.com/';
const browser = await chromium.launch();
const page = await browser.newPage();

const ingest = [];
page.on('request', (r) => {
  if (r.url().includes('/ingest') || r.url().includes('posthog')) {
    let body = '';
    try { body = r.postData() || ''; } catch {}
    ingest.push({ method: r.method(), url: r.url(), bodyLen: body.length, body: body.slice(0, 400) });
  }
});
page.on('response', async (r) => {
  if (r.url().includes('/ingest')) {
    const hit = ingest.find((i) => i.url === r.url() && i.status === undefined);
    if (hit) hit.status = r.status();
  }
});
const consoleErrors = [];
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 300)); });
page.on('pageerror', (e) => consoleErrors.push('PAGEERROR: ' + String(e).slice(0, 300)));

await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(6000);

const phState = await page.evaluate(() => {
  const ph = window.posthog;
  if (!ph) return { present: false };
  return {
    present: true,
    hasInit: typeof ph.capture === 'function',
    loaded: !!ph.__loaded,
    distinct_id: ph.get_distinct_id ? ph.get_distinct_id() : null,
    config_api_host: ph.config?.api_host,
    config_defaults: ph.config?.defaults,
    capture_pageview: ph.config?.capture_pageview,
    opt_out: ph.has_opted_out_capturing ? ph.has_opted_out_capturing() : null,
  };
});

console.log('=== posthog state ===');
console.log(JSON.stringify(phState, null, 2));
console.log('=== ingest requests (' + ingest.length + ') ===');
for (const i of ingest) console.log(`${i.status ?? '-'} ${i.method} ${i.url}  bodyLen=${i.bodyLen}`);
console.log('=== console errors (' + consoleErrors.length + ') ===');
for (const e of consoleErrors) console.log(e);

await browser.close();
