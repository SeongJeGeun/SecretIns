const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function getArg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

async function main() {
  const cwd = process.cwd();
  const htmlPath = path.resolve(cwd, getArg("html", "index.html"));
  const outputDir = path.resolve(cwd, getArg("out", "exported_png"));
  const date = getArg("date", new Date().toISOString().slice(0, 10));
  const prefix = getArg("prefix", "daily-briefing");

  if (!fs.existsSync(htmlPath)) {
    throw new Error(`HTML file not found: ${htmlPath}`);
  }

  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    args: [
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--disable-setuid-sandbox",
      "--no-sandbox",
      "--no-first-run",
      "--no-startup-window",
      "--single-process",
    ]
  });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 1,
  });

  // 로컬 파일이므로 networkidle 대기를 제거하고 domcontentloaded로 고속 로딩
  await page.goto(`file://${htmlPath}`, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  const cards = await page.locator(".card").all();
  if (cards.length === 0) {
    throw new Error("No .card sections found in index.html");
  }

  // 비동기 병렬 스크린샷 렌더링으로 3배 이상 속도 단축
  const promises = cards.map(async (card, i) => {
    const number = pad2(i + 1);
    const filename = `${date}_${prefix}_${number}.png`;
    const filePath = path.join(outputDir, filename);
    await card.screenshot({ path: filePath });

    const box = await card.boundingBox();
    const stat = fs.statSync(filePath);
    return {
      card: number,
      filename,
      resolution: `${Math.round(box.width)}x${Math.round(box.height)}`,
      size_bytes: stat.size,
    };
  });

  const report = await Promise.all(promises);

  await browser.close();

  const reportPath = path.join(outputDir, "export_report.json");
  fs.writeFileSync(reportPath, JSON.stringify({
    html: path.basename(htmlPath),
    card_count: cards.length,
    date,
    prefix,
    files: report,
  }, null, 2));

  console.log(`Exported ${cards.length} cards to ${outputDir}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
