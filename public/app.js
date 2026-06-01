const state = {
  stocks: [],
  selected: null
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
  sectors: document.querySelector("#sectorGrid")
};

const factorLabels = {
  momentum: "Momentum",
  value: "Valuation",
  quality: "Quality",
  growth: "Growth",
  risk: "Risk control"
};

function scoreClass(score) {
  if (score >= 76) return "strong";
  if (score >= 58) return "mid";
  return "weak";
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

async function loadStocks() {
  state.stocks = await getJson(`/api/stocks?${queryString()}`);
  renderList();
  if (state.stocks.length) {
    selectStock(state.selected?.symbol || state.stocks[0].symbol);
  } else {
    state.selected = null;
    elements.detail.innerHTML = `
      <p class="eyebrow">Selected Stock</p>
      <h3>没有符合条件的股票</h3>
      <p class="muted">放宽筛选条件后再试。</p>
    `;
  }
}

async function loadSummary() {
  const summary = await getJson("/api/summary");
  elements.summary.innerHTML = `
    <div><span class="metric-label">Universe</span><strong>${summary.universeSize}</strong></div>
    <div><span class="metric-label">Average</span><strong>${summary.averageScore}</strong></div>
    <div><span class="metric-label">Top Sector</span><strong>${summary.sectors[0]?.sector ?? "--"}</strong></div>
  `;

  elements.sectors.innerHTML = summary.sectors
    .map(
      (sector) => `
        <article class="sector-card">
          <span class="muted">${sector.sector}</span>
          <strong>${sector.avgScore}</strong>
          <span class="muted">${sector.count} stocks</span>
        </article>
      `
    )
    .join("");

  const sectors = ["all", ...summary.sectors.map((sector) => sector.sector)];
  elements.sector.innerHTML = sectors
    .map((sector) => `<option value="${sector}">${sector === "all" ? "All sectors" : sector}</option>`)
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
            <span>${stock.sector} · ${stock.rating} · $${stock.price}</span>
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
            <span>${factorLabels[name]}</span>
            <span>${score}</span>
          </div>
          <div class="bar"><span style="width:${score}%"></span></div>
        </div>
      `
    )
    .join("");

  elements.detail.innerHTML = `
    <div class="detail-title">
      <div>
        <p class="eyebrow">${stock.symbol}</p>
        <h3>${stock.name}</h3>
      </div>
      <div class="score ${scoreClass(stock.score)}">${stock.score}</div>
    </div>
    <div class="rating">${stock.rating}</div>
    <p class="muted">${stock.thesis}</p>
    <div class="factor-list">${factors}</div>
    <div class="metric-table">
      <div class="metric"><span>P/E</span><strong>${stock.pe}</strong></div>
      <div class="metric"><span>ROE</span><strong>${formatPercent(stock.roe)}</strong></div>
      <div class="metric"><span>Revenue growth</span><strong>${formatPercent(stock.revenueGrowth)}</strong></div>
      <div class="metric"><span>3M return</span><strong>${formatPercent(stock.return3m)}</strong></div>
      <div class="metric"><span>Beta</span><strong>${stock.beta}</strong></div>
      <div class="metric"><span>FCF yield</span><strong>${formatPercent(stock.freeCashFlowYield)}</strong></div>
    </div>
  `;
}

elements.list.addEventListener("click", (event) => {
  const row = event.target.closest(".stock-row");
  if (row) selectStock(row.dataset.symbol);
});

elements.refresh.addEventListener("click", loadStocks);
elements.sector.addEventListener("change", loadStocks);
elements.style.addEventListener("change", loadStocks);
elements.score.addEventListener("input", () => {
  elements.scoreValue.textContent = elements.score.value;
});
elements.score.addEventListener("change", loadStocks);

await loadSummary();
await loadStocks();
