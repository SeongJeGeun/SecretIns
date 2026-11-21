const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function getArg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index === -1 ? fallback : process.argv[index + 1] ?? fallback;
}

async function main() {
  const htmlPath = path.resolve(getArg("html", "index.html"));
  const outputDir = path.resolve(getArg("out", "exported_png"));
  const date = getArg("date", new Date().toISOString().slice(0, 10));
  const prefix = getArg("prefix", "daily-briefing");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || /[/\\]/.test(prefix)) {
    throw new Error("Invalid output date or filename prefix");
  }
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({
      viewport: { width: 1080, height: 1350 },
      deviceScaleFactor: 1,
      javaScriptEnabled: false,
      offline: true,
    });
    // Serve the deck from memory through Playwright, without opening a server or
    // granting the browser access to file:// or external resources.
    const root = fs.realpathSync(path.dirname(htmlPath));
    const origin = "http://localhost";
    await page.route("**/*", async (route) => {
      const url = new URL(route.request().url());
      if (url.origin !== origin) return route.abort();
      try {
        const filename = await fs.promises.realpath(path.join(root, decodeURIComponent(url.pathname)));
        const relative = path.relative(root, filename);
        if (relative.startsWith(`..${path.sep}`) || relative === ".." || path.isAbsolute(relative)) {
          return route.abort();
        }
        await route.fulfill({ path: filename });
      } catch {
        await route.fulfill({ status: 404, body: "" });
      }
    });
    await page.goto(`${origin}/${encodeURIComponent(path.basename(htmlPath))}`, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    const cards = page.locator(".card");
    const count = await cards.count();
    if (!count) throw new Error("No .card sections found in index.html");

    const files = [];
    // Screenshots scroll the same viewport. Finish one before scrolling to the next.
    for (let i = 0; i < count; i++) {
      const card = String(i + 1).padStart(2, "0");
      const filename = `${date}_${prefix}_${card}.png`;
      const png = await cards.nth(i).screenshot({ path: path.join(outputDir, filename) });
      // The PNG IHDR begins with the width and height, in network byte order.
      const resolution = `${png.readUInt32BE(16)}x${png.readUInt32BE(20)}`;
      files.push({ card, filename, resolution, size_bytes: png.length });
    }
    const report = { html: path.basename(htmlPath), card_count: count, date, prefix, files };
    fs.writeFileSync(path.join(outputDir, "export_report.json"), JSON.stringify(report, null, 2));
    console.log(`Exported ${count} cards to ${outputDir}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
