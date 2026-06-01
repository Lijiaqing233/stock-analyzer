import { createI18n, detectLanguage, languages } from "./i18n.js";

const i18n = createI18n(detectLanguage());

const state = {
  stocks: [],
  selected: null,
  diagnostics: null,
  summary: null
};

const elements = {
  list: document.querySelector("#stockList"),
  detail: document.querySelector("#detailPanel"),
  sector: document.querySelector("#sectorFilter"),
  style: document.querySelector("#styleFilter"),
  score: document.querySelector("#scoreFilter"),
  scoreValue: document.querySelector("#scoreValue"),
  refresh: document.querySelector("#refreshButton"),
  summary: document.querySelector("#summary"),
  sectors: document.querySelector("#sectorGrid"),
  diagnostics: document.querySelector("#diagnosticsGrid"),
  language: document.querySelector("#languageSelect")
};

function scoreClass(score) {
  if (score >= 76) return "strong";
  if (score >= 58) return "mid";
  return "weak";
}

function flagClass(severity) {
  if (severity === "high") return "danger";
  if (severity === "medium") return "warn";
  return "info";
}

function formatPercent(value) {
  return `${Number(value).toFixed(1)}%`;
}

async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function queryString() {
  const params = new URLSearchParams();
  params.set("sector", elements.sector.value);
  params.set("style", elements.style.value);
  params.set("minScore", elements.score.value);
  return params.toString();
}

function applyStaticTranslations() {
  document.documentElement.lang = i18n.language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = i18n.t(node.dataset.i18n);
  });
  elements.refresh.title = i18n.t("refresh");
}

function renderLanguageSelect() {
  elements.language.innerHTML = languages
    .map((language) => `<option value="${language.code}">${language.label}</option>`)
    .join("");
  elements.language.value = i18n.language;
}

function renderStyleOptions() {
  const currentStyle = elements.style.value || "all";
  const options = [
    ["all", i18n.t("allStyles")],
    ["balanced", i18n.t("balanced")],
    ["growth", i18n.t("growthTilt")],
    ["value", i18n.t("valueTilt")]
  ];
  elements.style.innerHTML = options
    .map(([value, label]) => `<option value="${value}">${label}</option>`)
    .join("");
  elements.style.value = options.some(([value]) => value === currentStyle) ? currentStyle : "all";
}

async function loadStocks() {
  state.stocks = await getJson(`/api/stocks?${queryString()}`);
  renderList();
  if (state.stocks.length) {
    selectStock(state.selected?.symbol || state.stocks[0].symbol);
  } else {
    state.selected = null;
    elements.detail.innerHTML = `
      <p class="eyebrow">${i18n.t("selectedStock")}</p>
      <h3>${i18n.t("noMatches")}</h3>
      <p class="muted">${i18n.t("relaxFilters")}</p>
    `;
  }
}

async function loadSummary() {
  state.summary = await getJson("/api/summary");
  renderSummary();
  renderSectorOptions();
  renderSectors();
}

async function loadDiagnostics() {
  state.diagnostics = await getJson("/api/diagnostics");
  renderDiagnostics();
}

function renderSummary() {
  const summary = state.summary;
  if (!summary) return;
  elements.summary.innerHTML = `
    <div><span class="metric-label">${i18n.t("universe")}</span><strong>${summary.universeSize}</strong></div>
    <div><span class="metric-label">${i18n.t("average")}</span><strong>${summary.averageScore}</strong></div>
    <div><span class="metric-label">${i18n.t("topSector")}</span><strong>${i18n.sector(summary.sectors[0]?.sector ?? "--")}</strong></div>
  `;
}

function renderSectorOptions() {
  const currentSector = elements.sector.value || "all";
  const sectors = ["all", ...(state.summary?.sectors ?? []).map((sector) => sector.sector)];
  elements.sector.innerHTML = sectors
    .map((sector) => {
      const label = sector === "all" ? i18n.t("allSectors") : i18n.sector(sector);
      return `<option value="${sector}">${label}</option>`;
    })
    .join("");
  elements.sector.value = sectors.includes(currentSector) ? currentSector : "all";
}

function renderSectors() {
  const summary = state.summary;
  if (!summary) return;
  elements.sectors.innerHTML = summary.sectors
    .map(
      (sector) => `
        <article class="sector-card">
          <span class="muted">${i18n.sector(sector.sector)}</span>
          <strong>${sector.avgScore}</strong>
          <span class="muted">${i18n.t("stocksCount", { count: sector.count })}</span>
        </article>
      `
    )
    .join("");
}

function renderList() {
  elements.list.innerHTML = state.stocks
    .map(
      (stock) => `
        <article class="stock-row ${state.selected?.symbol === stock.symbol ? "active" : ""}" data-symbol="${stock.symbol}">
          <div class="symbol">${stock.symbol}</div>
          <div class="company">
            <strong>${stock.name}</strong>
            <span>${i18n.sector(stock.sector)} / ${i18n.rating(stock.rating)} / ${i18n.t("confidence")} ${stock.confidence}</span>
          </div>
          <div class="score ${scoreClass(stock.score)}">${stock.score}</div>
        </article>
      `
    )
    .join("");
}

function selectStock(symbol) {
  const stock = state.stocks.find((item) => item.symbol === symbol) || state.stocks[0];
  state.selected = stock;
  renderList();
  renderDetail(stock);
}

