import { chromium } from '/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/index.mjs';

const actionLogPath = '.omo/ulw-loop/evidence/incident-report-browser-actions.txt';
const screenshotPath = '.omo/ulw-loop/evidence/incident-report-browser.png';
const actions = [];

function log(action) {
  actions.push(`${new Date().toISOString()} ${action}`);
}

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  await page.goto('http://127.0.0.1:8765/', { waitUntil: 'networkidle' });
  log('opened dashboard');

  await page.getByRole('button', { name: 'Create account' }).first().click();
  log('selected signup mode');

  await page.locator('input[name="email"]').fill(`ulw-${Date.now()}@example.com`);
  await page.locator('input[name="password"]').fill('saferoom-demo-pass');
  await page.locator('form.auth-card button[type="submit"]').click();
  log('submitted signup');

  await page.getByText('Incident response').waitFor({ timeout: 5000 });
  await page.getByRole('button', { name: 'Replay incident' }).click();
  log('clicked replay incident');

  await page.getByText('Replay timeline').waitFor({ timeout: 5000 });
  await page.getByText('Incident report').waitFor({ timeout: 5000 });
  await page.getByText('Next action').waitFor({ timeout: 5000 });
  log('verified incident response and report copy');

  await page.screenshot({ path: screenshotPath, fullPage: true });
  log(`screenshot ${screenshotPath}`);
  await page.close();
} finally {
  await browser.close();
}

await import('node:fs/promises').then((fs) => fs.writeFile(actionLogPath, `${actions.join('\n')}\ncleanup: browser.close()\n`, 'utf8'));
