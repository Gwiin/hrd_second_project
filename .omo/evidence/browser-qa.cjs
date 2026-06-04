const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');

async function main() {
  const evidenceDir = '/Users/chanpark/2n_project/.omo/evidence';
  await fs.mkdir(evidenceDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const actions = [];
  try {
    await page.goto('http://127.0.0.1:8011/', { waitUntil: 'networkidle' });
    actions.push('opened dashboard');
    await page.getByRole('button', { name: 'Create account' }).click();
    await page.getByLabel('Email').fill('incident-demo-2@example.com');
    await page.getByLabel('Password').fill('safe-password-123');
    await page.getByRole('button', { name: 'Create account' }).last().click();
    await page.waitForSelector('text=Incident response', { timeout: 10000 });
    actions.push('created account and unlocked dashboard');
    await page.getByRole('button', { name: /Critical gas reading/ }).click();
    actions.push('selected gas critical alert');
    await page.getByRole('button', { name: 'Replay incident' }).click();
    await page.waitForSelector('text=Critical gas level detected', { timeout: 10000 });
    actions.push('replayed incident guidance');
    await page.getByLabel('Response note').fill('Browser QA confirmed gas threshold response.');
    await page.getByLabel('Evidence').fill('Browser QA screenshot captured.');
    await page.getByRole('button', { name: 'Acknowledge with evidence' }).click();
    await page.waitForSelector('text=Incident response saved.', { timeout: 10000 });
    actions.push('acknowledged with evidence');
    const screenshotPath = path.join(evidenceDir, 'task-5-browser-incident.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    await fs.writeFile(
      path.join(evidenceDir, 'task-5-browser-actions.txt'),
      `${actions.join('\n')}\ncleanup: browser.close()\n`,
      'utf8'
    );
    console.log(JSON.stringify({ screenshotPath, actions }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
