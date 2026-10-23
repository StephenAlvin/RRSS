// Sticky header and sticky horizontal scrollbar for tables (styles in stylesheets/extra.css).
//
// Material wraps every table in a .md-typeset__scrollwrap that scrolls sideways. That puts the scrollbar under
// the last row, thousands of pixels down the page on a long table, and it stops position: sticky from working
// on the header row. This script wraps each of those in a .table-scroll box and adds a second scrollbar right
// after it. The CSS pins that scrollbar to the bottom of the window while the table is on screen, and moves the
// header row along with the page using a scroll-driven animation. The script sizes the scrollbar, keeps it in
// sync with the table, and measures where the header starts and how far it can travel.
(function () {
  // Element -> scrollLeft that our own write left it at, so the scroll event that write fires is not
  // copied back (copying it back makes the two fight during momentum scrolling).
  var echoes = new WeakMap();

  function setScrollLeft(el, x) {
    var before = el.scrollLeft;
    if (Math.abs(before - x) < 1) return;
    el.scrollLeft = x;
    if (el.scrollLeft !== before) echoes.set(el, el.scrollLeft);
  }

  function follow(from, to) {
    from.addEventListener("scroll", function () {
      var echo = echoes.get(from);
      echoes.delete(from);
      if (echo !== undefined && Math.abs(from.scrollLeft - echo) < 1) return;
      setScrollLeft(to, from.scrollLeft);
    }, { passive: true });
  }

  function update(box) {
    var wrap = box.firstElementChild;
    var bar = box.lastElementChild;
    var table = wrap.querySelector("table");
    if (table && table.tHead && table.tBodies[0]) {
      // The header starts following the page once it reaches the top, and stops at the last row.
      var top = table.tHead.getBoundingClientRect().top - box.getBoundingClientRect().top + "px";
      var travel = table.tBodies[0].getBoundingClientRect().height + "px";
      if (box.style.getPropertyValue("--table-head-top") !== top || box.style.getPropertyValue("--table-travel") !== travel) {
        box.style.setProperty("--table-head-top", top);
        box.style.setProperty("--table-travel", travel);
        // Chrome does not always hand new animation-range values to a header animation that is already
        // running, so restart it. Its position comes from the scroll offset, so nothing jumps.
        box.classList.add("table-scroll--restart");
        void box.offsetWidth;
        box.classList.remove("table-scroll--restart");
      }
    }
    var hidden = wrap.scrollWidth - wrap.clientWidth;
    box.classList.toggle("table-scroll--wide", hidden > 1);
    if (hidden <= 1) return;
    // Same scroll range as the table, so both scroll by the same number of pixels.
    bar.firstElementChild.style.width = bar.clientWidth + hidden + "px";
    setScrollLeft(bar, wrap.scrollLeft);
  }

  // Fires when a table is first laid out and whenever its size or the column width changes
  // (window resize, filtering, images loading, a collapsed section opening).
  var observer = new ResizeObserver(function (entries) {
    var boxes = new Set();
    entries.forEach(function (entry) {
      var box = entry.target.closest(".table-scroll");
      if (box) boxes.add(box);
    });
    boxes.forEach(update);
  });

  function setup(wrap) {
    if (!wrap.parentElement.classList.contains("table-scroll")) {
      var box = document.createElement("div");
      box.className = "table-scroll";
      var bar = document.createElement("div");
      bar.className = "table-scrollbar";
      bar.setAttribute("aria-hidden", "true");
      bar.tabIndex = -1;
      bar.appendChild(document.createElement("div"));
      wrap.parentNode.insertBefore(box, wrap);
      box.appendChild(wrap);
      box.appendChild(bar);
      follow(wrap, bar);
      follow(bar, wrap);
    }
    observer.observe(wrap);
    if (wrap.firstElementChild) observer.observe(wrap.firstElementChild);
  }

  // Runs on the first load and after every instant-navigation page change.
  document$.subscribe(function () {
    observer.disconnect();
    document.querySelectorAll(".md-content .md-typeset__scrollwrap").forEach(setup);
  });
})();
