// Shared renderer for an /api/llm-quota report.
//
// Both front ends hand it the same object: the static page computes it
// locally with engine.js, the FastAPI page fetches it from the API. Keeping
// one renderer means the two pages cannot drift apart visually either.
//
// Expects these element ids to exist:
//   #llm-summary #llm-demand  #llm-cost  #llm-warnings  #llm-controls
//   #llm-cards   #llm-sources  #llm-assumptions

(function (root) {
  'use strict';

  const VERDICT_LABEL = {
    ample:   '✅ 餘裕充沛',
    tight:   '⚠ 接近上限',
    over:    '⛔ 超出上限',
    blocked: '⛔ 預設為 0',
    unknown: '❓ 未公布',
  };
  const VERDICT_RANK = { over: 0, blocked: 1, unknown: 2, tight: 3, ample: 4 };
  const DIM_LABEL = { rpm: 'RPM', itpm: 'ITPM<span class="llm-dim-sub">未快取 Input</span>',
                      otpm: 'OTPM<span class="llm-dim-sub">Output</span>' };
  const ACTION_ICON = {
    request_quota: '\u{1F4C4}', switch_plan: '↕', switch_model: '\u{1F504}',
    raise_cache: '⚡', set_max_tokens: '\u{1F3AF}', enter_account_quota: '\u{1F511}',
  };

  let lastReport = null;
  let onlyFitting = false;
  let sortBy = 'platform';

  function esc(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtTok(n) {
    if (n == null || !isFinite(n)) return '—';
    // Strip trailing zeros only after a decimal point, so "20" stays "20".
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

  function el(id) { return document.getElementById(id); }

  // -- sections -----------------------------------------------------------

  function renderDemand(r) {
    const w = r.workload;
    const cacheLine = r.cached_itpm > 0
      ? '另有 ' + fmtTok(r.cached_itpm) + ' 走快取讀取，不佔 ITPM'
      : (w.apps.length > 1 ? w.apps.length + ' 個應用加總' : '未使用 prompt caching');
    el('llm-demand').innerHTML =
      card('RPM / QPM', fmtTok(r.required_rpm),
           r.total_users.toLocaleString() + ' 人共送出的每分鐘請求數') +
      card('ITPM<span class="llm-dim-sub">未快取 Input</span>', fmtTok(r.required_itpm), cacheLine) +
      card('OTPM<span class="llm-dim-sub">Output</span>', fmtTok(r.required_otpm),
           '尖峰 1 分鐘生成的 token 數');

    function card(label, value, formula) {
      return '<div class="llm-demand-card"><span class="llm-demand-label">' + label + '</span>' +
        '<span class="llm-demand-value">' + value + '</span>' +
        '<span class="llm-demand-formula">' + esc(formula) + '</span></div>';
    }
  }

  function renderCost(r) {
    const c = r.cost;
    const saving = c.cache_saving_pct > 0
      ? '<span class="llm-saving">快取已省 ' + c.cache_saving_pct + '%</span>' : '';
    const monthly = c.monthly_usd != null
      ? '<div class="llm-cost-item"><span class="llm-cost-label">預估月費</span>' +
        '<span class="llm-cost-value">' + fmtUsd(c.monthly_usd) + '</span>' +
        '<span class="llm-cost-sub">' + Number(r.workload.monthly_requests).toLocaleString() + ' 次請求</span></div>'
      : '<div class="llm-cost-item"><span class="llm-cost-label">預估月費</span>' +
        '<span class="llm-cost-value llm-muted">—</span>' +
        '<span class="llm-cost-sub">填入「每月總請求數」即可估算</span></div>';

    const b = c.breakdown_per_1k;
    const total = (b.uncached_input + b.cache_read + b.output) || 1;
    const bar = [['uncached_input', '未快取 Input'], ['cache_read', '快取讀取'], ['output', 'Output']]
      .map(([k, label]) =>
        '<span class="seg seg-' + k + '" style="width:' + (b[k] / total * 100).toFixed(1) + '%" ' +
        'title="' + label + ' ' + fmtUsd(b[k]) + '"></span>').join('');
    const legend = [['uncached_input', '未快取 Input'], ['cache_read', '快取讀取'], ['output', 'Output']]
      .map(([k, label]) => '<span class="llm-legend-item"><i class="seg-' + k + '"></i>' +
        esc(label) + ' ' + fmtUsd(b[k]) + '</span>').join('');

    el('llm-cost').innerHTML =
      '<div class="llm-cost-row">' +
        '<div class="llm-cost-item"><span class="llm-cost-label">每 1,000 次請求</span>' +
          '<span class="llm-cost-value">' + fmtUsd(c.per_1k_requests_usd) + '</span>' +
          '<span class="llm-cost-sub">單次 ' + fmtUsd(c.per_request_usd) + ' ' + saving + '</span></div>' +
        monthly +
        '<div class="llm-cost-item"><span class="llm-cost-label">若完全不用快取</span>' +
          '<span class="llm-cost-value llm-muted">' + fmtUsd(c.per_1k_requests_without_cache_usd) + '</span>' +
          '<span class="llm-cost-sub">每 1,000 次請求</span></div>' +
      '</div>' +
      '<div class="llm-cost-bar">' + bar + '</div>' +
      '<div class="llm-legend">' + legend + '</div>' +
      c.caveats.map(t => '<p class="llm-note">' + esc(t) + '</p>').join('');
  }

  function dimRow(key, dim) {
    const name = '<span class="llm-dim-name">' + DIM_LABEL[key] + '</span>';
    const acct = dim.from_account ? '<span class="llm-acct" title="來自你填入的帳號配額">帳號值</span>' : '';

    if (dim.status === 'not_enforced')
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-load llm-muted">不設限</span></div>' +
        (dim.note ? '<div class="llm-note">' + esc(dim.note) + '</div>' : '') + '</div>';
    if (dim.status === 'unpublished')
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-nums">需求 ' + fmtTok(dim.demand) + '</span>' +
        '<span class="llm-dim-load llm-muted">未公布</span></div></div>';
    if (dim.load == null)
      return '<div class="llm-dim"><div class="llm-dim-top">' + name +
        '<span class="llm-dim-nums">需求 ' + fmtTok(dim.demand) + '</span>' +
        '<span class="llm-dim-load" style="color:var(--danger)">額度 0</span></div>' +
        '<div class="llm-bar"><span class="over" style="width:100%"></span></div></div>';

    const cls = dim.load > 1 ? 'over' : (dim.load > 0.7 ? 'tight' : 'ample');
    const colour = cls === 'over' ? 'var(--danger)' : (cls === 'tight' ? 'var(--warning)' : 'var(--success)');
    return '<div class="llm-dim"><div class="llm-dim-top">' + name +
      '<span class="llm-dim-nums">' + fmtTok(dim.demand) + ' / ' + fmtTok(dim.limit) + acct + '</span>' +
      '<span class="llm-dim-load" style="color:' + colour + '">' + Math.round(dim.load * 100) + '%</span></div>' +
      '<div class="llm-bar"><span class="' + cls + '" style="width:' +
        Math.min(100, dim.load * 100) + '%"></span></div></div>';
  }

  function planCard(r, report) {
    const capacity = r.max_users != null
      ? '<div class="llm-capacity">以目前組合等比放大，此方案約可支撐 <strong>' +
        r.max_users.toLocaleString() + '</strong> 人' +
        (r.binding_dimension ? '<span class="llm-bind">瓶頸 ' + r.binding_dimension.toUpperCase() + '</span>' : '') +
        '</div>'
      : '';
    const actions = r.actions.length
      ? '<div class="llm-actions"><span class="llm-actions-title">下一步</span>' +
        r.actions.map(a => '<div class="llm-action"><span class="llm-action-icon">' +
          (ACTION_ICON[a.kind] || '•') + '</span>' + esc(a.text) + '</div>').join('') + '</div>'
      : '';
    return '<div class="llm-card verdict-' + r.verdict + '">' +
      '<div class="llm-card-head"><div><span class="llm-card-name">' + esc(r.platform_label) + '</span>' +
        '<span class="llm-card-plan">' + esc(r.plan_label) + '</span></div>' +
        '<span class="llm-badge ' + r.verdict + '">' + VERDICT_LABEL[r.verdict] + '</span></div>' +
      capacity +
      ['rpm', 'itpm', 'otpm'].map(k => dimRow(k, r[k])).join('') +
      actions +
      '<div class="llm-card-notes">' +
        r.notes.map(n => '<div class="llm-note">' + esc(n) + '</div>').join('') +
      '</div></div>';
  }

  function renderCards(report) {
    let rows = report.results.slice();
    if (onlyFitting) rows = rows.filter(r => r.verdict === 'ample' || r.verdict === 'tight');
    if (sortBy === 'headroom') {
      rows.sort((a, b) => {
        const d = VERDICT_RANK[b.verdict] - VERDICT_RANK[a.verdict];
        if (d) return d;
        return (b.headroom_multiple || 0) - (a.headroom_multiple || 0);
      });
    }
    el('llm-cards').innerHTML = rows.length
      ? rows.map(r => planCard(r, report)).join('')
      : '<p class="llm-note">目前沒有任何方案的預設配額容得下這個工作負載。' +
        '取消「只看容得下的方案」即可看到各方案的調升建議。</p>';
  }

  function renderControls(report) {
    const fitting = report.results.filter(r => r.verdict === 'ample' || r.verdict === 'tight').length;
    el('llm-controls').innerHTML =
      '<label class="llm-toggle"><input type="checkbox" id="llm-only-fitting"' +
        (onlyFitting ? ' checked' : '') + '> 只看容得下的方案 <span class="llm-count">' +
        fitting + ' / ' + report.results.length + '</span></label>' +
      '<label class="llm-toggle">排序 <select id="llm-sort">' +
        '<option value="platform"' + (sortBy === 'platform' ? ' selected' : '') + '>依平台</option>' +
        '<option value="headroom"' + (sortBy === 'headroom' ? ' selected' : '') + '>依餘裕</option>' +
      '</select></label>';

    el('llm-only-fitting').addEventListener('change', e => {
      onlyFitting = e.target.checked;
      renderCards(lastReport);
      renderControls(lastReport);
    });
    el('llm-sort').addEventListener('change', e => {
      sortBy = e.target.value;
      renderCards(lastReport);
    });
  }

  function renderFooter(report) {
    const seen = [];
    report.results.forEach(r => {
      if (!seen.some(x => x[0] === r.platform_label)) seen.push([r.platform_label, r.source]);
    });
    el('llm-sources').innerHTML = '官方文件：' +
      seen.map(x => '<a href="' + esc(x[1]) + '" target="_blank" rel="noopener">' +
        esc(x[0]) + '</a>').join(' · ');
    el('llm-assumptions').innerHTML =
      '<span class="llm-assume-title">模型假設</span>' +
      report.assumptions.map(t => '<div class="llm-note">' + esc(t) + '</div>').join('');
  }


  // The answer a salesperson actually needs, before any of the engineering
  // detail below it: can it be served, what does it cost, how far can it grow.
  function renderSummary(r) {
    const host = el('llm-summary');
    if (!host) return;

    const fitting = r.results.filter(x => x.verdict === 'ample' || x.verdict === 'tight');
    const users = r.total_users.toLocaleString();
    const cost = r.cost.monthly_usd != null
      ? fmtUsd(r.cost.monthly_usd)
      : fmtUsd(r.cost.per_1k_requests_usd) + ' / 千次';
    const costSub = r.cost.monthly_usd != null
      ? '以 ' + Number(r.workload.monthly_requests).toLocaleString() + ' 次/月估算'
      : '填入每月請求數即可換算月費';

    let headline, tone;
    if (fitting.length) {
      const caps = fitting.map(x => x.max_users).filter(v => v != null).sort((a, b) => a - b);
      const grow = caps.length
        ? (caps[0] === caps[caps.length - 1]
            ? caps[0].toLocaleString() + ' 人'
            : caps[0].toLocaleString() + '–' + caps[caps.length - 1].toLocaleString() + ' 人')
        : '—';
      const names = [];
      fitting.forEach(x => { if (names.indexOf(x.platform_label) < 0) names.push(x.platform_label); });
      tone = 'ok';
      headline = '<strong>' + users + ' 位使用者撐得住。</strong>' +
        names.join('、') + ' 的預設配額就足夠，不必先申請調額。';
      host.innerHTML = block(tone, headline, [
        ['每月費用', cost, costSub],
        ['可成長到', grow, '依選用方案而定，等比放大目前的使用組合'],
        ['可用方案', fitting.length + ' / ' + r.results.length, '其餘方案需先申請調額或未公布配額'],
      ]);
      return;
    }

    // Nothing fits on defaults — say what it would take, not just "no".
    const closest = r.results
      .filter(x => x.peak_load != null)
      .sort((a, b) => a.peak_load - b.peak_load)[0];
    const fix = closest && closest.actions.length ? closest.actions[0].text : '';
    tone = 'warn';
    headline = '<strong>預設配額不夠用。</strong>' +
      (closest ? '最接近的是 ' + esc(closest.platform_label) + ' ' + esc(closest.plan_label) +
        '，' + esc(fix) : '每個方案都需要先申請調額。') +
      ' 下方每張卡片都列出了具體的下一步。';
    host.innerHTML = block(tone, headline, [
      ['每月費用', cost, costSub],
      ['尖峰需求', fmtTok(r.required_itpm) + ' ITPM', '未快取輸入，配額最常卡住的一項'],
      ['可用方案', '0 / ' + r.results.length, '調額後即可使用，配額並非模型上限'],
    ]);

    function block(kind, text, tiles) {
      return '<div class="llm-summary ' + kind + '">' +
        '<p class="llm-summary-head">' + text + '</p>' +
        '<div class="llm-summary-tiles">' +
          tiles.map(([label, value, sub]) =>
            '<div><span class="llm-summary-label">' + esc(label) + '</span>' +
            '<span class="llm-summary-value">' + value + '</span>' +
            '<span class="llm-summary-sub">' + esc(sub) + '</span></div>').join('') +
        '</div></div>';
    }
  }

  function renderLLMReport(report) {
    lastReport = report;
    renderSummary(report);
    renderDemand(report);
    renderCost(report);
    el('llm-warnings').innerHTML =
      (report.warnings || []).map(t => '<p class="llm-warn">' + esc(t) + '</p>').join('');
    renderControls(report);
    renderCards(report);
    renderFooter(report);
    const results = el('llm-results');
    if (results) results.style.display = '';
  }

  const api = { renderLLMReport, llmEsc: esc, llmFmtTok: fmtTok, llmFmtUsd: fmtUsd };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  Object.assign(root, api);
})(typeof globalThis !== 'undefined' ? globalThis : this);
