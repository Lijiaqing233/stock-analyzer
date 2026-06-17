import fs from "node:fs";
import assert from "node:assert/strict";

import { createI18n } from "./i18n.js";

const appSource = fs.readFileSync(new URL("./app.js", import.meta.url), "utf8");
const requiredMetricKeys = ["price", "return3m", "volatility", "maxDrawdown", "avgDollarVolume"];

for (const language of ["en", "zh", "ja"]) {
  const i18n = createI18n(language);
  assert.ok(i18n.t("marketDataSetupRequired").length > 0, `${language} should translate setup title`);
  assert.ok(i18n.t("marketDataSetupDetail").length > 0, `${language} should translate setup detail`);
  assert.ok(i18n.t("manualEntry").length > 0, `${language} should translate manual entry`);
  assert.ok(i18n.t("removeSymbol", { symbol: "AAPL" }).includes("AAPL"), `${language} should interpolate remove symbol`);
  for (const key of requiredMetricKeys) {
    assert.ok(i18n.metric(key).length > 0, `${language} should translate metric ${key}`);
  }
}

for (const hardcoded of ["Market data setup required", "Manual entry", "Latest price", "Max drawdown"]) {
  assert.equal(appSource.includes(hardcoded), false, `app.js should not hardcode ${hardcoded}`);
}

console.log("public i18n checks passed");
