/* bwclient.js - SSE client for the bwserve protocol */
function wwBoot(clientId, initData) {
  var root = document.getElementById('ww-root');

  // Render initial TACO data
  initData.forEach(function(taco) {
    root.appendChild(bw.createDOM(taco));
  });

  // Initialize charts after DOM is ready
  setTimeout(function() {
    document.querySelectorAll('[data-chart-config]').forEach(function(canvas) {
      var config = JSON.parse(canvas.getAttribute('data-chart-config'));
      if (typeof Chart !== 'undefined') {
        new Chart(canvas.getContext('2d'), config);
      }
    });
  }, 0);

  // Open SSE connection
  var evtSource = new EventSource('/bw/events/' + clientId);
  evtSource.onmessage = function(event) {
    var msg = JSON.parse(event.data);
    handleMessage(msg);
  };

  function handleMessage(msg) {
    switch (msg.type) {
      case 'replace':
        var target = document.getElementById(msg.target) || document.querySelector(msg.target);
        if (target && msg.node) {
          target.innerHTML = '';
          target.appendChild(bw.createDOM(msg.node));
        }
        break;
      case 'patch':
        var el = document.getElementById(msg.target) || document.querySelector(msg.target);
        if (el) {
          if (msg.content !== undefined) el.textContent = String(msg.content);
          if (msg.attr) Object.keys(msg.attr).forEach(function(k) { el.setAttribute(k, msg.attr[k]); });
        }
        break;
      case 'append':
        var parent = document.getElementById(msg.target) || document.querySelector(msg.target);
        if (parent && msg.node) parent.appendChild(bw.createDOM(msg.node));
        break;
      case 'remove':
        var rem = document.getElementById(msg.target) || document.querySelector(msg.target);
        if (rem) rem.remove();
        break;
      case 'batch':
        if (msg.ops) msg.ops.forEach(handleMessage);
        break;
      case 'call':
        if (msg.name === 'loadStyles' && msg.args) bw.loadStyles(msg.args[0]);
        else if (msg.name === 'toggleStyles') bw.toggleStyles();
        else if (msg.name === 'redirect' && msg.args) window.location.href = msg.args[0];
        else if (msg.name === 'download' && msg.args) triggerDownload(msg.args[0], msg.args[1], msg.args[2]);
        else if (msg.name === 'log' && msg.args) console.log.apply(console, msg.args);
        break;
      case 'message':
        // Component-level message dispatch
        break;
    }
  }

  // Bind widget events
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

function postAction(clientId, payload) {
  fetch('/bw/return/action/' + clientId, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

function triggerDownload(filename, content, mime) {
  var blob = new Blob([content], { type: mime || 'application/octet-stream' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function wwToast(message, type, duration) {
  var toast = document.createElement('div');
  toast.className = 'ww-toast ww-toast-' + type;
  toast.textContent = message;
  toast.style.cssText = 'position:fixed;top:1em;right:1em;padding:0.75em 1.5em;border-radius:4px;z-index:9999;background:#333;color:#fff;';
  document.body.appendChild(toast);
  setTimeout(function() { toast.remove(); }, duration || 3000);
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
