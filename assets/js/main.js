// Sidebar nav — scroll overflowing titles horizontally on hover
document.querySelectorAll('.nav-link, .nav-summary-link').forEach(link => {
  link.addEventListener('mouseenter', () => {
    const overflow = link.scrollWidth - link.clientWidth;
    link.style.setProperty('--_scroll', overflow > 0 ? `-${overflow}px` : '0px');
  });
});

// TOC active section highlighting via IntersectionObserver
const headings = document.querySelectorAll('.prose h2, .prose h3, .prose h4');
const tocLinks = document.querySelectorAll('#TableOfContents a');

if (headings.length && tocLinks.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          tocLinks.forEach((link) => {
            link.classList.toggle('toc-active', link.getAttribute('href') === `#${id}`);
          });
          break;
        }
      }
    },
    { rootMargin: '-20px 0px -70% 0px', threshold: 0 }
  );
  headings.forEach((h) => observer.observe(h));
}
