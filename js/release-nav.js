(() => {
  const releases = [
    ["v1.0.16", "#pantheon-v1016"],
    ["v1.0.15", "#pantheon-v1015-latest"],
    ["v1.0.14", "#pantheon-v1014"],
    ["v1.0.13", "#pantheon-v1013"],
    ["v1.0.12", "#pantheon-v1012"],
    ["v1.0.10", "#pantheon-v1010"],
    ["v1.0.8", "#pantheon-v108"],
    ["v1.0.7", "#v107"],
  ];

  const installReleaseNav = () => {
    if (!/^\/release\/?$/.test(window.location.pathname)) return;

    const nav = document.querySelector(".md-sidebar--primary .md-nav");
    if (!nav) return;

    const list = nav.querySelector(":scope > .md-nav__list");
    if (!list) return;

    nav.setAttribute("aria-label", "Release versions");
    nav.classList.add("release-version-nav");
    list.innerHTML = releases.map(([label, anchor], index) => `
      <li class="md-nav__item${index === 0 ? " md-nav__item--active" : ""}"><a class="md-nav__link${index === 0 ? " md-nav__link--active" : ""}" href="${anchor}">${label}</a></li>
    `).join("");
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installReleaseNav, { once: true });
  } else {
    installReleaseNav();
  }
})();
