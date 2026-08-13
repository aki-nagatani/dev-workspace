/**
 * 公開 LP ヘッダーを、ヒーロー上では透過、通過後はソリッドにする。
 * ページ内アンカーは scrollIntoView と scroll-margin-top で固定ヘッダー分をずらす。
 * 製品 landing_base へ載せる想定の完成版相当。
 */
function initPublicLandingHeader() {
  const header = document.querySelector(".ft-site-header--public");
  const hero = document.querySelector(".ft-lp-hero");
  if (!header || !hero) {
    return;
  }

  const update = () => {
    const threshold = Math.max(0, hero.offsetHeight - header.offsetHeight);
    header.classList.toggle("is-solid", window.scrollY >= threshold);
  };

  const scrollToHash = (id) => {
    const target = document.querySelector(id);
    if (!target) {
      return false;
    }
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    target.scrollIntoView({
      behavior: reduceMotion ? "auto" : "smooth",
      block: "start",
    });
    window.requestAnimationFrame(update);
    window.setTimeout(update, 420);
    return true;
  };

  const inPageLinks = document.querySelectorAll(
    ".ft-lp-nav__link[href^='#'], .site-brand__link[href^='#']",
  );
  inPageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const id = link.getAttribute("href");
      if (!id || id === "#" || !scrollToHash(id)) {
        return;
      }
      event.preventDefault();
      if (window.history.replaceState) {
        window.history.replaceState(null, "", id);
      }
    });
  });

  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  update();
}

initPublicLandingHeader();
