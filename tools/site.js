/* 이미지가 없거나 받지 못했을 때 자리표시 */
(() => {
  const mark = img => { const f = img.closest('figure,.rh-media'); if (!f) return; f.classList.add('noimg'); if (!f.dataset.label) f.dataset.label = img.alt.replace(/^Wolf Tooth /, ''); };
  document.querySelectorAll('img').forEach(img => {
    if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) mark(img);
    img.addEventListener('error', () => mark(img));
  });
})();
