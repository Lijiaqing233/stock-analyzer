export const languages = [
  { code: "en", label: "English" },
  { code: "zh", label: "中文" },
  { code: "ja", label: "日本語" }
];

export const messages = {
  en: {
    appEyebrow: "Research Workbench",
    appTitle: "Stock Analyzer",
    modelStatus: "Local model",
    language: "Language",
    heroEyebrow: "Multi-factor stock research",
    heroTitle: "Rank stocks with quality, valuation, growth, momentum, and risk signals",
    heroBody:
      "This is a local research tool. It does not promise returns or replace personal investment advice. The model keeps the scoring logic visible so the next step can be real market data, filings, and portfolio constraints.",
    universe: "Universe",
    average: "Average",
    topSector: "Top Sector",
    sector: "Sector",
    style: "Style",
    minScore: "Min score",
    allSectors: "All sectors",
    allStyles: "All styles",
    balanced: "Balanced",
    growthTilt: "Growth tilt",
    valueTilt: "Value tilt",
    rankings: "Rankings",
    candidateUniverse: "Candidate universe",
    refresh: "Refresh",
    selectedStock: "Selected Stock",
    selectStock: "Select a stock to inspect the model explanation",
    detailHelp: "The detail view shows score, confidence, factor contributions, warnings, and raw metrics.",
    noMatches: "No matching stocks",
    relaxFilters: "Relax the filters to widen the research universe.",
    diagnosticsEyebrow: "Model Diagnostics",
    diagnosticsTitle: "Data quality and factor health",
    marketMap: "Market Map",
    sectorScores: "Sector average scores",
    riskNoteLabel: "Risk note:",
    riskNote:
      "This software is for research and education only. Sample data may be stale, incomplete, or inaccurate. Any trading decision requires independent verification of data, suitability, and risk constraints.",
    confidence: "confidence",
    points: "pts",
    noActiveFlags: "No active flags",
    noActiveFlagsDetail: "The sample model found no major warnings.",
    completeRows: "Complete rows",
    requiredFieldsChecked: "{count} required fields checked",
    averageConfidence: "Average confidence",
    modelTrust: "Penalty-adjusted model trust",
    riskFlags: "Risk flags",
    highSeverity: "{count} high severity",
    factorAverages: "Factor averages",
    stocksCount: "{count} stocks",
    thesis: "{name} ranks as {rating}. Strength in {strengths}. Monitor {weaknesses}.",
    thesisNoStrength: "{name} ranks as {rating}. No dominant factor edge. Monitor {weaknesses}.",
    thesisNoWeakness: "{name} ranks as {rating}. Strength in {strengths}. No severe factor weakness in the sample model.",
    thesisNeutral: "{name} ranks as {rating}. No dominant factor edge. No severe factor weakness in the sample model."
  },
  zh: {
    appEyebrow: "研究工作台",
    appTitle: "股票分析器",
    modelStatus: "本地模型",
    language: "语言",
    heroEyebrow: "多因子股票研究",
    heroTitle: "用质量、估值、成长、动量和风险信号给股票排序",
    heroBody:
      "这是一个本地研究工具。它不承诺收益，也不替代个人投资建议。模型会把评分逻辑展示出来，方便后续接入真实行情、财报和组合约束。",
    universe: "股票池",
    average: "平均分",
    topSector: "领先行业",
    sector: "行业",
    style: "风格",
    minScore: "最低分",
    allSectors: "全部行业",
    allStyles: "全部风格",
    balanced: "均衡",
    growthTilt: "成长倾向",
    valueTilt: "价值倾向",
    rankings: "排行榜",
    candidateUniverse: "候选股票池",
    refresh: "刷新",
    selectedStock: "已选股票",
    selectStock: "选择一只股票查看模型解释",
    detailHelp: "详情会展示评分、置信度、因子贡献、风险提示和原始指标。",
    noMatches: "没有符合条件的股票",
    relaxFilters: "放宽筛选条件以扩大研究股票池。",
    diagnosticsEyebrow: "模型诊断",
    diagnosticsTitle: "数据质量与因子健康度",
    marketMap: "市场地图",
    sectorScores: "行业平均分",
    riskNoteLabel: "风险提示：",
    riskNote:
      "本软件仅用于研究和教学。样例数据可能过时、不完整或不准确。任何交易决策都需要独立验证数据、适配性和风险约束。",
    confidence: "置信度",
    points: "分",
    noActiveFlags: "暂无风险提示",
    noActiveFlagsDetail: "样例模型没有发现主要警示。",
    completeRows: "完整数据行",
    requiredFieldsChecked: "已检查 {count} 个必填字段",
    averageConfidence: "平均置信度",
    modelTrust: "扣除惩罚后的模型可信度",
    riskFlags: "风险提示",
    highSeverity: "{count} 个高严重度",
    factorAverages: "因子平均分",
    stocksCount: "{count} 只股票",
    thesis: "{name} 评级为 {rating}。优势在于 {strengths}。需要关注 {weaknesses}。",
    thesisNoStrength: "{name} 评级为 {rating}。没有突出的因子优势。需要关注 {weaknesses}。",
    thesisNoWeakness: "{name} 评级为 {rating}。优势在于 {strengths}。样例模型没有发现严重因子弱点。",
    thesisNeutral: "{name} 评级为 {rating}。没有突出的因子优势。样例模型没有发现严重因子弱点。"
  },
  ja: {
    appEyebrow: "リサーチワークベンチ",
    appTitle: "株式アナライザー",
    modelStatus: "ローカルモデル",
    language: "言語",
    heroEyebrow: "マルチファクター株式分析",
    heroTitle: "品質、バリュエーション、成長、モメンタム、リスクで銘柄を順位付け",
    heroBody:
      "これはローカルのリサーチツールです。リターンを保証せず、個別の投資助言の代替にもなりません。スコアリングの根拠を見える形にし、次の段階で実データ、開示資料、ポートフォリオ制約を接続しやすくします。",
    universe: "ユニバース",
    average: "平均スコア",
    topSector: "上位セクター",
    sector: "セクター",
    style: "スタイル",
    minScore: "最低スコア",
    allSectors: "全セクター",
    allStyles: "全スタイル",
    balanced: "バランス",
    growthTilt: "成長重視",
    valueTilt: "割安重視",
    rankings: "ランキング",
    candidateUniverse: "候補ユニバース",
    refresh: "更新",
    selectedStock: "選択銘柄",
    selectStock: "銘柄を選択してモデル説明を確認",
    detailHelp: "詳細ではスコア、信頼度、ファクター寄与、警告、元指標を表示します。",
    noMatches: "条件に合う銘柄がありません",
    relaxFilters: "条件を緩めてリサーチ対象を広げてください。",
    diagnosticsEyebrow: "モデル診断",
    diagnosticsTitle: "データ品質とファクター健全性",
    marketMap: "マーケットマップ",
    sectorScores: "セクター平均スコア",
    riskNoteLabel: "リスク注記：",
    riskNote:
      "本ソフトウェアは調査と学習のみを目的としています。サンプルデータは古い、不完全、または不正確な可能性があります。売買判断にはデータ、適合性、リスク制約の独立した確認が必要です。",
    confidence: "信頼度",
    points: "点",
    noActiveFlags: "有効な警告なし",
    noActiveFlagsDetail: "サンプルモデルでは大きな警告は検出されませんでした。",
    completeRows: "完全な行",
    requiredFieldsChecked: "{count} 個の必須項目を確認",
    averageConfidence: "平均信頼度",
    modelTrust: "ペナルティ調整後のモデル信頼度",
    riskFlags: "リスク警告",
    highSeverity: "高重大度 {count} 件",
    factorAverages: "ファクター平均",
    stocksCount: "{count} 銘柄",
    thesis: "{name} の評価は {rating} です。強みは {strengths}。注意点は {weaknesses}。",
    thesisNoStrength: "{name} の評価は {rating} です。明確なファクター優位性はありません。注意点は {weaknesses}。",
    thesisNoWeakness: "{name} の評価は {rating} です。強みは {strengths}。サンプルモデルでは深刻なファクター弱点はありません。",
    thesisNeutral: "{name} の評価は {rating} です。明確なファクター優位性はありません。サンプルモデルでは深刻なファクター弱点はありません。"
  }
};

