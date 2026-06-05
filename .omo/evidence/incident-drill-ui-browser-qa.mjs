import { chromium } from "/Users/chanpark/.npm/_npx/31e32ef8478fbf80/node_modules/playwright/index.mjs";
import { writeFile } from "node:fs/promises";

const base = "http://127.0.0.1:8771";
const suffix = Date.now();

async function signup(page, email) {
  await page.getByRole("button", { name: /Create account/i }).click();
  await page.getByLabel(/Email/i).fill(email);
  await page.getByLabel(/Password/i).fill("strong-pass-12345");
  await page.locator(".auth-submit", { hasText: "Create account" }).click();
  await page.getByText(/Signed in as/i).waitFor({ timeout: 10000 });
}

async function seedGas(request, eventId) {
  const response = await request.post(`${base}/internal/events`, {
    data: {
      event_id: eventId,
      site_id: "safe-room-lab",
      zone_id: "room-1",
      device_id: "pico-safe-001",
      sensor_id: "gas",
      protocol: "mock",
      value: 601,
      unit: "ppm",
      timestamp: "2026-06-05T14:00:00+09:00",
      quality: "good",
      metadata: { qa: "incident-drill-ui-polish" }
    }
  });
  return response.status();
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
const request = context.request;
const eventStatus = await seedGas(request, `incident-drill-ui-polish-gas-${suffix}`);
const page = await context.newPage();
await page.goto(base, { waitUntil: "networkidle" });
await signup(page, `incident-drill-ui-polish-${suffix}@example.com`);
await page.getByRole("button", { name: /Replay incident/i }).click();
await page.getByRole("checkbox", { name: /Move people away from the room/i }).check();
await page.getByLabel(/Response note/i).fill("UI polish QA started evacuation only.");
await page.getByLabel(/Evidence/i).fill("UI polish screenshot captured.");
await page.getByRole("button", { name: /Acknowledge with evidence/i }).click();
await page.locator(".incident-review-card").waitFor({ timeout: 10000 });
await page.locator(".incident-score-ring", { hasText: "33%" }).waitFor({ timeout: 10000 });
await page.locator(".incident-checklist-card").waitFor({ timeout: 10000 });
await page.locator(".incident-report-card").waitFor({ timeout: 10000 });
await page.screenshot({ path: ".omo/evidence/incident-drill-ui-browser-happy.png", fullPage: true });

const happy = {
  eventStatus,
  reviewCard: await page.locator(".incident-review-card").isVisible(),
  scoreRing: await page.locator(".incident-score-ring").innerText(),
  checklistCard: await page.locator(".incident-checklist-card").isVisible(),
  reportCard: await page.locator(".incident-report-card").isVisible(),
  checkedCount: await page.locator('input[name="response-checklist"]:checked').count(),
  uncheckedCount: await page.locator('input[name="response-checklist"]:not(:checked)').count(),
  panelText: (await page.locator(".incident-response-panel").innerText()).split("\n").filter(Boolean).slice(0, 42)
};
await writeFile(".omo/evidence/incident-drill-ui-browser-happy.txt", JSON.stringify(happy, null, 2));

const mobileContext = await browser.newContext({ viewport: { width: 390, height: 950 } });
const mobileRequest = mobileContext.request;
const mobileEventStatus = await mobileRequest.post(`${base}/internal/events`, {
  data: {
    event_id: `incident-drill-ui-polish-mobile-gas-${suffix}`,
    site_id: "safe-room-lab",
    zone_id: "room-1",
    device_id: "pico-safe-001",
    sensor_id: "gas",
    protocol: "mock",
    value: 601,
    unit: "ppm",
    timestamp: "2026-06-05T14:05:00+09:00",
    quality: "good",
    metadata: { qa: "incident-drill-ui-mobile" }
  }
});
const mobilePage = await mobileContext.newPage();
await mobilePage.goto(base, { waitUntil: "networkidle" });
await signup(mobilePage, `incident-drill-ui-mobile-${suffix}@example.com`);
await mobilePage.getByRole("button", { name: /Replay incident/i }).click();
await mobilePage.getByRole("checkbox", { name: /Move people away from the room/i }).check();
await mobilePage.getByRole("button", { name: /Acknowledge with evidence/i }).click();
await mobilePage.locator(".incident-review-card").waitFor({ timeout: 10000 });
await mobilePage.screenshot({ path: ".omo/evidence/incident-drill-ui-browser-mobile.png", fullPage: true });
const mobile = {
  eventStatus: mobileEventStatus.status(),
  scrollWidth: await mobilePage.evaluate(() => document.documentElement.scrollWidth),
  viewportWidth: 390,
  replayVisible: await mobilePage.getByRole("button", { name: /Replay incident/i }).isVisible(),
  completedVisible: await mobilePage.getByText(/Completed actions/i).first().isVisible(),
  scoreVisible: await mobilePage.getByText(/Partial response/i).isVisible(),
  reportVisible: await mobilePage.getByText(/Incident command report/i).first().isVisible()
};
await writeFile(".omo/evidence/incident-drill-ui-browser-mobile.txt", JSON.stringify(mobile, null, 2));
await mobileContext.close();

await browser.close();
console.log(JSON.stringify({ happy, mobile }, null, 2));
