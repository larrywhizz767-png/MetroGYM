(() => {
  const BOUND_ATTR = "data-api-nav-icon-bound";
  const TOP_LEVEL_SECTION_SELECTOR = "li.md-nav__item--nested";

  const ICONS = {
    Foundations:
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-layers-3" aria-hidden="true"><path d="M12.83 2.18a2 2 0 0 0-1.66 0l-8 3.2A2 2 0 0 0 2 7.24v9.52a2 2 0 0 0 1.17 1.82l8 3.2a2 2 0 0 0 1.66 0l8-3.2A2 2 0 0 0 22 16.76V7.24a2 2 0 0 0-1.17-1.86z"/><path d="m2.3 7 9.7 3.88L21.7 7"/><path d="M12 22V10.88"/></svg>',
    Primitives:
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-component" aria-hidden="true"><path d="M15.536 11.293a1 1 0 0 0 0 1.414l2.376 2.377a1 1 0 0 0 1.414 0l2.377-2.377a1 1 0 0 0 0-1.414l-2.377-2.377a1 1 0 0 0-1.414 0z"/><path d="M2.297 11.293a1 1 0 0 0 0 1.414l2.377 2.377a1 1 0 0 0 1.414 0l2.377-2.377a1 1 0 0 0 0-1.414L6.088 8.916a1 1 0 0 0-1.414 0z"/><path d="M8.916 17.912a1 1 0 0 0 0 1.415l2.377 2.376a1 1 0 0 0 1.414 0l2.377-2.376a1 1 0 0 0 0-1.415l-2.377-2.376a1 1 0 0 0-1.414 0z"/><path d="M8.916 4.674a1 1 0 0 0 0 1.414l2.377 2.376a1 1 0 0 0 1.414 0l2.377-2.376a1 1 0 0 0 0-1.414l-2.377-2.377a1 1 0 0 0-1.414 0z"/></svg>',
    Solvers:
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain-circuit" aria-hidden="true"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M9 13a4.5 4.5 0 0 0 3-4M6.003 5.125A3 3 0 0 0 6.401 6.5M3.477 10.896a4 4 0 0 1 .585-.396M6 18a4 4 0 0 1-1.967-.516M12 13h4M12 18h6a2 2 0 0 1 2 2v1M12 8h8M16 8V5a2 2 0 0 1 2-2"/><circle cx="16" cy="13" r=".5"/><circle cx="18" cy="3" r=".5"/><circle cx="20" cy="21" r=".5"/><circle cx="20" cy="8" r=".5"/></svg>',
    Rendering:
      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-monitor-play" aria-hidden="true"><path d="M10 7.75 15 11l-5 3.25Z"/><rect width="20" height="14" x="2" y="3" rx="2"/><path d="M12 17v4"/><path d="M8 21h8"/></svg>',
  };

  function addIcon(labelText, container) {
    if (!container || container.getAttribute(BOUND_ATTR) === "true") return;
    const iconMarkup = ICONS[labelText];
    if (!iconMarkup) return;

    container.setAttribute(BOUND_ATTR, "true");
    container.style.display = "inline-flex";
    container.style.alignItems = "center";
    container.style.gap = "0.7rem";

    container.insertAdjacentHTML("afterbegin", iconMarkup);
  }

  function initApiNavIcons(root = document) {
    root.querySelectorAll(TOP_LEVEL_SECTION_SELECTOR).forEach((section) => {
      const sectionLabel = section.querySelector(":scope > label.md-nav__link > .md-ellipsis");
      const sectionText = sectionLabel?.textContent.replace(/\s+/g, " ").trim();

      if (sectionText !== "API") return;

      section
        .querySelectorAll("nav label.md-nav__link > .md-ellipsis")
        .forEach((label) => {
          const text = label.textContent.replace(/\s+/g, " ").trim();
          if (!ICONS[text]) return;

          const container = label.parentElement;
          if (!(container instanceof HTMLElement)) return;

          addIcon(text, container);
        });
    });
  }

  if (
    typeof window.document$ !== "undefined" &&
    typeof window.document$.subscribe === "function"
  ) {
    window.document$.subscribe(() => initApiNavIcons(document));
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initApiNavIcons(document));
  } else {
    initApiNavIcons(document);
  }
})();
