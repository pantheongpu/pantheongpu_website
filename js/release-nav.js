(() => {
  // Match a release version in a heading, e.g. "Pantheon v1.0.18 (Latest)".
  const VERSION_PATTERN = /v\d+\.\d+(?:\.\d+)?/i;

  const installReleaseNav = () => {
    if (!/^\/release\/?$/.test(window.location.pathname)) return;

    const nav = document.querySelector(".md-sidebar--primary .md-nav");
    if (!nav) return;

    const list = nav.querySelector(":scope > .md-nav__list");
    if (!list) return;

    // Derive the version list from the page's own release headings. A
    // hardcoded list silently goes stale with every release: it kept
    // advertising v1.0.16 as current, omitted newer releases, and linked to
    // anchors that no longer existed once a different release became latest.
    const releases = Array.from(document.querySelectorAll(".md-typeset h2[id]"))
      .map((heading) => {
        const match = (heading.textContent || "").match(VERSION_PATTERN);
        return match ? { label: match[0], anchor: `#${heading.id}` } : null;
      })
      .filter(Boolean);

    if (!releases.length) return;

    nav.setAttribute("aria-label", "Release versions");
    nav.classList.add("release-version-nav");
    list.innerHTML = releases
      .map(({ label, anchor }, index) => {
        const active = index === 0 ? " md-nav__item--active" : "";
        const activeLink = index === 0 ? " md-nav__link--active" : "";
        return `<li class="md-nav__item${active}"><a class="md-nav__link${activeLink}" href="${anchor}">${label}</a></li>`;
      })
      .join("");
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installReleaseNav, { once: true });
  } else {
    installReleaseNav();
  }
})();