function renderDetail(stock) {
  const factors = Object.entries(stock.factors)
    .map(
      ([name, score]) => `
        <div class="factor">
          <div class="factor-top">
            <span>${i18n.factor(name)}</span>
            <span>${score} / +${stock.contributions[name]} ${i18n.t("points")}</span>
          </div>
          <div class="bar"><span style="width:${score}%"></span></div>
        </div>
      `
    )
    .join("");

  const flags = stock.flags.length
    ? stock.flags
        .map((flag) => {
          const [label, detail] = i18n.flag(flag);
          return `
            <li class="flag ${flagClass(flag.severity)}">
              <strong>${label}</strong>
              <span>${detail}</span>
            </li>
          `;
        })
        .join("")
    : `<li class="flag info"><strong>${i18n.t("noActiveFlags")}</strong><span>${i18n.t("noActiveFlagsDetail")}</span></li>`;

  elements.detail.innerHTML = `
    <div class="detail-title">
      <div>
        <p class="eyebrow">${stock.symbol}</p>
        <h3>${stock.name}</h3>
      </div>
      <div class="score ${scoreClass(stock.score)}">${stock.score}</div>
    </div>
    <div class="rating">${i18n.rating(stock.rating)} / ${i18n.t("confidence")} ${stock.confidence}</div>
    <p class="muted">${localizedThesis(stock)}</p>
    <div class="factor-list">${factors}</div>
    <ul class="flag-list">${flags}</ul>
    <div class="metric-table">
      <div class="metric"><span>P/E</span><strong>${stock.pe}</strong></div>
      <div class="metric"><span>ROE</span><strong>${formatPercent(stock.roe)}</strong></div>
      <div class="metric"><span>${metricLabel("revenueGrowth")}</span><strong>${formatPercent(stock.revenueGrowth)}</strong></div>
      <div class="metric"><span>${metricLabel("return3m")}</span><strong>${formatPercent(stock.return3m)}</strong></div>
      <div class="metric"><span>Beta</span><strong>${stock.beta}</strong></div>
      <div class="metric"><span>${metricLabel("fcfYield")}</span><strong>${formatPercent(stock.freeCashFlowYield)}</strong></div>
    </div>
  `;
}

function renderDiagnostics() {
  const diagnostics = state.diagnostics;
  if (!diagnostics) return;
  elements.diagnostics.innerHTML = `
    <article class="diagnostic-card">
      <span class="muted">${i18n.t("completeRows")}</span>
      <strong>${diagnostics.coverage.completeRows}/${diagnostics.coverage.stocks}</strong>
      <span class="muted">${i18n.t("requiredFieldsChecked", { count: diagnostics.coverage.requiredFields })}</span>
    </article>
    <article class="diagnostic-card">
      <span class="muted">${i18n.t("averageConfidence")}</span>
      <strong>${diagnostics.model.averageConfidence}</strong>
      <span class="muted">${i18n.t("modelTrust")}</span>
    </article>
    <article class="diagnostic-card">
      <span class="muted">${i18n.t("riskFlags")}</span>
      <strong>${diagnostics.risk.flagCount}</strong>
      <span class="muted">${i18n.t("highSeverity", { count: diagnostics.risk.highSeverityCount })}</span>
    </article>
    <article class="diagnostic-card wide">
      <span class="muted">${i18n.t("factorAverages")}</span>
      <div class="mini-bars">
        ${Object.entries(diagnostics.model.factorAverages)
          .map(
            ([name, score]) => `
              <div>
                <span>${i18n.factor(name)}</span>
                <div class="bar"><span style="width:${score}%"></span></div>
                <b>${score}</b>
              </div>
            `
          )
          .join("")}
      </div>
    </article>
  `;
}

function localizedThesis(stock) {
  const strengths = Object.entries(stock.factors)
    .filter(([, score]) => score >= 68)
    .sort((a, b) => b[1] - a[1])
    .map(([name]) => i18n.factor(name))
    .slice(0, 2)
    .join(" / ");
  const weaknesses = Object.entries(stock.factors)
    .filter(([, score]) => score < 48)
    .sort((a, b) => a[1] - b[1])
    .map(([name]) => i18n.factor(name))
    .slice(0, 2)
    .join(" / ");

  const params = {
    name: stock.name,
    rating: i18n.rating(stock.rating),
    strengths,
    weaknesses
  };
  if (strengths && weaknesses) return i18n.t("thesis", params);
  if (!strengths && weaknesses) return i18n.t("thesisNoStrength", params);
  if (strengths && !weaknesses) return i18n.t("thesisNoWeakness", params);
  return i18n.t("thesisNeutral", params);
}

function metricLabel(key) {
  const labels = {
    en: {
      revenueGrowth: "Revenue growth",
      return3m: "3M return",
      fcfYield: "FCF yield"
    },
    zh: {
      revenueGrowth: "营收增长",
      return3m: "3个月回报",
      fcfYield: "自由现金流收益率"
    },
    ja: {
      revenueGrowth: "売上成長率",
      return3m: "3か月リターン",
      fcfYield: "FCF利回り"
    }
  };
  return labels[i18n.language][key] ?? labels.en[key];
}

function rerenderAll() {
  applyStaticTranslations();
  renderLanguageSelect();
  renderStyleOptions();
  renderSummary();
  renderSectorOptions();
  renderSectors();
  renderList();
  renderDiagnostics();
  if (state.selected) renderDetail(state.selected);
}

elements.list.addEventListener("click", (event) => {
  const row = event.target.closest(".stock-row");
  if (row) selectStock(row.dataset.symbol);
});

elements.refresh.addEventListener("click", async () => {
  await loadSummary();
  await loadDiagnostics();
  await loadStocks();
});
elements.sector.addEventListener("change", loadStocks);
elements.style.addEventListener("change", loadStocks);
elements.score.addEventListener("input", () => {
  elements.scoreValue.textContent = elements.score.value;
});
elements.score.addEventListener("change", loadStocks);
elements.language.addEventListener("change", () => {
  i18n.setLanguage(elements.language.value);
  rerenderAll();
});

rerenderAll();
await loadSummary();
await loadDiagnostics();
await loadStocks();
