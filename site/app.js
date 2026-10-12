// Shared behaviour: header/footer and Zoho snippet loading.
// Cookie consent is shown by SalesIQ's own banner (visitor tracking is on in SalesIQ).
(function () {
  const cfg = window.ZOHO_CONFIG || {};
  // Injects a pasted HTML snippet into `target`, re-creating <script> tags so they execute.
  function injectSnippet(snippet, target) {
    if (!snippet || !snippet.trim()) return false;
    const doc = new DOMParser().parseFromString(snippet, "text/html");
    const nodes = [...doc.head.childNodes, ...doc.body.childNodes];
    for (const node of nodes) {
      if (node.nodeName === "SCRIPT") {
        const s = document.createElement("script");
        for (const attr of node.attributes) s.setAttribute(attr.name, attr.value);
        s.text = node.textContent;
        target.appendChild(s);
      } else {
        target.appendChild(document.importNode(node, true));
      }
    }
    return true;
  }

  function renderChrome() {
    const page = document.body.dataset.page;
    const header = document.getElementById("site-header");
    if (header) {
      header.innerHTML = `
        <div class="wrap nav">
          <a class="brand" href="index.html"><span class="logo">LM</span> LMS-Mark Academy</a>
          <nav>
            <a href="index.html" ${page === "home" ? 'aria-current="page"' : ""}>Home</a>
            <a href="courses.html" ${page === "courses" ? 'aria-current="page"' : ""}>Courses</a>
            <a href="course-guide.html" ${page === "guide" ? 'aria-current="page"' : ""}>Course guide</a>
            <a href="privacy.html" ${page === "privacy" ? 'aria-current="page"' : ""}>Privacy</a>
            <a class="btn btn-small" href="index.html#join">Join free</a>
          </nav>
        </div>
        <div class="poc-ribbon">Demo site for a marketing POC. No real courses or payments.</div>`;
    }
    const footer = document.getElementById("site-footer");
    if (footer) {
      footer.innerHTML = `
        <div class="wrap footer-grid">
          <div><strong>LMS-Mark Academy</strong><br><span class="muted">Clinical skills, taught by practitioners.</span></div>
          <div><a href="privacy.html">Privacy &amp; consent</a></div>
        </div>`;
    }
  }

  let trackingLoaded = false;
  function loadTracking() {
    if (trackingLoaded) return;
    trackingLoaded = injectSnippet(cfg.ZMA_TRACKING_SNIPPET, document.body);
  }

  function loadChat() {
    injectSnippet(cfg.SALESIQ_WIDGET_SNIPPET, document.body);
  }

  function loadSignupForm() {
    const slot = document.getElementById("zma-form-slot");
    if (!slot) return;
    if (!injectSnippet(cfg.ZMA_SIGNUP_FORM_EMBED, slot)) {
      slot.innerHTML = `<div class="placeholder">Zoho sign-up form not connected yet.<br>
        Paste the ZMA form embed code into <code>site/zoho-config.js</code> (<code>ZMA_SIGNUP_FORM_EMBED</code>).</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderChrome();
    loadChat();
    loadTracking();
  });

  // Zoho's optin.min.js (setupSF) waits for DOMContentLoaded unless
  // readyState is already "complete". Injecting after `load` guarantees
  // "complete", so the form's submit handler actually gets bound.
  if (document.readyState === "complete") loadSignupForm();
  else window.addEventListener("load", loadSignupForm);
})();