export const factorLabels = {
  en: {
    momentum: "Momentum",
    value: "Valuation",
    quality: "Quality",
    growth: "Growth",
    risk: "Risk control"
  },
  zh: {
    momentum: "动量",
    value: "估值",
    quality: "质量",
    growth: "成长",
    risk: "风险控制"
  },
  ja: {
    momentum: "モメンタム",
    value: "バリュエーション",
    quality: "品質",
    growth: "成長",
    risk: "リスク管理"
  }
};

export const ratingLabels = {
  en: {
    "Strong Watch": "Strong Watch",
    Watch: "Watch",
    Neutral: "Neutral",
    Weak: "Weak",
    Avoid: "Avoid"
  },
  zh: {
    "Strong Watch": "强关注",
    Watch: "关注",
    Neutral: "中性",
    Weak: "偏弱",
    Avoid: "回避"
  },
  ja: {
    "Strong Watch": "強い注目",
    Watch: "注目",
    Neutral: "中立",
    Weak: "弱い",
    Avoid: "回避"
  }
};

export const sectorLabels = {
  en: {},
  zh: {
    Technology: "科技",
    Financials: "金融",
    Healthcare: "医疗健康",
    Utilities: "公用事业",
    Industrials: "工业",
    "Consumer Staples": "必需消费",
    Energy: "能源"
  },
  ja: {
    Technology: "テクノロジー",
    Financials: "金融",
    Healthcare: "ヘルスケア",
    Utilities: "公益事業",
    Industrials: "資本財",
    "Consumer Staples": "生活必需品",
    Energy: "エネルギー"
  }
};

