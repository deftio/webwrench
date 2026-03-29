/* bwclient.js - SSE client for the bwserve protocol */

/* ── Section 1: Global helper functions ── */

function triggerDownload(filename, content, mime) {
  var blob = new Blob([content], { type: mime || 'application/octet-stream' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function wwToast(message, type, duration) {
  var ms = duration || 3000;
  var toast = document.createElement('div');
  toast.className = 'ww-toast ww-toast-' + (type || 'info');
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(function() {
    toast.classList.add('ww-toast-fading');
    setTimeout(function() { toast.remove(); }, 300);
  }, ms);
}

function wwScreenshot(filename, selector) {
  if (typeof html2canvas === 'undefined') return;
  var target = selector ? document.querySelector(selector) : document.body;
  html2canvas(target).then(function(canvas) {
    var a = document.createElement('a');
    a.download = filename;
    a.href = canvas.toDataURL('image/png');
    a.click();
  });
}

function wwExportPDF(filename) {
  window.print();
}

/* ── Section 2: Register helpers into bw._clientFunctions ── */

(function() {
  if (typeof bw === 'undefined' || !bw._clientFunctions) return;
  bw._clientFunctions.loadStyles = function(palette) { bw.loadStyles(palette); };
  bw._clientFunctions.toggleStyles = function() { bw.toggleStyles(); };
  bw._clientFunctions.redirect = function(url) { window.location.href = url; };
  bw._clientFunctions.download = function(filename, content, mime) { triggerDownload(filename, content, mime); };
  bw._clientFunctions.log = function() { console.log.apply(console, arguments); };
  bw._clientFunctions.wwToast = function(message, type, duration) { wwToast(message, type, duration); };
  bw._clientFunctions.wwScreenshot = function(filename, selector) { wwScreenshot(filename, selector); };
  bw._clientFunctions.wwExportPDF = function(filename) { wwExportPDF(filename); };
})();

/* ── Section 3: applyMessage — patch adapter + batch recursion + bw.apply delegate ── */

function applyMessage(msg) {
  if (msg.type === 'patch' && msg.attr && typeof msg.attr === 'object' && !Array.isArray(msg.attr)) {
    // Server sends attr as a dict; bw.patch() expects a single attr name string.
    // Expand dict into per-attribute bw.patch() calls.
    var el = bw._el(msg.target);
    if (el) {
      if (msg.content !== undefined) {
        bw.patch(msg.target, msg.content);
      }
      var keys = Object.keys(msg.attr);
      for (var i = 0; i < keys.length; i++) {
        bw.patch(msg.target, msg.attr[keys[i]], keys[i]);
      }
    }
  } else if (msg.type === 'batch' && msg.ops) {
    // Recurse through applyMessage so nested patches get the dict adapter too
    for (var j = 0; j < msg.ops.length; j++) {
      applyMessage(msg.ops[j]);
    }
  } else {
    // All other message types: delegate directly to bitwrench
    bw.apply(msg);
  }
}

/* ── Section 4: Chart initialization via MutationObserver ── */

function initCharts(root) {
  if (typeof Chart === 'undefined') return;
  var canvases = root.querySelectorAll('[data-chart-config]');
  canvases.forEach(function(canvas) {
    if (canvas._wwChartInit) return;
    try {
      var config = JSON.parse(canvas.getAttribute('data-chart-config'));
      new Chart(canvas.getContext('2d'), config);
      canvas._wwChartInit = true;
    } catch (e) {
      // skip malformed configs
    }
  });
}

function observeCharts(root) {
  // Initial scan
  initCharts(root);
  // Watch for new chart canvases added to the DOM
  if (typeof MutationObserver !== 'undefined') {
    var observer = new MutationObserver(function(mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var added = mutations[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          if (added[j].nodeType === 1) {
            initCharts(added[j].parentElement || root);
          }
        }
      }
    });
    observer.observe(root, { childList: true, subtree: true });
  }
}

/* ── Section 4a2: Markdown rendering via quikdown ── */

function initMarkdown(root) {
  if (typeof quikdown === 'undefined') return;
  var els = root.querySelectorAll('.ww-markdown[data-md]');
  els.forEach(function(el) {
    if (el._wwMdInit) return;
    var md = el.getAttribute('data-md');
    el.innerHTML = quikdown(md, {inline_styles: true});
    el._wwMdInit = true;
  });
}

function observeMarkdown(root) {
  initMarkdown(root);
  if (typeof MutationObserver !== 'undefined') {
    var observer = new MutationObserver(function(mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var added = mutations[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          if (added[j].nodeType === 1) {
            initMarkdown(added[j].parentElement || root);
          }
        }
      }
    });
    observer.observe(root, { childList: true, subtree: true });
  }
}

/* ── Section 4b: Table initialization via bw.makeTable() ── */

function initTables(root) {
  if (typeof bw === 'undefined' || !bw.makeTable) return;
  var containers = root.querySelectorAll('.ww-table[data-config]');
  containers.forEach(function(container) {
    if (container._wwTableInit) return;
    try {
      var config = JSON.parse(container.getAttribute('data-config'));
      if (!config.sortable && !config.searchable && !config.paginate) return;
      // Convert headers+rows to bw.makeTable format
      var data = config.rows.map(function(row) {
        var obj = {};
        config.headers.forEach(function(h, i) { obj[h] = row[i]; });
        return obj;
      });
      var tableConfig = {
        data: data,
        sortable: !!config.sortable,
        hover: true,
        striped: true
      };
      if (config.paginate) {
        tableConfig.pageSize = config.paginate;
      }
      var taco = bw.makeTable(tableConfig);
      var newEl = bw.createDOM(taco);
      container.innerHTML = '';
      container.appendChild(newEl);
      container._wwTableInit = true;
    } catch (e) {
      // skip malformed configs
    }
  });
}

function observeTables(root) {
  initTables(root);
  if (typeof MutationObserver !== 'undefined') {
    var observer = new MutationObserver(function(mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var added = mutations[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          if (added[j].nodeType === 1) {
            initTables(added[j].parentElement || root);
          }
        }
      }
    });
    observer.observe(root, { childList: true, subtree: true });
  }
}

