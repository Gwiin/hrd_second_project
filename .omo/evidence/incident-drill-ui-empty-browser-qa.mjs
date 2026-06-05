import { chromium } from "/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/index.mjs";
import { writeFile } from "node:fs/promises";

const base = "http://127.0.0.1:8772";
const suffix = Date.now();

async function signup(page, email) {
  await page.getByRole("button", { name: /Create account/i }).click();
  await page.getByLabel(/Email/i).fill(email);
  await page.getByLabel(/Password/i).fill("strong-pass-12345");
  await page.locator(".auth-submit", { hasText: "Create account" }).click();
  await page.getByText(/Signed in as/i).waitFor({ timeout: 10000 });
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();
await page.goto(base, { waitUntil: "networkidle" });
await signup(page, `incident-drill-ui-empty-${suffix}@example.com`);
await page.getByText(/No active alert/i).waitFor({ timeout: 10000 });
await page.screenshot({ path: ".omo/evidence/incident-drill-ui-browser-empty.png", fullPage: true });

const empty = {
  noActiveAlert: await page.getByText(/No active alert/i).isVisible(),
  notReplayable: await page.getByText(/not replayable/i).isVisible(),
  replayDisabled: await page.getByRole("button", { name: /Replay incident/i }).isDisabled(),
  reviewCards: await page.locator(".incident-review-card").count(),
  panelText: (await page.locator(".incident-response-panel").innerText()).split("\n").filter(Boolean).slice(0, 24)
};
await writeFile(".omo/evidence/incident-drill-ui-browser-empty.txt", JSON.stringify(empty, null, 2));
await browser.close();
console.log(JSON.stringify(empty, null, 2));
