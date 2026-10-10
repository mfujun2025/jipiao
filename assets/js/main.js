/* ==========================================================================
   机票.CC — 前端交互
   包含：移动端导航 / 站内搜索 / 栏目筛选 / 表格排序 / FAQ 折叠
        / 邮件订阅 / 复制邮箱 / 轻提示
   依赖：data.js（构建时自动生成）
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------- 轻提示 ---------------- */
  var toastEl = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add('is-show');
    clearTimeout(toastEl._t);
    toastEl._t = setTimeout(function () { toastEl.classList.remove('is-show'); }, 2600);
  }

  /* ---------------- 移动端导航 ---------------- */
  function initNav() {
    var btn = $('#navToggle'), nav = $('#siteNav');
    if (!btn || !nav) return;
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $$('#siteNav a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('is-open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------------- 站内搜索 ---------------- */
  function initSearch() {
    var input = $('#searchInput'), box = $('#searchResults');
    if (!input || !box || typeof SEARCH_INDEX === 'undefined') return;

    var EMPTY = '<p class="search-empty">输入关键词试试，例如：北京、中转、行李、会员日。</p>';

    function render(list) {
      if (!list.length) {
        box.innerHTML = '<p class="search-empty">没有找到匹配内容。可以换个关键词，或直接发邮件告诉我们你想看什么：'
          + (typeof SITE !== 'undefined' ? SITE.agentEmail : '') + '</p>';
        return;
      }
      box.innerHTML = list.slice(0, 8).map(function (it) {
        return '<a class="sr-item" href="' + it.url + '">'
          + '<span class="sr-title">' + escapeHtml(it.title) + '</span>'
          + '<span class="sr-meta">' + escapeHtml(it.meta) + '</span></a>';
      }).join('');
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"]/g, function (c) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
      });
    }

    function run() {
      var q = input.value.trim().toLowerCase();
      if (!q) { box.innerHTML = EMPTY; return; }
      render(SEARCH_INDEX.filter(function (it) {
        return (it.title + ' ' + it.meta).toLowerCase().indexOf(q) > -1;
      }));
    }

    input.addEventListener('input', run);
    var form = $('#searchForm');
    if (form) form.addEventListener('submit', function (ev) { ev.preventDefault(); run(); });

    // 支持 ?q= 直接带入
    var m = location.search.match(/[?&]q=([^&]+)/);
    if (m) { input.value = decodeURIComponent(m[1].replace(/\+/g, ' ')); run(); }
  }

  /* ---------------- 栏目筛选 ---------------- */
  function initFilters() {
    var chips = $$('.chip[data-filter]');
    if (!chips.length) return;

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.classList.remove('is-active'); });
        chip.classList.add('is-active');
        var f = chip.getAttribute('data-filter');
        $$('.js-item').forEach(function (item) {
          var cat = item.getAttribute('data-cat') || '';
          item.style.display = (f === '全部' || cat === f) ? '' : 'none';
        });
      });
    });
  }

  /* ---------------- 表格排序 ---------------- */
  function initTableSort() {
    var table = $('#priceTable');
    if (!table) return;
    $$('th.sortable', table).forEach(function (th) {
      th.addEventListener('click', function () {
        var col = parseInt(th.getAttribute('data-col'), 10);
        var tbody = $('tbody', table);
        var rows = $$('tr', tbody).filter(function (r) { return r.style.display !== 'none'; });
        var dir = th._dir === 'asc' ? 'desc' : 'asc';
        th._dir = dir;

        rows.sort(function (a, b) {
          var av = num(a.children[col]), bv = num(b.children[col]);
          return dir === 'asc' ? av - bv : bv - av;
        });
        rows.forEach(function (r) { tbody.appendChild(r); });

        $$('th.sortable', table).forEach(function (t) {
          t.textContent = t.textContent.replace(/\s*[↑↓]$/, '');
        });
        th.textContent = th.textContent.replace(/\s*↕\s*$/, '') + (dir === 'asc' ? ' ↑' : ' ↓');
      });
    });

    function num(cell) {
      if (!cell) return 0;
      var raw = cell.getAttribute('data-sort') || cell.textContent;
      var v = parseFloat(String(raw).replace(/[^\d.\-+]/g, ''));
      return isNaN(v) ? 0 : v;
    }
  }

  /* ---------------- FAQ 折叠 ---------------- */
  function initFaq() {
    $$('.faq-q').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item = btn.closest('.faq-item');
        var open = item.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ---------------- 邮件订阅 ---------------- */
  function initSubscribe() {
    var form = $('#subForm'), msg = $('#subMsg');
    if (!form) return;
    var email = typeof SITE !== 'undefined' ? SITE.agentEmail : '';

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var input = $('#subEmail');
      var val = (input.value || '').trim();
      var ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);

      if (!ok) {
        if (msg) msg.textContent = '请输入有效的邮箱地址。';
        input.focus();
        return;
      }
      if (msg) msg.textContent = '已为你打开邮件客户端，请点击发送完成订阅。';

      var subject = encodeURIComponent('订阅：机票.CC 内容更新');
      var body = encodeURIComponent(
        '我想订阅机票.CC 的内容更新。\n\n订阅邮箱：' + val
        + '\n关注方向（可多选）：机票价格动态 / 航线资讯 / 出行攻略 / 航司动态 / 优惠活动\n'
      );
      window.location.href = 'mailto:' + email + '?subject=' + subject + '&body=' + body;
      toast('订阅请求已生成，请在弹出的邮件客户端中发送');
      form.reset();
    });
  }

  /* ---------------- 复制邮箱 ---------------- */
  function initCopyMail() {
    $$('#copyMail, [data-copy-mail]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var mail = btn.getAttribute('data-mail') || '';
        var done = function () { toast('邮箱已复制：' + mail); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(mail).then(done, function () { fallback(mail, done); });
        } else {
          fallback(mail, done);
        }
      });
    });

    function fallback(text, cb) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); cb(); } catch (e) { toast('复制失败，请手动选择邮箱'); }
      document.body.removeChild(ta);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initNav();
    initSearch();
    initFilters();
    initTableSort();
    initFaq();
    initSubscribe();
    initCopyMail();
  });
})();