/* ── Section 5: SSE connection with exponential backoff ── */

function connectSSE(clientId) {
  var retryDelay = 1000;
  var maxDelay = 30000;

  function connect() {
    var evtSource = new EventSource('/bw/events/' + clientId);

    evtSource.onmessage = function(event) {
      var msg = JSON.parse(event.data);
      applyMessage(msg);
    };

    evtSource.onopen = function() {
      retryDelay = 1000;  // Reset on successful connection
    };

    evtSource.onerror = function() {
      evtSource.close();
      setTimeout(function() {
        retryDelay = Math.min(retryDelay * 2, maxDelay);
        connect();
      }, retryDelay);
    };
  }

  connect();
}

/* ── Section 6: Widget event delegation ── */

function bindWidgetEvents(root, clientId) {
  root.addEventListener('click', function(e) {
    var btn = e.target.closest('.ww-button');
    if (btn) {
      postAction(clientId, { widget_id: btn.id, action: 'click' });
    }
  });

  root.addEventListener('change', function(e) {
    var el = e.target;
    var group = el.closest('[id^="ww-"]');
    if (group) {
      var value = el.type === 'checkbox' ? el.checked : el.value;
      if (el.type === 'range' || el.type === 'number') value = Number(value);
      postAction(clientId, { widget_id: group.id, action: 'change', value: value });
    }
  });

  root.addEventListener('input', function(e) {
    if (e.target.type === 'range') {
      var display = e.target.parentElement.querySelector('.ww-slider-value');
      if (display) display.textContent = e.target.value;
    }
  });
}

/* ── Section 7: POST action sender ── */

function postAction(clientId, payload) {
  fetch('/bw/return/action/' + clientId, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

/* ── Section 8: Boot ── */

function wwBoot(clientId, initData, palette) {
  var root = document.getElementById('ww-root');

  // Inject bitwrench structural CSS + themed styles via JS
  if (typeof bw !== 'undefined' && bw.loadStyles) {
    bw.loadStyles(palette || {});
  }

  // Render initial TACO data using bitwrench's DOM mount
  bw.DOM(root, initData);

  // Markdown rendering via quikdown
  observeMarkdown(root);

  // Chart initialization with MutationObserver
  observeCharts(root);

  // Table initialization (sortable/paginated via bw.makeTable)
  observeTables(root);

  // Open SSE with reconnection
  connectSSE(clientId);

  // Bind widget interactions
  bindWidgetEvents(root, clientId);
}
