// Browser port of cloudcost/llm/planner.py.
//
// GitHub Pages has no backend, so the static page computes the report
// locally. This file emits exactly the same JSON shape the /api/llm-quota
// endpoint returns, which lets render.js be shared by both front ends and
// lets tests/test_llm_assets.py diff this implementation against the Python
// one under Node. Keep the two in step: change a rule here, change
// planner.py too, and the parity test will tell you if you forgot.
//
// Reads LLM_CONST / LLM_MODELS / LLM_PLANS from data.js (generated).

/* global LLM_CONST, LLM_MODELS, LLM_PLANS */

(function (root) {
  'use strict';

  const data = (typeof LLM_CONST !== 'undefined') ? null : require('./data.js');
  const C = data ? data.LLM_CONST : LLM_CONST;
  const MODELS = data ? data.LLM_MODELS : LLM_MODELS;
  const PLANS = data ? data.LLM_PLANS : LLM_PLANS;

  const MAX_OUTPUT_TOKENS = C.MAX_OUTPUT_TOKENS;
  const DIMS = ['rpm', 'itpm', 'otpm'];

  function round(n, digits) {
    const f = Math.pow(10, digits);
    return Math.round((n + Number.EPSILON) * f) / f;
  }
  const fmt = n => Math.round(n).toLocaleString('en-US');
  const getModel = id => MODELS.find(m => m.model === id);
  const listPlans = (model, platform) =>
    PLANS.filter(p => (!model || p.model === model) && (!platform || p.platform === platform));

  // -- workload -----------------------------------------------------------

  const appRpm = a => a.concurrent_users * (a.requests_per_user_per_minute || 0);
  const uncachedInput = a => a.input_tokens_per_request * (1 - (a.cache_hit_rate || 0));
  const cachedInput = a => a.input_tokens_per_request * (a.cache_hit_rate || 0);
  const billedOutput = a => a.output_tokens_per_request + (a.thinking_tokens_per_request || 0);

  function aggregate(w) {
    const apps = w.apps || [];
    const sum = fn => apps.reduce((t, a) => t + fn(a), 0);
    const rpm = sum(appRpm);
    const effMax = w.max_tokens != null ? w.max_tokens : MAX_OUTPUT_TOKENS;
    const itpm = sum(a => appRpm(a) * uncachedInput(a));
    return {
      total_users: sum(a => a.concurrent_users),
      rpm: rpm,
      itpm: itpm,
      cached_itpm: sum(a => appRpm(a) * cachedInput(a)),
      // OTPM counts everything generated, thinking included.
      otpm: sum(a => appRpm(a) * billedOutput(a)),
      thinking_tpm: sum(a => appRpm(a) * (a.thinking_tokens_per_request || 0)),
      raw_input_tpm: sum(a => appRpm(a) * a.input_tokens_per_request),
      effective_max_tokens: effMax,
      itpm_with_reservation: itpm + rpm * effMax,
    };
  }

  const overrideFor = (w, planId) =>
    (w.account_quotas || []).find(o => o.plan_id === planId) || null;

  // -- dimensions ---------------------------------------------------------

  function evaluateDimension(demand, limit, override) {
    let status = limit.status;
    let value = limit.value != null ? limit.value : null;
    let fromAccount = false;
    if (override != null) { status = 'enforced'; value = override; fromAccount = true; }
    if (status !== 'enforced' || value == null) {
      return { demand: round(demand, 2), limit: null, status: status, load: null,
               from_account: false, note: limit.note || '' };
    }
    // A zero quota has no meaningful ratio: Infinity is not valid JSON.
    const load = value === 0 ? null : demand / value;
    return { demand: round(demand, 2), limit: value, status: status, load: load,
             from_account: fromAccount, note: limit.note || '' };
  }

  function planDims(w, agg, plan) {
    const o = overrideFor(w, plan.plan_id);
    const pick = k => (o && o[k] != null ? o[k] : null);
    return {
      rpm: evaluateDimension(agg.rpm, plan.rpm, pick('rpm')),
      itpm: evaluateDimension(plan.reserves_max_tokens ? agg.itpm_with_reservation : agg.itpm,
                              plan.itpm, pick('itpm')),
      otpm: evaluateDimension(agg.otpm, plan.otpm, pick('otpm')),
    };
  }

  function verdictFor(dims) {
    if (DIMS.some(k => dims[k].status === 'enforced' && dims[k].limit === 0)) {
      return { verdict: 'blocked', binding: null, peak: null };
    }
    const loads = {};
    DIMS.forEach(k => { if (dims[k].load != null) loads[k] = dims[k].load; });
    const keys = Object.keys(loads);
    if (!keys.length) return { verdict: 'unknown', binding: null, peak: null };
    const binding = keys.reduce((a, b) => (loads[a] >= loads[b] ? a : b));
    const peak = loads[binding];
    const verdict = peak > 1 ? 'over' : (peak > C.AMPLE_THRESHOLD ? 'tight' : 'ample');
    return { verdict: verdict, binding: binding, peak: round(peak, 4) };
  }

  const FITS = v => v === 'ample' || v === 'tight';
  const fits = (w, agg, plan) => FITS(verdictFor(planDims(w, agg, plan)).verdict);

  function headroom(dims) {
    const ratios = DIMS.map(k => dims[k])
      .filter(d => d.status === 'enforced' && d.limit != null && d.demand > 0)
      .map(d => d.limit / d.demand);
    return ratios.length ? Math.min.apply(null, ratios) : null;
  }

  function breakevenCacheRate(agg, itpmLimit) {
    if (agg.raw_input_tpm <= 0 || itpmLimit <= 0) return null;
    const needed = 1 - itpmLimit / agg.raw_input_tpm;
    if (needed <= 0 || needed > C.MAX_SUGGESTED_CACHE_RATE) return null;
    return round(needed, 3);
  }

  // -- next actions -------------------------------------------------------

  function buildActions(w, agg, plan, dims, verdict) {
    const actions = [];

    if (verdict === 'unknown') {
      actions.push({ kind: 'enter_account_quota',
        text: '此平台未公布預設值。請到 Service Quotas 主控台搜尋 Bedrock Mantle 查出本帳號的輸入／輸出 TPM，填入上方「我的帳號配額」即可得到判讀' });
      if (w.max_tokens == null) {
        actions.push({ kind: 'set_max_tokens',
          text: '設定 max_tokens 可大幅降低 ITPM 需求：目前按模型上限 ' + fmt(MAX_OUTPUT_TOKENS) + ' 預扣，佔 ITPM 需求的絕大部分' });
      }
      return actions;
    }
    if (verdict !== 'over' && verdict !== 'blocked') return actions;

    const over = k => dims[k].status === 'enforced' && dims[k].limit != null && dims[k].demand > dims[k].limit;
    const shortfalls = DIMS.filter(over)
      .map(k => k.toUpperCase() + ' ' + fmt(dims[k].demand) + '（目前 ' + fmt(dims[k].limit) + '）');
    if (shortfalls.length) {
      actions.push({ kind: 'request_quota', text: '提報調升至：' + shortfalls.join('、') });
    }

    const samePlatform = listPlans(plan.model, plan.platform)
      .filter(p => p.plan_id !== plan.plan_id && fits(w, agg, p));
    if (samePlatform.length) {
      actions.push({ kind: 'switch_plan',
        text: '改用「' + samePlatform[0].plan_label + '」即可容納，無需另外申請' });
    }

    // Never trade capability for quota silently: stay at or below the current
    // tier, keep as much capability as possible, break ties on price.
    const current = getModel(plan.model);
    const alts = listPlans(null, plan.platform).filter(p =>
      p.plan_id === plan.plan_id && p.model !== plan.model &&
      getModel(p.model).tier <= current.tier && fits(w, agg, p));
    alts.sort((a, b) => {
      const ma = getModel(a.model), mb = getModel(b.model);
      return (mb.tier - ma.tier) ||
             (ma.pricing.input_per_mtok - mb.pricing.input_per_mtok) ||
             (ma.pricing.output_per_mtok - mb.pricing.output_per_mtok);
    });
    if (alts.length) {
      const alt = alts[0];
      const info = getModel(alt.model);
      const cheaper = info.pricing.input_per_mtok < current.pricing.input_per_mtok ? '，單價也更低' : '';
      const prefix = info.tier < current.tier ? '若 ' + alt.model_label + ' 的能力足夠，' : '';
      actions.push({ kind: 'switch_model',
        text: prefix + '同一方案改用 ' + alt.model_label + ' 就塞得下' + cheaper });
    }

    const overDims = DIMS.filter(over);
    if (overDims.length === 1 && overDims[0] === 'itpm' && dims.itpm.limit && !plan.reserves_max_tokens) {
      const rate = breakevenCacheRate(agg, dims.itpm.limit);
      if (rate != null) {
        const cur = Math.max.apply(null, (w.apps || []).map(a => a.cache_hit_rate || 0));
        actions.push({ kind: 'raise_cache',
          text: '把快取命中率提高到 ' + (rate * 100).toFixed(0) + '% 就能塞進現有額度，不必申請調額（目前 ' + (cur * 100).toFixed(0) + '%）' });
      }
    }

    if (w.batch_eligible) {
      actions.push({ kind: 'use_batch',
        text: '這類工作可以非即時處理：改走批次 API 不佔即時配額，且費用打五折' });
    }

    if (plan.reserves_max_tokens && w.max_tokens == null) {
      actions.push({ kind: 'set_max_tokens',
        text: '設定 max_tokens：目前按模型上限 ' + fmt(MAX_OUTPUT_TOKENS) + ' 預扣 ITPM' });
    }
    return actions;
  }

  // -- per plan -----------------------------------------------------------

  function evaluatePlan(w, agg, plan) {
    const dims = planDims(w, agg, plan);
    const v = verdictFor(dims);
    const h = headroom(dims);
    const notes = plan.notes.slice();
    if (plan.reserves_max_tokens) {
      notes.unshift(w.max_tokens != null
        ? 'ITPM 需求已含每次請求預扣的 max_tokens ' + fmt(agg.effective_max_tokens) + ' tokens'
        : '未指定 max_tokens，每次請求預扣模型上限 ' + fmt(MAX_OUTPUT_TOKENS) + ' tokens 的 ITPM');
    }
    return {
      model: plan.model, model_label: plan.model_label, platform: plan.platform,
      plan_id: plan.plan_id, platform_label: plan.platform_label, plan_label: plan.plan_label,
      rpm: dims.rpm, itpm: dims.itpm, otpm: dims.otpm,
      verdict: v.verdict, peak_load: v.peak, binding_dimension: v.binding,
      headroom_multiple: h != null ? round(h, 4) : null,
      max_users: h != null && agg.total_users > 0 ? Math.floor(agg.total_users * h) : null,
      actions: buildActions(w, agg, plan, dims, v.verdict),
      notes: notes, source: plan.source, verified: plan.verified,
    };
  }

  // -- cost ---------------------------------------------------------------

  function estimateCost(w, agg) {
    const price = getModel(w.model).pricing;
    const perM = 1000000;
    const uncachedUsd = agg.itpm * price.input_per_mtok / perM;
    const cacheReadUsd = agg.cached_itpm * price.cache_read_per_mtok / perM;
    const thinkingUsd = agg.thinking_tpm * price.output_per_mtok / perM;
    const replyUsd = (agg.otpm - agg.thinking_tpm) * price.output_per_mtok / perM;
    const perMinute = uncachedUsd + cacheReadUsd + replyUsd + thinkingUsd;

    const rpm = agg.rpm;
    const perRequest = rpm ? perMinute / rpm : 0;
    const per1k = perRequest * 1000;
    const noCacheMinute = (agg.raw_input_tpm * price.input_per_mtok + agg.otpm * price.output_per_mtok) / perM;
    const noCachePer1k = rpm ? (noCacheMinute / rpm) * 1000 : 0;
    const savingPct = noCachePer1k > 0 ? ((noCachePer1k - per1k) / noCachePer1k) * 100 : 0;
    const per1kOf = usd => (rpm ? round((usd / rpm) * 1000, 4) : 0);
    const batchPerRequest = perRequest * (1 - C.BATCH_DISCOUNT);
    const monthly = x => (w.monthly_requests != null ? round(x * w.monthly_requests, 2) : null);

    return {
      per_request_usd: round(perRequest, 6),
      per_1k_requests_usd: round(per1k, 4),
      per_peak_minute_usd: round(perMinute, 4),
      monthly_usd: monthly(perRequest),
      per_1k_requests_without_cache_usd: round(noCachePer1k, 4),
      cache_saving_pct: round(savingPct, 1),
      breakdown_per_1k: {
        uncached_input: per1kOf(uncachedUsd),
        cache_read: per1kOf(cacheReadUsd),
        output: per1kOf(replyUsd),
        thinking: per1kOf(thinkingUsd),
      },
      thinking_share_pct: perMinute ? round(thinkingUsd / perMinute * 100, 1) : 0,
      batch_per_1k_requests_usd: round(batchPerRequest * 1000, 4),
      batch_monthly_usd: monthly(batchPerRequest),
      caveats: [
        '以 Anthropic 官方第一方定價計算。Claude in Microsoft Foundry 同樣採標準 API 費率（以 CCU 計價開立帳單）；Amazon Bedrock 與 Google Vertex 為合作夥伴自訂定價，實際金額請以該平台價目表為準',
        '思考 token 一律按 Output 計費，即使畫面不顯示也會收費。此處的思考量是規劃估計，請以實際請求回傳的 usage.output_tokens 校正',
        '假設快取在穩定流量下由讀取持續續期，因此未計入快取寫入費用（首次寫入為輸入價的 1.25 倍，約 $' + price.cache_write_5m_per_mtok + '/MTok）',
      ],
    };
  }

  // -- comparison and sensitivity -----------------------------------------

  function scaled(w, multiplier) {
    return Object.assign({}, w, { apps: w.apps.map(a =>
      Object.assign({}, a, { requests_per_user_per_minute: a.requests_per_user_per_minute * multiplier })) });
  }

  function countFitting(w, platform) {
    const agg = aggregate(w);
    const plans = listPlans(w.model, platform);
    return [plans.filter(p => fits(w, agg, p)).length, plans.length];
  }

  function compareModels(w, platform) {
    const rows = MODELS.map(info => {
      const v = Object.assign({}, w, { model: info.model });
      const agg = aggregate(v);
      const cost = estimateCost(v, agg);
      const results = listPlans(info.model, platform).map(p => evaluatePlan(v, agg, p));
      const fitting = results.filter(r => FITS(r.verdict));
      const caps = fitting.map(r => r.max_users).filter(x => x != null);
      return {
        model: info.model, label: info.label,
        per_1k_requests_usd: cost.per_1k_requests_usd,
        monthly_usd: cost.monthly_usd,
        fitting_plans: fitting.length, total_plans: results.length,
        best_max_users: caps.length ? Math.max.apply(null, caps) : null,
        is_selected: info.model === w.model,
      };
    });
    rows.sort((a, b) => (a.per_1k_requests_usd - b.per_1k_requests_usd) ||
                        (a.label < b.label ? -1 : a.label > b.label ? 1 : 0));
    return rows;
  }

  // -- entry point --------------------------------------------------------

  function evaluateWorkload(workload, platform) {
    const w = Object.assign({ model: 'fable-5-1', apps: [], max_tokens: null, monthly_requests: null,
                              account_quotas: [], batch_eligible: false }, workload);
    const agg = aggregate(w);
    const plans = listPlans(w.model, platform || null);
    const results = plans.map(p => evaluatePlan(w, agg, p));

    const warnings = [];
    if (w.apps.every(a => (a.cache_hit_rate || 0) === 0)) {
      warnings.push('快取命中率設為 0：System Prompt 與固定 RAG 前綴通常可以快取，開啟後 ITPM 需求與費用會同時下降');
    }
    if (w.max_tokens == null && plans.some(p => p.reserves_max_tokens)) {
      warnings.push('未指定 max_tokens：Bedrock Mantle 會按模型上限 ' + fmt(MAX_OUTPUT_TOKENS) + ' tokens 預扣 ITPM，設定實際值可大幅降低被節流的機會');
    }
    if (w.max_tokens != null) {
      const needed = Math.max.apply(null, w.apps.map(billedOutput));
      if (w.max_tokens < needed) {
        warnings.push('max_tokens ' + fmt(w.max_tokens) + ' 小於單次回覆加思考的 ' + fmt(needed) + ' tokens：思考也計入 max_tokens，回應會被截斷，請調高');
      }
    }
    if (results.some(r => r.verdict === 'unknown')) {
      warnings.push('部分平台未公布預設配額。可在該平台的配額主控台查出本帳號實際額度後填入上方欄位');
    }

    const stress = countFitting(scaled(w, 2.0), platform || null);

    return {
      workload: w,
      model_label: getModel(w.model).label,
      total_users: agg.total_users,
      required_rpm: round(agg.rpm, 2),
      required_itpm: round(agg.itpm, 2),
      required_otpm: round(agg.otpm, 2),
      cached_itpm: round(agg.cached_itpm, 2),
      cost: estimateCost(w, agg),
      results: results,
      fitting_plans: results.filter(r => FITS(r.verdict)).length,
      model_comparison: compareModels(w, platform || null),
      sensitivity: [{ label: '尖峰再集中一倍', multiplier: 2.0,
                      fitting_plans: stress[0], total_plans: stress[1] }],
      warnings: warnings,
      assumptions: [
        '所有數字皆為尖峰 1 分鐘的平均值。平台採持續補充的 token bucket，同樣的量在幾秒內灌完仍可能被節流，實務上請預留突發餘裕',
        '配額為組織／訂閱層級共用。多個應用跑在同一個帳號上會共用同一個額度，此處已加總',
        '思考 token 計入 Output 費用與 OTPM。思考量隨 effort 與題目難度變動，此處為規劃估計',
        '情境的 token 量、每人每天次數與尖峰係數為規劃估計，不是任何實際部署的量測值',
        '配額資料驗證：' + (results.length ? results[0].verified : '') + '。以上皆為平台預設值，非模型本體物理上限，均可提報申請調升',
      ],
    };
  }

  const api = { evaluateWorkload, compareModels, aggregate, listPlans, getModel, MAX_OUTPUT_TOKENS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  Object.assign(root, api);
})(typeof globalThis !== 'undefined' ? globalThis : this);
