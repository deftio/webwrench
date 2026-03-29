/* webwrench docs — shared navigation + utilities */

(function () {
  "use strict";

  /* ---- Dark mode toggle ---- */
  var stored = localStorage.getItem("ww-theme");
  if (stored === "dark" || (!stored && matchMedia("(prefers-color-scheme:dark)").matches)) {
    document.documentElement.setAttribute("data-theme", "dark");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.querySelector(".theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var isDark = document.documentElement.getAttribute("data-theme") === "dark";
        document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
        localStorage.setItem("ww-theme", isDark ? "light" : "dark");
        toggle.textContent = isDark ? "Dark" : "Light";
      });
      var current = document.documentElement.getAttribute("data-theme");
      toggle.textContent = current === "dark" ? "Light" : "Dark";
    }

    /* ---- Hamburger menu ---- */
    var hamburger = document.querySelector(".hamburger");
    var sidebar = document.querySelector(".sidebar");
    if (hamburger && sidebar) {
      hamburger.addEventListener("click", function () {
        sidebar.classList.toggle("open");
      });
      document.addEventListener("click", function (e) {
        if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== hamburger) {
          sidebar.classList.remove("open");
        }
      });
    }

    /* ---- Active sidebar link ---- */
    var path = location.pathname.replace(/\/$/, "").split("/").pop() || "index.html";
    var links = document.querySelectorAll(".sidebar a");
    for (var i = 0; i < links.length; i++) {
      var href = links[i].getAttribute("href").replace(/^\.\//, "").replace(/^\.\.\//, "");
      if (href === path || href.endsWith("/" + path)) {
        links[i].classList.add("active");
      }
    }

    /* ---- Copy buttons on code blocks ---- */
    var pres = document.querySelectorAll("pre");
    for (var j = 0; j < pres.length; j++) {
      var btn = document.createElement("button");
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.addEventListener("click", (function (block) {
        return function () {
          var code = block.querySelector("code");
          var text = code ? code.textContent : block.textContent;
          navigator.clipboard.writeText(text).then(function () {
            btn.textContent = "Copied!";
            setTimeout(function () { btn.textContent = "Copy"; }, 1500);
          });
        };
      })(pres[j]));
      pres[j].appendChild(btn);
    }
  });
})();
