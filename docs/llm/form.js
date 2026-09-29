// Shared form handling for the LLM quota planner.
//
// The form asks only what a customer can answer — which kind of deployment,
// how many people, how often — and derives the rest from the scenario's token
// profile. Token counts, per-application breakdowns and account-specific
// quotas live in the advanced panel for whoever needs them.
//
// The two front ends differ in exactly one respect: how a workload turns into
// a report. The static GitHub Pages build computes it locally with engine.js;
// the FastAPI page posts it to /api/llm-quota. That single difference is
// injected as `window.llmEvaluate`.
//
// Requires: data.js (LLM_CONST / LLM_LINES / LLM_MODELS / LLM_SCENARIOS / LLM_PLANS),
//           render.js (renderLLMReport).

(function () {
  'use strict';

  const evaluate = w =>
    (typeof window.llmEvaluate === 'function')
      ? window.llmEvaluate(w)
      : Promise.resolve(evaluateWorkload(w, null));

  const EFFORT_LABELS = { low: '低', medium: '中', high: '高', xhigh: '極高' };

  const PEAK_LABELS = {
    flat:   ['平穩', '背景批次、排程作業，流量整天散開'],
    normal: ['一般', '上班時間使用，有明顯的忙碌時段'],
    spiky:  ['集中', '活動檔期、早會後、上課時間，短時間湧入'],
  };

  let scenarioId = 'rag';
  let customised = false;          // advanced panel has been edited
  let apps = [];
  let accounts = [];
  // Measured usage replacing the scenario's token profile:
  // { usage, includes, profile, before } or null.
  let calibration = null;

  const $ = id => document.getElementById(id);
  const scenario = id => LLM_SCENARIOS.find(s => s.scenario_id === id);

  function plansFor(model) {
    return (typeof listPlans === 'function')
      ? listPlans(model, null)
      : LLM_PLANS.filter(p => p.model === model);
  }
  function modelInfo(id) {
    return (typeof getModel === 'function')
      ? getModel(id)
      : LLM_MODELS.find(m => m.model === id);
  }
  const currentModel = () => $('llm_model').value || 'fable-5-1';
  const lineOf = id => (modelInfo(id) || {}).line || 'claude';
  const modelsOf = line => LLM_MODELS.filter(m => m.line === line);
  const ACCT_LABELS = { rpm: 'RPM', itpm: 'ITPM', otpm: 'OTPM', tpm: 'TPM', rpd: 'RPD', usd10m: '每 10 分鐘 $' };

  // Two-level picker: the vendor line, then a version inside it.
  function populateVersions(line, selected) {
    $('llm_model').innerHTML = modelsOf(line).map(m =>
      '<option value="' + m.model + '"' + (m.model === selected ? ' selected' : '') + '>' +
      llmEsc(m.version_label || m.label) + '　$' + m.pricing.input_per_mtok + ' / $' +
      m.pricing.output_per_mtok + ' per MTok</option>').join('');
  }

  function setModel(id) {
    const line = lineOf(id);
    $('llm_line').value = line;
    populateVersions(line, id);
    $('llm_model').value = id;
    // Account overrides are per plan id, which differ between models.
    const valid = plansFor(id).map(p => p.plan_id);
    accounts = accounts.filter(o => valid.indexOf(o.plan_id) >= 0);
  }

  // -- scenario -> workload ------------------------------------------------

  // Mirrors cloudcost.llm.planner.size_from_scenario. The peak factor is the
  // load-bearing assumption: quota is a per-minute ceiling, so how sharply the
  // day piles into the busiest minute matters more than the daily total.
  function peakRpmPerUser(perDay, profile) {
    const factor = LLM_CONST.PEAK_FACTORS[profile] || LLM_CONST.PEAK_FACTORS.normal;
    return (perDay / (LLM_CONST.ACTIVE_HOURS_PER_DAY * 60)) * factor;
  }

  function thinkingFor(s) {
    const factor = LLM_CONST.EFFORT_THINKING_FACTORS[$('llm_effort').value] || 1;
    return Math.round(s.thinking_tokens_per_request * factor);
  }

  function rebuildFromScenario() {
    const s = scenario(scenarioId);
    const users = Math.max(1, Math.round(parseFloat($('llm_users').value) || 1));
    const perDay = Math.max(0.01, parseFloat($('llm_per_day').value) || s.messages_per_user_per_day);
    const p = calibration && calibration.profile;
    apps = [{
      name: s.label,
      concurrent_users: users,
      requests_per_user_per_minute: Math.max(0.0001, peakRpmPerUser(perDay, $('llm_peak').value)),
      input_tokens_per_request: p ? p.input_tokens_per_request : s.input_tokens_per_request,
      output_tokens_per_request: p ? p.output_tokens_per_request : s.output_tokens_per_request,
      thinking_tokens_per_request: p ? p.thinking_tokens_per_request : thinkingFor(s),
      cache_hit_rate: p ? p.cache_hit_rate : s.cache_hit_rate,
      cache_write_rate: p ? p.cache_write_rate : 0,
    }];
    $('llm_max').value = s.max_tokens;
    $('llm_monthly').value = Math.round(users * perDay * LLM_CONST.WORKING_DAYS_PER_MONTH);
  }

  function selectScenario(id) {
    scenarioId = id;
    customised = false;
    // Measured usage describes one workload; a different scenario is another.
    if (calibration) { calibration = null; renderCalibration(null); }
    const s = scenario(id);
    setModel(llmModelFor($('llm_line').value || 'claude', s.suggested_class));
    $('llm_per_day').value = s.messages_per_user_per_day;
    $('llm_effort').value = s.default_effort;
    $('llm_batch').checked = !!s.batch_friendly;
    rebuildFromScenario();
    renderScenarios();
    renderApps();
    syncHints();
  }

  function markCustomised() {
    if (customised) return;
    customised = true;
    renderScenarios();
    syncHints();
  }

  // -- rendering -----------------------------------------------------------

  function renderScenarios() {
    $('llm-scenarios').innerHTML = LLM_SCENARIOS.map(s =>
      '<button type="button" class="llm-scenario' +
        (s.scenario_id === scenarioId && !customised ? ' active' : '') +
        '" data-scenario="' + s.scenario_id + '">' +
        '<span class="llm-scenario-icon">' + s.icon + '</span>' +
        '<span class="llm-scenario-label">' + llmEsc(s.label) + '</span>' +
        '<span class="llm-scenario-blurb">' + llmEsc(s.blurb) + '</span></button>').join('');
    $('llm-scenarios').querySelectorAll('[data-scenario]').forEach(b =>
      b.addEventListener('click', () => { selectScenario(b.dataset.scenario); run(); }));
  }

  function syncHints() {
    const m = modelInfo(currentModel());
    $('llm-model-hint').innerHTML =
      llmEsc(m.notes[0] || '') + '　快取讀取 $' + m.pricing.cache_read_per_mtok + '/MTok';

    const total = apps.reduce((t, a) => t + a.concurrent_users * a.requests_per_user_per_minute, 0);
    const perDay = parseFloat($('llm_per_day').value) || 0;
    const users = apps.reduce((t, a) => t + a.concurrent_users, 0);
    const profile = PEAK_LABELS[$('llm_peak').value] || PEAK_LABELS.normal;
    const factor = LLM_CONST.PEAK_FACTORS[$('llm_peak').value] || LLM_CONST.PEAK_FACTORS.normal;

    const cal = calibration && calibration.profile;
    $('llm-derived').innerHTML = cal && !customised
      ? '依實際用量校正：' + users.toLocaleString() + ' 人 × 每人每天 ' + perDay +
        ' 次（試用期實測）÷ ' + LLM_CONST.ACTIVE_HOURS_PER_DAY + ' 小時 × ' + factor + '（' + profile[0] + '）' +
        ' ＝ 尖峰 <b>' + Math.round(total).toLocaleString() + '</b> Requests/min。' +
        '　單次 <b>' + cal.input_tokens_per_request.toLocaleString() + '</b> Input / <b>' +
        (cal.output_tokens_per_request + cal.thinking_tokens_per_request).toLocaleString() + '</b> Output tokens，' +
        '快取命中 <b>' + Math.round(cal.cache_hit_rate * 100) + '%</b>' +
        (cal.cache_write_rate > 0 ? '、快取寫入 <b>' + Math.round(cal.cache_write_rate * 100) + '%</b>' : '') +
        '。<span class="llm-custom-flag llm-cal-flag">已校正</span>'
      : customised
      ? '已在進階設定中自訂，上方的情境與規模欄位不再覆寫。<span class="llm-custom-flag">自訂</span>' +
        '　目前尖峰 <b>' + Math.round(total).toLocaleString() + '</b> Requests/min，共 ' +
        apps.length + ' 個應用。'
      : '由以上推導：' + users.toLocaleString() + ' 人 × 每人每天 ' + perDay +
        ' 次 ÷ ' + LLM_CONST.ACTIVE_HOURS_PER_DAY + ' 小時 × ' + factor + '（' + profile[0] + '）' +
        ' ＝ 尖峰 <b>' + Math.round(total).toLocaleString() + '</b> Requests/min。' +
        '　單次 <b>' + apps[0].input_tokens_per_request.toLocaleString() + '</b> Input / <b>' +
        apps[0].output_tokens_per_request.toLocaleString() + '</b> Output tokens，' +
        '固定前綴 <b>' + Math.round(apps[0].cache_hit_rate * 100) + '%</b> 可快取，' +
        '另有約 <b>' + (apps[0].thinking_tokens_per_request || 0).toLocaleString() + '</b> 思考 tokens' +
        '（思考強度「' + (EFFORT_LABELS[$('llm_effort').value] || '') + '」，按 Output 計費）。' +
        '以上為情境預設的規劃估計，可在進階設定調整。';
  }

  // step="any": a stepped input rejects values off its min-anchored grid (8 with
  // min 0.1 step 1, 20,000 with min 1 step 100) and silently blocks the submit.
  function num(i, field, label, unit, value, min, max, hint) {
    return '<div class="form-group"><label>' + label + ' <span class="unit">' + unit + '</span></label>' +
      '<input type="number" data-app-field="' + field + '" value="' + value + '" min="' + min +
      '" max="' + max + '" step="any" required>' + (hint || '') + '</div>';
  }

  // Official guidance: ~4 English characters per token. CJK runs hotter, so the
  // hint says so rather than inventing a ratio.
  function tokenHint(tokens) {
    if (!tokens) return '';
    return '≈ ' + (tokens * 4).toLocaleString() + ' 個英文字元（1 token ≒ 4 字元；中文較耗 token，請抓寬）';
  }

  function appRow(a, i) {
    const rm = apps.length > 1
      ? '<button type="button" class="llm-row-del" data-app-del="' + i + '" title="移除這個應用">✕</button>' : '';
    return '<div class="llm-app-row" data-app="' + i + '">' +
      '<div class="llm-app-row-head"><input type="text" class="llm-app-name" data-app-field="name" value="' +
        llmEsc(a.name) + '" placeholder="應用名稱">' + rm + '</div>' +
      '<div class="form-grid">' +
        num(i, 'concurrent_users', '使用者人數', '人', a.concurrent_users, 1, 1000000) +
        num(i, 'requests_per_user_per_minute', '尖峰每人每分鐘', 'Requests',
            Math.round(a.requests_per_user_per_minute * 10000) / 10000, 0.0001, 600) +
        num(i, 'input_tokens_per_request', '單次 Input', 'Tokens', a.input_tokens_per_request, 1, 1000000,
            '<span class="llm-hint" data-token-hint="' + i + '">' + tokenHint(a.input_tokens_per_request) + '</span>') +
        num(i, 'output_tokens_per_request', '單次回覆', 'Output Tokens', a.output_tokens_per_request, 1, 128000) +
        num(i, 'thinking_tokens_per_request', '單次思考', 'Tokens', a.thinking_tokens_per_request || 0, 0, 128000,
            '<span class="llm-hint">思考一律按 Output 計費並佔用 OTPM，即使畫面不顯示</span>') +
        num(i, 'cache_hit_rate_pct', '固定前綴佔比', '% of Input', Math.round(a.cache_hit_rate * 100), 0, 99,
            '<span class="llm-hint">System Prompt + 固定 RAG 前綴的比例，這段可以快取，不佔 ITPM</span>') +
      '</div></div>';
  }

  function renderApps() {
    const host = $('llm-app-list');
    host.innerHTML = apps.map(appRow).join('');
    host.querySelectorAll('[data-app-del]').forEach(b => b.addEventListener('click', () => {
      apps.splice(parseInt(b.dataset.appDel, 10), 1);
      markCustomised();
      renderApps();
    }));
    host.querySelectorAll('.llm-app-row').forEach(row => {
      row.querySelectorAll('[data-app-field]').forEach(input => {
        input.addEventListener('input', () => {
          markCustomised();
          collectApps();
          if (input.dataset.appField === 'input_tokens_per_request') {
            const hint = row.querySelector('[data-token-hint]');
            if (hint) hint.textContent = tokenHint(parseFloat(input.value) || 0);
          }
          syncHints();
        });
      });
    });
  }

  function collectApps() {
    document.querySelectorAll('#llm-app-list .llm-app-row').forEach(row => {
      const a = apps[parseInt(row.dataset.app, 10)];
      if (!a) return;
      row.querySelectorAll('[data-app-field]').forEach(input => {
        const f = input.dataset.appField;
        if (f === 'name') { a.name = input.value || '應用'; return; }
        const v = parseFloat(input.value);
        if (isNaN(v)) return;
        if (f === 'cache_hit_rate_pct') {
          a.cache_hit_rate = Math.min(0.99, Math.max(0, v / 100));
          a.cache_write_rate = Math.min(a.cache_write_rate || 0, 1 - a.cache_hit_rate);
        }
        else a[f] = v;
      });
    });
  }

  function accountRow(o, i) {
    const plans = plansFor(currentModel());
    const plan = plans.find(p => p.plan_id === o.plan_id) || plans[0];
    if (plan && o.plan_id !== plan.plan_id) o.plan_id = plan.plan_id;
    // Only the dimensions this platform actually meters get an input.
    // A dimension the platform does not meter (Mantle RPM) has nothing to override.
    const dims = LLM_CONST.DIMS.filter(d => plan && plan[d] && plan[d].status !== 'not_enforced');
    return '<div class="llm-account-row" data-acct="' + i + '">' +
      '<select data-acct-field="plan_id">' +
        plans.map(p => '<option value="' + p.plan_id + '"' + (p.plan_id === o.plan_id ? ' selected' : '') +
          '>' + llmEsc(p.platform_label + ' — ' + p.plan_label) + '</option>').join('') +
      '</select>' +
      dims.map(d => '<input type="number" data-acct-field="' + d + '" placeholder="' + ACCT_LABELS[d] +
        '" title="' + ACCT_LABELS[d] + '" min="0" step="any" value="' + (o[d] != null ? o[d] : '') + '">').join('') +
      '<button type="button" class="llm-row-del" data-acct-del="' + i + '" title="移除">✕</button></div>';
  }

  function renderAccounts() {
    const host = $('llm-account-list');
    host.innerHTML = accounts.map(accountRow).join('');
    host.querySelectorAll('[data-acct-del]').forEach(b => b.addEventListener('click', () => {
      accounts.splice(parseInt(b.dataset.acctDel, 10), 1);
      renderAccounts();
    }));
    host.querySelectorAll('[data-acct-field]').forEach(input => {
      input.addEventListener('input', collectAccounts);
      // A different plan meters different dimensions: redraw its inputs.
      if (input.dataset.acctField === 'plan_id') {
        input.addEventListener('change', () => { collectAccounts(); renderAccounts(); });
      }
    });
  }

  function collectAccounts() {
    document.querySelectorAll('#llm-account-list .llm-account-row').forEach(row => {
      const o = accounts[parseInt(row.dataset.acct, 10)];
      if (!o) return;
      row.querySelectorAll('[data-acct-field]').forEach(input => {
        const f = input.dataset.acctField;
        if (f === 'plan_id') { o.plan_id = input.value; return; }
        const v = parseFloat(input.value);
        o[f] = isNaN(v) ? null : v;
      });
    });
  }

  // -- read / run ----------------------------------------------------------

  function readForm() {
    collectApps();
    collectAccounts();
    const maxTok = parseFloat($('llm_max').value);
    const monthly = parseFloat($('llm_monthly').value);
    return {
      model: currentModel(),
      apps: apps.map(a => ({
        name: a.name,
        concurrent_users: Math.max(1, Math.round(a.concurrent_users)),
        requests_per_user_per_minute: Math.max(0.0001, a.requests_per_user_per_minute),
        input_tokens_per_request: Math.max(1, Math.round(a.input_tokens_per_request)),
        output_tokens_per_request: Math.max(1, Math.round(a.output_tokens_per_request)),
        thinking_tokens_per_request: Math.max(0, Math.round(a.thinking_tokens_per_request || 0)),
        cache_hit_rate: a.cache_hit_rate,
        cache_write_rate: a.cache_write_rate || 0,
      })),
      max_tokens: isNaN(maxTok) ? null : Math.min(LLM_CONST.MAX_OUTPUT_TOKENS, Math.max(1, Math.round(maxTok))),
      monthly_requests: isNaN(monthly) ? null : Math.max(0, Math.round(monthly)),
      account_quotas: accounts.filter(o => o.rpm != null || o.itpm != null || o.otpm != null),
      batch_eligible: $('llm_batch').checked,
      scenario_id: customised ? null : scenarioId,
      effort: $('llm_effort').value,
      per_day: parseFloat($('llm_per_day').value) || null,
      peak: $('llm_peak').value,
      calibration: calibration,
    };
  }

  // The API takes a workload; the rest of readForm() is page state for share links.
  function apiPayload(w) {
    const payload = Object.assign({}, w);
    ['scenario_id', 'effort', 'per_day', 'peak', 'calibration'].forEach(k => { delete payload[k]; });
    return payload;
  }

  function run() {
    const payload = apiPayload(readForm());
    const btn = document.querySelector('#llm-form .btn-compare');
    const label = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = '試算中…'; }
    return Promise.resolve(evaluate(payload))
      .then(r => { renderLLMReport(r); renderCalibration(r); return r; })
      .catch(err => {
        $('llm-warnings').innerHTML =
          '<p class="llm-warn">試算失敗：' + llmEsc(err && err.message ? err.message : err) + '</p>';
        $('llm-results').style.display = '';
      })
      .finally(() => { if (btn) { btn.disabled = false; btn.textContent = label; } });
  }

  function applyShared(w) {
    setModel(modelInfo(w.model) ? w.model : 'fable-5-1');
    $('llm_max').value = w.max_tokens != null ? w.max_tokens : '';
    $('llm_monthly').value = w.monthly_requests != null ? w.monthly_requests : '';
    apps = (w.apps && w.apps.length ? w.apps : apps).map(a => Object.assign({}, a));
    accounts = (w.account_quotas || []).map(o => Object.assign({}, o));
    if (w.effort && LLM_CONST.EFFORT_THINKING_FACTORS[w.effort]) $('llm_effort').value = w.effort;
    $('llm_batch').checked = !!w.batch_eligible;
    calibration = w.calibration && w.calibration.profile ? w.calibration : null;
    if (calibration) fillCalibrationFields(calibration);
    if (w.peak && PEAK_LABELS[w.peak]) $('llm_peak').value = w.peak;
    const perDay = w.per_day || (calibration && calibration.profile.per_user_per_day);
    if (perDay) $('llm_per_day').value = perDay;
    if (w.scenario_id && scenario(w.scenario_id)) {
      scenarioId = w.scenario_id;
      customised = false;
    } else {
      customised = true;
    }
    $('llm_users').value = apps.reduce((t, a) => t + a.concurrent_users, 0);
    renderScenarios();
    renderApps();
    renderAccounts();
    syncHints();
  }

  // -- calibration from measured usage -------------------------------------

  const CAL_FIELDS = { trial_users: 'llm_cal_users', days: 'llm_cal_days', requests: 'llm_cal_requests',
    input: 'llm_cal_input', cache_read: 'llm_cal_read', cache_write: 'llm_cal_write',
    output: 'llm_cal_output', thinking: 'llm_cal_thinking' };

  function lineInfo(line) { return LLM_LINES.find(l => l.line === line) || LLM_LINES[0]; }

  // The checkbox describes the console the numbers came from, so it follows
  // the picker only until a calibration is applied.
  function syncCalibrationDefaults() {
    if (!$('llm-calibration')) return;
    const info = lineInfo($('llm_line').value);
    if (!calibration) $('llm_cal_includes').checked = !!info.usage_input_includes_cache;
    $('llm-cal-hint').textContent = info.usage_hint || '';
  }

  function readCalibrationFields() {
    const u = {};
    Object.keys(CAL_FIELDS).forEach(k => {
      const v = parseFloat(String($(CAL_FIELDS[k]).value).replace(/,/g, ''));
      u[k] = isNaN(v) ? null : v;
    });
    return u;
  }

  function fillCalibrationFields(c) {
    Object.keys(CAL_FIELDS).forEach(k => {
      $(CAL_FIELDS[k]).value = c.usage[k] != null ? c.usage[k] : '';
    });
    $('llm_cal_includes').checked = !!c.includes;
  }

  // One row of what the scenario assumed next to what the customer measured.
  function snapshot(w, report) {
    const a = w.apps[0];
    const perDay = parseFloat($('llm_per_day').value) || 0;
    return {
      input: a.input_tokens_per_request,
      output: a.output_tokens_per_request + (a.thinking_tokens_per_request || 0),
      hit: a.cache_hit_rate || 0,
      write: a.cache_write_rate || 0,
      per_day: perDay,
      monthly: w.monthly_requests,
      monthly_usd: report && report.cost ? report.cost.monthly_usd : null,
      per_1k_usd: report && report.cost ? report.cost.per_1k_requests_usd : null,
    };
  }

  function renderCalibration(report) {
    if (!$('llm-calibration')) return;
    const status = $('llm-cal-status'), table = $('llm-cal-table');
    $('llm-cal-clear').style.display = calibration ? '' : 'none';
    $('llm-cal-apply').textContent = calibration ? '重新套用校正' : '套用校正';
    if (!calibration || !report) { table.innerHTML = ''; if (!calibration) status.innerHTML = ''; return; }
    const b = calibration.before, u = calibration.usage;
    const after = snapshot(report.workload, report);
    const pct = x => Math.round(x * 100) + '%';
    const tok = x => Math.round(x).toLocaleString();
    const usd = x => (x == null ? '—' : llmFmtUsd(x));
    const delta = (was, now) => {
      if (was == null || now == null || !was) return '';
      const d = Math.round((now - was) / was * 100);
      return d === 0 ? '持平' : (d > 0 ? '+' : '') + d + '%';
    };
    const rows = [
      ['每次 Input', tok(b.input), tok(after.input), delta(b.input, after.input)],
      ['每次 Output（含思考）', tok(b.output), tok(after.output), delta(b.output, after.output)],
      ['快取命中率', pct(b.hit), pct(after.hit), ''],
      ['快取寫入', pct(b.write), pct(after.write), ''],
      ['每人每天使用次數', b.per_day, after.per_day, delta(b.per_day, after.per_day)],
      ['每月請求數', b.monthly != null ? tok(b.monthly) : '—', after.monthly != null ? tok(after.monthly) : '—',
       delta(b.monthly, after.monthly)],
      ['每 1,000 次請求', usd(b.per_1k_usd), usd(after.per_1k_usd), delta(b.per_1k_usd, after.per_1k_usd)],
      ['預估月費', usd(b.monthly_usd), usd(after.monthly_usd), delta(b.monthly_usd, after.monthly_usd)],
    ];
    status.innerHTML = '<p class="llm-cal-ok">&#10003; 已依 ' + tok(u.trial_users) + ' 人、' + u.days + ' 天、' +
      tok(u.requests) + ' 次請求的實際用量校正，上方所有結果皆已重算。尖峰仍依上方的使用人數與尖峰集中度推算。</p>';
    table.innerHTML = '<div class="llm-table-wrap"><table class="llm-table llm-cal-table"><thead><tr>' +
      '<th>項目</th><th>情境估計</th><th>實際用量</th><th>差異</th></tr></thead><tbody>' +
      rows.map((r, i) => '<tr' + (i === rows.length - 1 ? ' class="llm-cal-total"' : '') + '><td>' + r[0] +
        '</td><td>' + r[1] + '</td><td><b>' + r[2] + '</b></td><td>' + r[3] + '</td></tr>').join('') +
      '</tbody></table></div>';
  }

  function applyCalibration() {
    const usage = readCalibrationFields();
    const includes = $('llm_cal_includes').checked;
    const profile = llmCalibrate(usage, includes);
    if (profile.error) {
      $('llm-cal-status').innerHTML = '<p class="llm-warn">' + llmEsc(profile.error) + '</p>';
      return;
    }
    const baseline = calibration ? Promise.resolve(calibration.before) : (() => {
      const w = readForm();
      return Promise.resolve(evaluate(apiPayload(w))).then(r => snapshot(w, r));
    })();
    baseline.then(before => {
      calibration = { usage: usage, includes: includes, profile: profile, before: before };
      $('llm_per_day').value = profile.per_user_per_day;
      if (!customised) {
        rebuildFromScenario();
      } else {
        collectApps();
        const a = apps[0];
        Object.assign(a, {
          input_tokens_per_request: profile.input_tokens_per_request,
          output_tokens_per_request: profile.output_tokens_per_request,
          thinking_tokens_per_request: profile.thinking_tokens_per_request,
          cache_hit_rate: profile.cache_hit_rate,
          cache_write_rate: profile.cache_write_rate,
          requests_per_user_per_minute: Math.max(0.0001, peakRpmPerUser(profile.per_user_per_day, $('llm_peak').value)),
        });
        if (apps.length === 1) {
          $('llm_monthly').value = Math.round(a.concurrent_users * profile.per_user_per_day * LLM_CONST.WORKING_DAYS_PER_MONTH);
        }
      }
      renderApps();
      syncHints();
      return run();
    }).then(() => {
      const top = $('llm-summary');
      if (top && top.scrollIntoView) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function clearCalibration() {
    const before = calibration && calibration.before;
    calibration = null;
    if (before && before.per_day) $('llm_per_day').value = before.per_day;
    if (!customised) rebuildFromScenario();
    else apps.forEach(a => { a.cache_write_rate = 0; });
    renderApps();
    syncHints();
    syncCalibrationDefaults();
    run();
  }

  // -- wiring --------------------------------------------------------------

  $('llm_line').innerHTML = LLM_LINES.map(l =>
    '<option value="' + l.line + '">' + llmEsc(l.label + '（' + l.vendor + '）') + '</option>').join('');
  setModel('fable-5-1');
  $('llm_peak').innerHTML = Object.keys(PEAK_LABELS).map(k =>
    '<option value="' + k + '"' + (k === 'normal' ? ' selected' : '') + '>' +
    PEAK_LABELS[k][0] + '　' + PEAK_LABELS[k][1] + '</option>').join('');

  ['llm_users', 'llm_per_day', 'llm_peak'].forEach(id => {
    $(id).addEventListener('input', () => {
      if (customised) { syncHints(); return; }
      rebuildFromScenario();
      renderApps();
      syncHints();
    });
    $(id).addEventListener('change', () => {
      if (!customised) { rebuildFromScenario(); renderApps(); }
      syncHints();
      run();
    });
  });

  $('llm_line').addEventListener('change', () => {
    // Keep the capability level when switching vendor: a balanced Claude
    // becomes a balanced GPT, not whatever happens to be listed first.
    const cls = (modelInfo(currentModel()) || {}).model_class || 'balanced';
    setModel(llmModelFor($('llm_line').value, cls));
    syncCalibrationDefaults();
    syncHints(); renderAccounts(); run();
  });
  $('llm_model').addEventListener('change', () => {
    setModel(currentModel());
    syncHints(); renderAccounts(); run();
  });
  ['llm_max', 'llm_monthly'].forEach(id =>
    $(id).addEventListener('input', () => { markCustomised(); }));

  $('llm-add-app').addEventListener('click', () => {
    collectApps();
    markCustomised();
    const s = scenario(scenarioId);
    apps.push({ name: '應用 ' + (apps.length + 1), concurrent_users: 50,
      requests_per_user_per_minute: peakRpmPerUser(s.messages_per_user_per_day, $('llm_peak').value),
      input_tokens_per_request: s.input_tokens_per_request,
      output_tokens_per_request: s.output_tokens_per_request,
      cache_hit_rate: s.cache_hit_rate });
    renderApps();
    syncHints();
  });

  $('llm-add-account').addEventListener('click', () => {
    collectAccounts();
    accounts.push({ plan_id: 'mantle', rpm: null, itpm: null, otpm: null });
    renderAccounts();
  });

  $('llm-form').addEventListener('submit', e => { e.preventDefault(); run(); });
  if ($('llm-calibration')) {
    $('llm-cal-apply').addEventListener('click', applyCalibration);
    $('llm-cal-clear').addEventListener('click', clearCalibration);
  }

  $('llm-btn-share').addEventListener('click', () => {
    const url = location.origin + location.pathname + '?llm=' +
      encodeURIComponent(JSON.stringify(readForm()));
    $('llm-share-url').value = url;
    $('llm-share-bar').style.display = 'flex';
    if (navigator.clipboard) navigator.clipboard.writeText(url).catch(() => {});
  });
  $('llm-copy-url').addEventListener('click', () => {
    $('llm-share-url').select();
    if (navigator.clipboard) navigator.clipboard.writeText($('llm-share-url').value).catch(() => {});
  });

  $('llm_effort').innerHTML = Object.keys(EFFORT_LABELS).map(k =>
    '<option value="' + k + '">' + EFFORT_LABELS[k] + '（' + k + '）</option>').join('');
  $('llm_effort').addEventListener('change', () => {
    if (!customised) { rebuildFromScenario(); renderApps(); }
    syncHints();
    run();
  });
  $('llm_batch').addEventListener('change', run);

  // Currency: reuse the site-wide rate when the page has one.
  const siteRate = $('usd-rate');
  if (siteRate) {
    const box = $('llm-fx-group');
    if (box) box.style.display = 'none';
    siteRate.addEventListener('input', () => llmRerender());
  } else if ($('llm_fx')) {
    $('llm_fx').addEventListener('input', () => llmRerender());
  }

  // Model comparison table -> switch the working model.
  window.llmSelectModel = function (id) {
    setModel(id);
    syncHints();
    renderAccounts();
    run();
    const top = $('llm-summary');
    if (top && top.scrollIntoView) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Copy a plain-text summary a salesperson can paste into a proposal.
  if ($('llm-btn-copy')) {
    $('llm-btn-copy').addEventListener('click', () => {
      let text = llmSummaryText();
      if (calibration) {
        const u = calibration.usage;
        text += '\n\n本試算已依客戶實際用量校正（' + u.trial_users + ' 人、' + u.days + ' 天、' +
          Math.round(u.requests).toLocaleString() + ' 次請求）：單次 ' +
          calibration.profile.input_tokens_per_request.toLocaleString() + ' Input tokens、快取命中 ' +
          Math.round(calibration.profile.cache_hit_rate * 100) + '%、每人每天 ' +
          calibration.profile.per_user_per_day + ' 次。';
      }
      const done = () => {
        const b = $('llm-btn-copy');
        const was = b.textContent;
        b.textContent = '已複製 ✓';
        setTimeout(() => { b.textContent = was; }, 1600);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done).catch(() => window.prompt('複製以下內容', text));
      else window.prompt('複製以下內容', text);
    });
  }

  // Exact token counts need an API key, so only a page with a backend offers
  // them. It injects window.llmCountTokens; the static page explains instead.
  const counter = $('llm-counter');
  if (counter) {
    if (typeof window.llmCountTokens === 'function') {
      $('llm-counter-live').style.display = '';
      $('llm-counter-static').style.display = 'none';
      $('llm-count-btn').addEventListener('click', () => {
        const system = $('llm-count-system').value;
        const sample = $('llm-count-sample').value;
        const out = $('llm-counter-result');
        if (lineOf(currentModel()) !== 'claude') {
          out.textContent = '精算使用 Anthropic 的 tokenizer，目前只支援 Claude 模型；GPT 與 Gemini 的 token 數會不同。';
          return;
        }
        if (!system.trim() && !sample.trim()) { out.textContent = '請至少貼上一段提示詞。'; return; }
        out.textContent = '計算中…';
        Promise.resolve(window.llmCountTokens({ model: currentModel(), system: system, sample: sample }))
          .then(res => {
            collectApps();
            markCustomised();
            const a = apps[0];
            a.input_tokens_per_request = Math.max(1, res.total_tokens);
            a.cache_hit_rate = res.total_tokens > 0
              ? Math.min(0.95, Math.max(0, res.prefix_tokens / res.total_tokens)) : 0;
            renderApps();
            syncHints();
            out.innerHTML = '實測：固定前綴 <b>' + res.prefix_tokens.toLocaleString() + '</b> tokens、單次共 <b>' +
              res.total_tokens.toLocaleString() + '</b> tokens，已套用到第一個應用（固定前綴佔比 ' +
              Math.round(a.cache_hit_rate * 100) + '%）。';
            run();
          })
          .catch(err => { out.textContent = '無法計算：' + (err && err.message ? err.message : err); });
      });
    } else {
      $('llm-counter-live').style.display = 'none';
      $('llm-counter-static').style.display = '';
    }
  }

  // -- boot ----------------------------------------------------------------

  const shared = new URLSearchParams(location.search).get('llm');
  if (shared) {
    try {
      applyShared(JSON.parse(shared));
      const tab = [].slice.call(document.querySelectorAll('.mode-tab'))
        .filter(t => t.dataset.mode === 'llm')[0];
      if (tab) tab.click();
    } catch (err) {
      selectScenario(scenarioId);   // a malformed link falls back to the default
    }
  } else {
    selectScenario(scenarioId);
  }
  syncCalibrationDefaults();
  run();
})();