export const flagMessages = {
  en: {
    expensive_valuation: ["Expensive valuation", "High valuation multiples reduce margin of safety."],
    high_market_risk: ["High market risk", "Beta or realized volatility is elevated."],
    leverage: ["Leverage watch", "Debt-to-equity is above the model comfort zone."],
    weak_growth: ["Weak growth", "Growth factor is below the neutral threshold."],
    liquidity: ["Liquidity watch", "Liquidity score is below preferred level."],
    missing_data: ["Missing required fields", "Some required inputs are missing."]
  },
  zh: {
    expensive_valuation: ["估值偏高", "较高的估值倍数会压缩安全边际。"],
    high_market_risk: ["市场风险偏高", "Beta 或波动率处于较高水平。"],
    leverage: ["杠杆关注", "资产负债结构高于模型舒适区间。"],
    weak_growth: ["成长偏弱", "成长因子低于中性阈值。"],
    liquidity: ["流动性关注", "流动性评分低于偏好水平。"],
    missing_data: ["缺少必填字段", "部分模型输入数据缺失。"]
  },
  ja: {
    expensive_valuation: ["割高な評価", "高い評価倍率は安全余裕を小さくします。"],
    high_market_risk: ["市場リスク高め", "ベータまたは実現ボラティリティが高い水準です。"],
    leverage: ["レバレッジ注意", "D/E レシオがモデルの快適圏を上回っています。"],
    weak_growth: ["成長力が弱い", "成長ファクターが中立基準を下回っています。"],
    liquidity: ["流動性注意", "流動性スコアが望ましい水準を下回っています。"],
    missing_data: ["必須項目の欠損", "一部のモデル入力が欠損しています。"]
  }
};

export function createI18n(initialLanguage) {
  let language = normalizeLanguage(initialLanguage);

  return {
    get language() {
      return language;
    },
    setLanguage(nextLanguage) {
      language = normalizeLanguage(nextLanguage);
      localStorage.setItem("stock-analyzer-language", language);
    },
    t(key, params = {}) {
      const template = messages[language][key] ?? messages.en[key] ?? key;
      return Object.entries(params).reduce(
        (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
        template
      );
    },
    factor(name) {
      return factorLabels[language][name] ?? factorLabels.en[name] ?? name;
    },
    rating(name) {
      return ratingLabels[language][name] ?? ratingLabels.en[name] ?? name;
    },
    sector(name) {
      return sectorLabels[language][name] ?? name;
    },
    flag(flag) {
      const pair = flagMessages[language][flag.code] ?? flagMessages.en[flag.code];
      if (!pair) return [flag.label, flag.detail];
      return pair;
    }
  };
}

export function detectLanguage() {
  const saved = localStorage.getItem("stock-analyzer-language");
  if (saved) return normalizeLanguage(saved);
  return normalizeLanguage(navigator.language);
}

function normalizeLanguage(language) {
  const normalized = String(language || "en").toLowerCase();
  if (normalized.startsWith("zh")) return "zh";
  if (normalized.startsWith("ja")) return "ja";
  return "en";
}
