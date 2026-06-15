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

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 1,
  });

  await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  const cards = await page.locator(".card").all();
  if (cards.length === 0) {
    throw new Error("No .card sections found in index.html");
  }

  const report = [];
  for (let i = 0; i < cards.length; i += 1) {
    const number = pad2(i + 1);
    const filename = `${date}_${prefix}_${number}.png`;
    const filePath = path.join(outputDir, filename);
    await cards[i].screenshot({ path: filePath });

    const box = await cards[i].boundingBox();
    const stat = fs.statSync(filePath);
    report.push({
      card: number,
      filename,
      resolution: `${Math.round(box.width)}x${Math.round(box.height)}`,
      size_bytes: stat.size,
    });
  }

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
