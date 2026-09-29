// Shared renderer for an /api/llm-quota report.
//
// Both front ends hand it the same object: the static page computes it
// locally with engine.js, the FastAPI page fetches it from the API. One
// renderer means the two pages cannot drift apart visually either.
//
// Expects these element ids to exist:
//   #llm-summary #llm-warnings #llm-cost #llm-models #llm-demand
//   #llm-controls #llm-cards #llm-sources #llm-assumptions

(function (root) {
  'use strict';

  const VERDICT_LABEL = {
    ample: '✅ 餘裕充沛', tight: '⚠ 接近上限', over: '⛔ 超出上限',
    blocked: '⛔ 預設為 0', unknown: '❓ 未公布',
  };
  const VERDICT_RANK = { over: 0, blocked: 1, unknown: 2, tight: 3, ample: 4 };
  const DIM_LABEL = { rpm: 'RPM', itpm: 'ITPM<span class="llm-dim-sub">Input</span>',
                      otpm: 'OTPM<span class="llm-dim-sub">Output + 思考</span>',
                      tpm: 'TPM<span class="llm-dim-sub">Input + Output 合併</span>',
                      rpd: 'RPD<span class="llm-dim-sub">每日請求</span>',
                      usd10m: '消費上限<span class="llm-dim-sub">每 10 分鐘</span>' };
  const DIMS = ['rpm', 'itpm', 'otpm', 'tpm', 'rpd', 'usd10m'];
  const ACTION_ICON = {
    request_quota: '\u{1F4C4}', switch_plan: '↕', switch_model: '\u{1F504}',
    raise_cache: '⚡', set_max_tokens: '\u{1F3AF}', enter_account_quota: '\u{1F511}',
    use_batch: '\u{1F4E6}',
  };
  const SEGMENTS = [['uncached_input', '未快取 Input'], ['cache_read', '快取讀取'], ['cache_write', '快取寫入'],
                    ['output', 'Output'], ['thinking', '思考']];

  let lastReport = null;
  let onlyFitting = false;
  let sortBy = 'platform';
  let compareAll = false;

  function vendorOf(report) {
    const m = (typeof LLM_MODELS !== 'undefined') ? LLM_MODELS.find(x => x.model === report.workload.model) : null;
    const l = m && typeof LLM_LINES !== 'undefined' ? LLM_LINES.find(x => x.line === m.line) : null;
    return l ? l.vendor : '';
  }

  // Mirrors catalog.model_for: the version of a capability class inside a
  // line — nearest class, prefer the more capable side on a tie, then order.
  function modelFor(line, cls) {
    const classes = LLM_CONST.MODEL_CLASSES;
    const want = classes.indexOf(cls) >= 0 ? classes.indexOf(cls) : 2;
    const cands = LLM_MODELS.filter(m => m.line === line);
    const ranked = cands.slice().sort((a, b) => {
      const ia = classes.indexOf(a.model_class), ib = classes.indexOf(b.model_class);
      return (Math.abs(ia - want) - Math.abs(ib - want)) || ((ia > want) - (ib > want)) ||
             (cands.indexOf(a) - cands.indexOf(b));
    });
    return ranked.length ? ranked[0].model : null;
  }

  const el = id => document.getElementById(id);
  const fits = v => v === 'ample' || v === 'tight';

  function esc(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtTok(n) {
    if (n == null || !isFinite(n)) return '—';
    const trim = s => (s.indexOf('.') >= 0 ? s.replace(/\.?0+$/, '') : s);
    if (n >= 1e6) return trim((n / 1e6).toFixed(2)) + 'M';
    if (n >= 1e3) return trim((n / 1e3).toFixed(1)) + 'K';
    return String(Math.round(n));
  }

  function fmtUsd(n) {
    if (n == null) return '—';
    if (n >= 1000) return '$' + Math.round(n).toLocaleString('en-US');
    if (n >= 1) return '$' + n.toFixed(2);
    return '$' + n.toFixed(4).replace(/0+$/, '').replace(/\.$/, '');
  }

  // USD -> TWD. The static page already has a site-wide rate in its header;
  // the FastAPI page gets one inside the planner form.
  function fxRate() {
    const input = el('usd-rate') || el('llm_fx');
    const v = input ? parseFloat(input.value) : NaN;
    return v > 0 ? v : 32;
  }
  function twd(usd) {
    return usd == null ? '' : 'NT$' + Math.round(usd * fxRate()).toLocaleString('en-US');
  }
  // `twd-hint` + data-usd lets the static page's own rate listener update it live.
  function twdSpan(usd) {
    return usd == null ? '' :
      '<span class="twd-hint llm-twd" data-usd="' + usd + '"> ≈ ' + twd(usd) + '</span>';
  }

  // -- summary ------------------------------------------------------------

  function platformCapacity(r) {
    const best = {};
    r.results.filter(x => fits(x.verdict) && x.max_users != null).forEach(x => {
      if (!best[x.platform] || x.max_users > best[x.platform].max_users) best[x.platform] = x;
    });
    return Object.keys(best).map(k => best[k]);
  }

  function renderSummary(r) {
    const host = el('llm-summary');
    if (!host) return;
    const fitting = r.results.filter(x => fits(x.verdict));
    const users = r.total_users.toLocaleString();
    const c = r.cost;
    const monthlyLine = c.monthly_usd != null
      ? fmtUsd(c.monthly_usd) + twdSpan(c.monthly_usd) : fmtUsd(c.per_1k_requests_usd) + ' / 千次';
    const costSub = (c.monthly_usd != null
      ? '以 ' + Number(r.workload.monthly_requests).toLocaleString() + ' 次/月、' : '') +
      vendorOf(r) + ' 官方牌價計算；未套用牌價的平台另依其定價';

    const stress = (r.sensitivity || [])[0];
    let stressLine = '';
    if (stress) {
      stressLine = stress.fitting_plans === 0
        ? '壓力測試：若尖峰再集中一倍，<strong>沒有任何方案</strong>的預設配額撐得住，建議先申請調額預留餘裕。'
        : stress.fitting_plans < fitting.length
          ? '壓力測試：若尖峰再集中一倍，可用方案從 ' + fitting.length + ' 個降到 ' + stress.fitting_plans + ' 個。'
          : '壓力測試：即使尖峰再集中一倍，' + stress.fitting_plans + ' 個方案仍撐得住，結論穩定。';
    }
    const batchLine = r.workload.batch_eligible && c.batch_monthly_usd != null
      ? '<p class="llm-summary-note">\u{1F4E6} 這類工作可以非即時處理：改走批次 API 月費約 ' +
        fmtUsd(c.batch_monthly_usd) + twdSpan(c.batch_monthly_usd) + '，且不佔即時配額。</p>' : '';

    let head, tone, tiles;
    if (fitting.length) {
      const caps = platformCapacity(r).sort((a, b) => a.max_users - b.max_users);
      const listed = caps.filter(x => x.list_priced).map(x => x.platform_label);
      const partner = caps.filter(x => !x.list_priced).map(x => x.platform_label);
      tone = 'ok';
      head = '<strong>' + users + ' 位使用者撐得住，不必先申請調額。</strong>' +
        (listed.length ? listed.join('、') + ' 可直接套用下方月費' : '') +
        (listed.length && partner.length ? '；' : '') +
        (partner.length ? partner.join('、') + ' 同樣撐得住，但費用需依該平台定價另計' : '') + '。';
      tiles = [
        ['每月費用', monthlyLine, costSub],
        ['保守可成長到', caps.length ? caps[0].max_users.toLocaleString() + ' 人' : '—',
         caps.map(x => x.platform_label + ' ' + x.plan_label.replace(/\s*\(.*\)$/, '') + ' ' +
           x.max_users.toLocaleString() + ' 人').join(' · ')],
        ['可用方案', fitting.length + ' / ' + r.results.length, '其餘方案需先申請調額或未公布配額'],
      ];
    } else {
      const closest = r.results.filter(x => x.peak_load != null).sort((a, b) => a.peak_load - b.peak_load)[0];
      const fix = closest && closest.actions.length ? closest.actions[0].text : '';
      tone = 'warn';
      head = '<strong>預設配額不夠用。</strong>' +
        (closest ? '最接近的是 ' + esc(closest.platform_label) + ' ' + esc(closest.plan_label) +
          '，' + esc(fix) : '每個方案都需要先申請調額。') + ' 下方每張卡片都列出了具體的下一步。';
      tiles = [
        ['每月費用', monthlyLine, costSub],
        ['尖峰需求', fmtTok(r.required_itpm) + ' ITPM', '未快取輸入，配額最常卡住的一項'],
        ['可用方案', '0 / ' + r.results.length, '調額後即可使用，配額並非模型上限'],
      ];
    }

    host.innerHTML = '<div class="llm-summary ' + tone + '">' +
      '<p class="llm-summary-head">' + head + '</p>' +
      '<div class="llm-summary-tiles">' + tiles.map(t =>
        '<div><span class="llm-summary-label">' + esc(t[0]) + '</span>' +
        '<span class="llm-summary-value">' + t[1] + '</span>' +
        '<span class="llm-summary-sub">' + esc(t[2]) + '</span></div>').join('') + '</div>' +
      (stressLine ? '<p class="llm-summary-note">' + stressLine + '</p>' : '') + batchLine +
      '</div>';
  }

  // -- cost ---------------------------------------------------------------

  // -- calibration from measured usage --------------------------------------

  // Turns a period's usage totals (as a vendor console reports them) into the
  // per-request profile the planner works with. `includesCache` says whether
  // the console's input figure already counts cache reads and writes.
  function calibrateFromUsage(u, includesCache) {
    const n = v => (v == null || v === '' || isNaN(v) ? 0 : Number(v));
    const users = n(u.trial_users), days = n(u.days), requests = n(u.requests);
    const input = n(u.input), read = n(u.cache_read), write = n(u.cache_write);
    const output = n(u.output), thinking = n(u.thinking);
    if (users <= 0 || days <= 0 || requests <= 0) {
      return { error: '請填入試用人數、統計天數與請求次數' };
    }
    if (includesCache && read + write > input) {
      return { error: '快取讀取加寫入大於 Input 總量。這家的 Input 若不含快取，請取消勾選「Input 已包含快取」' };
    }
    const total = includesCache ? input : input + read + write;
    if (total <= 0) return { error: '請填入 Input tokens' };
    if (output + thinking <= 0) return { error: '請填入 Output tokens' };
    const perRequest = total / requests;
    const r4 = x => Math.floor(x * 10000 + 0.5) / 10000;
    if (perRequest > 1000000) return { error: '換算後每次 Input 超過 100 萬 tokens，請確認數字與單位' };
    const hit = Math.min(0.99, r4(read / total));
    // Rounded shares must still fit inside the prompt.
    const writeShare = Math.max(0, Math.min(r4(write / total), 1 - hit));
    return {
      input_tokens_per_request: Math.max(1, Math.round(perRequest)),
      output_tokens_per_request: Math.min(LLM_CONST.MAX_OUTPUT_TOKENS, Math.max(1, Math.round(output / requests))),
      thinking_tokens_per_request: Math.min(LLM_CONST.MAX_OUTPUT_TOKENS, Math.round(thinking / requests)),
      cache_hit_rate: hit,
      cache_write_rate: Math.min(0.99, writeShare),
      requests_per_day: requests / days,
      per_user_per_day: Math.floor(requests / days / users * 100 + 0.5) / 100,
    };
  }

  // 50 (% off) -> 五折, 20 -> 八折.
  function zhe(pct) {
    const pay = Math.floor((100 - pct) / 10 + 0.5);
    return pay > 0 && pay < 10 ? '零一二三四五六七八九'[pay] + '折' : pay + ' 折';
  }

  function renderCost(r) {
    const c = r.cost;
    const basis = document.getElementById('llm-cost-basis');
    if (basis) basis.textContent = vendorOf(r) + ' 官方牌價';
    const saving = c.cache_saving_pct > 0 ? '<span class="llm-saving">快取已省 ' + c.cache_saving_pct + '%</span>' : '';
    const item = (label, value, sub, muted) =>
      '<div class="llm-cost-item"><span class="llm-cost-label">' + label + '</span>' +
      '<span class="llm-cost-value' + (muted ? ' llm-muted' : '') + '">' + value + '</span>' +
      '<span class="llm-cost-sub">' + sub + '</span></div>';
    const monthly = c.monthly_usd != null
      ? item('預估月費', fmtUsd(c.monthly_usd), twd(c.monthly_usd) + '・' +
             Number(r.workload.monthly_requests).toLocaleString() + ' 次請求')
      : item('預估月費', '—', '填入每月總請求數即可估算', true);
    const b = c.breakdown_per_1k;
    const total = SEGMENTS.reduce((t, s) => t + (b[s[0]] || 0), 0) || 1;

    // Cache writes only appear once measured usage supplies them.
    const segs = SEGMENTS.filter(s => s[0] !== 'cache_write' || (b.cache_write || 0) > 0);
    el('llm-cost').innerHTML =
      '<div class="llm-cost-row">' +
        item('每 1,000 次請求', fmtUsd(c.per_1k_requests_usd), twd(c.per_1k_requests_usd) + '・單次 ' + fmtUsd(c.per_request_usd) + ' ' + saving) +
        monthly +
        (c.batch_discount_pct == null
          ? item('批次 API', '不支援', '此模型只能即時呼叫', true)
          : item(r.workload.batch_eligible ? '改走批次 API' : '批次 API 參考',
                 fmtUsd(c.batch_monthly_usd != null ? c.batch_monthly_usd : c.batch_per_1k_requests_usd),
                 (c.batch_monthly_usd != null ? '每月' : '每 1,000 次') + '・' + zhe(c.batch_discount_pct) +
                 '，適合不需即時回應的工作', !r.workload.batch_eligible)) +
      '</div>' +
      '<div class="llm-cost-bar">' + segs.map(s =>
        '<span class="seg seg-' + s[0] + '" style="width:' + ((b[s[0]] || 0) / total * 100).toFixed(1) +
        '%" title="' + s[1] + ' ' + fmtUsd(b[s[0]]) + '"></span>').join('') + '</div>' +
      '<div class="llm-legend">' + segs.map(s =>
        '<span class="llm-legend-item"><i class="seg-' + s[0] + '"></i>' + esc(s[1]) + ' ' +
        fmtUsd(b[s[0]]) + '</span>').join('') + '</div>' +
      (c.thinking_share_pct > 0 ? '<p class="llm-note">思考 token 佔費用 ' + c.thinking_share_pct +
        '%。思考量隨 effort 設定與題目難度變動，是費用估算中最需要實測校正的一項。</p>' : '') +
      c.caveats.map(t => '<p class="llm-note">' + esc(t) + '</p>').join('');
  }

  // -- model comparison ---------------------------------------------------

  function renderModels(r) {
    const host = el('llm-models');
    if (!host || !r.model_comparison) return;
    const selected = r.model_comparison.find(m => m.is_selected);
    const line = selected ? selected.line : null;
    const rows = compareAll ? r.model_comparison : r.model_comparison.filter(m => m.line === line);
    host.innerHTML =
      '<label class="llm-toggle" style="margin-bottom:0.6rem;"><input type="checkbox" id="llm-compare-all"' +
        (compareAll ? ' checked' : '') + '> 比較所有廠商（' + r.model_comparison.length + ' 個版本）</label>' +
      '<div class="llm-table-wrap"><table class="llm-table"><thead><tr>' +
        '<th>模型</th><th>每月費用</th><th>每千次</th><th>可用方案</th><th>最多支撐</th><th></th>' +
      '</tr></thead><tbody>' + rows.map(m =>
        '<tr class="' + (m.is_selected ? 'selected' : '') + '">' +
          '<td>' + esc(m.label) + (m.is_selected ? ' <span class="llm-custom-flag">目前</span>' : '') + '</td>' +
          '<td>' + (m.monthly_usd != null ? fmtUsd(m.monthly_usd) + '<span class="llm-cell-sub">' + twd(m.monthly_usd) + '</span>' : '—') + '</td>' +
          '<td>' + fmtUsd(m.per_1k_requests_usd) + '</td>' +
          '<td>' + m.fitting_plans + ' / ' + m.total_plans + '</td>' +
          '<td>' + (m.best_max_users != null ? m.best_max_users.toLocaleString() + ' 人' : '—') + '</td>' +
          '<td>' + (m.is_selected ? '' : '<button type="button" class="llm-row-pick" data-pick-model="' + m.model + '">改用</button>') + '</td>' +
        '</tr>').join('') + '</tbody></table></div>' +
      '<p class="llm-note">各模型以相同的 token 量比較，只反映已公布的價格與配額差異。實際 token 數會因模型而異：' +
      '不同廠商的 tokenizer 不同，思考量也不同。省錢前請先確認能力是否足夠，跨廠商比較僅供參考。</p>';
    const toggle = el('llm-compare-all');
    if (toggle) toggle.addEventListener('change', e => { compareAll = e.target.checked; renderModels(lastReport); });
    host.querySelectorAll('[data-pick-model]').forEach(b => b.addEventListener('click', () => {
      if (typeof root.llmSelectModel === 'function') root.llmSelectModel(b.dataset.pickModel);
    }));
  }

  // -- demand, cards, footer ----------------------------------------------

  function renderDemand(r) {
    const w = r.workload;
    const thinking = w.apps.reduce((t, a) => t + (a.thinking_tokens_per_request || 0), 0);
    const card = (label, value, formula) =>
      '<div class="llm-demand-card"><span class="llm-demand-label">' + label + '</span>' +
      '<span class="llm-demand-value">' + value + '</span>' +
      '<span class="llm-demand-formula">' + esc(formula) + '</span></div>';
    el('llm-demand').innerHTML =
      card('RPM / QPM', fmtTok(r.required_rpm), r.total_users.toLocaleString() + ' 人共送出的每分鐘請求數') +
      card(DIM_LABEL.itpm, fmtTok(r.required_itpm), r.cached_itpm > 0
        ? '另有 ' + fmtTok(r.cached_itpm) + ' 走快取讀取，不佔 ITPM'
        : (w.apps.length > 1 ? w.apps.length + ' 個應用加總' : '未使用 prompt caching')) +
      card(DIM_LABEL.otpm, fmtTok(r.required_otpm), thinking > 0
        ? '含思考 token，思考同樣佔用 OTPM' : '尖峰 1 分鐘生成的 token 數');
  }

  function dimVal(key, v) { return key === 'usd10m' ? fmtUsd(v) : fmtTok(v); }

  function dimRow(key, dim) {
    const name = '<span class="llm-dim-name">' + DIM_LABEL[key] + '</span>';
    const acct = dim.from_account ? '<span class="llm-acct" title="來自你填入的帳號配額">帳號值</span>'
      : (dim.soft ? '<span class="llm-acct" title="基準值，並非硬上限">基準值</span>' : '');
    if (dim.demand_known === false)
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-nums">' + (dim.limit != null ? '上限 ' + dimVal(key, dim.limit) : '') + '</span>' +
        '<span class="llm-dim-load llm-muted">需填每月請求數</span></div></div>';
    if (dim.status === 'not_enforced')
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-load llm-muted">不設限</span></div>' +
        (dim.note ? '<div class="llm-note">' + esc(dim.note) + '</div>' : '') + '</div>';
    if (dim.status === 'unpublished')
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-nums">需求 ' + dimVal(key, dim.demand) + '</span>' +
        '<span class="llm-dim-load llm-muted">未公布</span></div></div>';
    if (dim.load == null)
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-nums">需求 ' + dimVal(key, dim.demand) + '</span>' +
        '<span class="llm-dim-load" style="color:var(--danger)">額度 0</span></div>' +
        '<div class="llm-bar"><span class="over" style="width:100%"></span></div></div>';
    const cls = dim.load > 1 ? 'over' : (dim.load > 0.7 ? 'tight' : 'ample');
    const colour = cls === 'over' ? 'var(--danger)' : (cls === 'tight' ? 'var(--warning)' : 'var(--success)');
    return '<div class="llm-dim"><div class="llm-dim-top">' + name +
      '<span class="llm-dim-nums">' + dimVal(key, dim.demand) + ' / ' + dimVal(key, dim.limit) + acct + '</span>' +
      '<span class="llm-dim-load" style="color:' + colour + '">' + Math.round(dim.load * 100) + '%</span></div>' +
      '<div class="llm-bar"><span class="' + cls + '" style="width:' + Math.min(100, dim.load * 100) + '%"></span></div></div>';
  }

  function planCard(r) {
    const capacity = r.max_users != null
      ? '<div class="llm-capacity">以目前組合等比放大，此方案約可支撐 <strong>' + r.max_users.toLocaleString() +
        '</strong> 人' + (r.binding_dimension ? '<span class="llm-bind">瓶頸 ' + r.binding_dimension.toUpperCase() + '</span>' : '') + '</div>'
      : '';
    const actions = r.actions.length
      ? '<div class="llm-actions"><span class="llm-actions-title">下一步</span>' + r.actions.map(a =>
          '<div class="llm-action"><span class="llm-action-icon">' + (ACTION_ICON[a.kind] || '•') +
          '</span>' + esc(a.text) + '</div>').join('') + '</div>'
      : '';
    const price = r.list_priced ? '' :
      '<div class="llm-note">此方案費用依該平台自己的定價，與上方月費不同</div>';
    return '<div class="llm-card verdict-' + r.verdict + '">' +
      '<div class="llm-card-head"><div><span class="llm-card-name">' + esc(r.platform_label) + '</span>' +
        '<span class="llm-card-plan">' + esc(r.plan_label) + '</span></div>' +
        '<span class="llm-badge ' + r.verdict + '">' + VERDICT_LABEL[r.verdict] + '</span></div>' +
      capacity + DIMS.filter(k => r[k]).map(k => dimRow(k, r[k])).join('') + actions +
      '<div class="llm-card-notes">' + price + r.notes.map(n => '<div class="llm-note">' + esc(n) + '</div>').join('') +
      '</div></div>';
  }

  function renderCards(report) {
    let rows = report.results.slice();
    if (onlyFitting) rows = rows.filter(r => fits(r.verdict));
    if (sortBy === 'headroom') {
      rows.sort((a, b) => (VERDICT_RANK[b.verdict] - VERDICT_RANK[a.verdict]) ||
                          ((b.headroom_multiple || 0) - (a.headroom_multiple || 0)));
    }
    el('llm-cards').innerHTML = rows.length ? rows.map(planCard).join('') :
      '<p class="llm-note">目前沒有任何方案的預設配額容得下這個工作負載。取消「只看容得下的方案」即可看到各方案的調升建議。</p>';
  }

  function renderControls(report) {
    const n = report.results.filter(r => fits(r.verdict)).length;
    el('llm-controls').innerHTML =
      '<label class="llm-toggle"><input type="checkbox" id="llm-only-fitting"' + (onlyFitting ? ' checked' : '') +
        '> 只看容得下的方案 <span class="llm-count">' + n + ' / ' + report.results.length + '</span></label>' +
      '<label class="llm-toggle">排序 <select id="llm-sort">' +
        '<option value="platform"' + (sortBy === 'platform' ? ' selected' : '') + '>依平台</option>' +
        '<option value="headroom"' + (sortBy === 'headroom' ? ' selected' : '') + '>依餘裕</option>' +
      '</select></label>';
    el('llm-only-fitting').addEventListener('change', e => {
      onlyFitting = e.target.checked; renderCards(lastReport); renderControls(lastReport);
    });
    el('llm-sort').addEventListener('change', e => { sortBy = e.target.value; renderCards(lastReport); });
  }

  function renderFooter(report) {
    const seen = [];
    report.results.forEach(r => { if (!seen.some(x => x[0] === r.platform_label)) seen.push([r.platform_label, r.source]); });
    el('llm-sources').innerHTML = '官方文件：' + seen.map(x =>
      '<a href="' + esc(x[1]) + '" target="_blank" rel="noopener">' + esc(x[0]) + '</a>').join(' · ');
    el('llm-assumptions').innerHTML = '<span class="llm-assume-title">模型假設</span>' +
      report.assumptions.map(t => '<div class="llm-note">' + esc(t) + '</div>').join('');
  }

  // -- plain-text summary for proposals ------------------------------------

  function summaryText(r) {
    if (!r) return '';
    const c = r.cost;
    const fitting = r.results.filter(x => fits(x.verdict));
    const caps = platformCapacity(r).sort((a, b) => a.max_users - b.max_users);
    const lines = [
      'Claude 用量與配額試算（' + r.model_label + '）',
      '',
      '規模：' + r.total_users.toLocaleString() + ' 位使用者，尖峰每分鐘 ' + Math.round(r.required_rpm).toLocaleString() + ' 次請求',
      '結論：' + (fitting.length
        ? '預設配額即可支撐，' + fitting.length + ' / ' + r.results.length + ' 個方案可用，不必先申請調額'
        : '預設配額不足，需先申請調額'),
    ];
    if (c.monthly_usd != null) {
      lines.push('預估月費：' + fmtUsd(c.monthly_usd) + '（約 ' + twd(c.monthly_usd) + '，' +
        Number(r.workload.monthly_requests).toLocaleString() + ' 次請求，' + vendorOf(r) + ' 官方牌價）');
    }
    lines.push('每 1,000 次請求：' + fmtUsd(c.per_1k_requests_usd) +
      (c.cache_saving_pct > 0 ? '，已含快取節省 ' + c.cache_saving_pct + '%' : ''));
    if (r.workload.batch_eligible && c.batch_monthly_usd != null) {
      lines.push('若改走批次 API：月費約 ' + fmtUsd(c.batch_monthly_usd) + '（約 ' + twd(c.batch_monthly_usd) + '）');
    }
    if (caps.length) {
      lines.push('可成長到：' + caps.map(x => x.platform_label + ' ' + x.max_users.toLocaleString() + ' 人').join('、'));
    }
    const stress = (r.sensitivity || [])[0];
    if (stress) lines.push('壓力測試（尖峰再集中一倍）：' + stress.fitting_plans + ' / ' + stress.total_plans + ' 個方案仍可用');
    const selLine = ((r.model_comparison || []).find(m => m.is_selected) || {}).line;
    const cheaper = (r.model_comparison || []).filter(m => m.line === selLine && !m.is_selected && m.fitting_plans > 0 && m.monthly_usd != null)
      .filter(m => c.monthly_usd != null && m.monthly_usd < c.monthly_usd);
    if (cheaper.length) {
      lines.push('其他選擇：' + cheaper.map(m => m.label + ' ' + fmtUsd(m.monthly_usd) + '/月').join('、') + '（能力需另行評估）');
    }
    lines.push('');
    lines.push('註：部分平台另依其定價計費；token 量與尖峰集中度為規劃估計，正式報價前請以實際提示詞與用量校正。' +
      '配額資料驗證 ' + (r.results[0] ? r.results[0].verified : '') + '。');
    return lines.join('\n');
  }

  function renderLLMReport(report) {
    lastReport = report;
    renderSummary(report);
    el('llm-warnings').innerHTML = (report.warnings || []).map(t => '<p class="llm-warn">' + esc(t) + '</p>').join('');
    renderCost(report);
    renderModels(report);
    renderDemand(report);
    renderControls(report);
    renderCards(report);
    renderFooter(report);
    const results = el('llm-results');
    if (results) results.style.display = '';
  }

  const api = {
    renderLLMReport,
    llmRerender: () => { if (lastReport) renderLLMReport(lastReport); },
    llmSummaryText: r => summaryText(r || lastReport),
    llmModelFor: modelFor, llmCalibrate: calibrateFromUsage,
    llmEsc: esc, llmFmtTok: fmtTok, llmFmtUsd: fmtUsd,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  Object.assign(root, api);
})(typeof globalThis !== 'undefined' ? globalThis : this);
