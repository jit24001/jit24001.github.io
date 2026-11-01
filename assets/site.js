(() => {
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open)); nav.classList.toggle('open', open);
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { nav?.classList.remove('open'); menu?.setAttribute('aria-expanded', 'false'); } });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { nav.classList.remove('open'); menu?.setAttribute('aria-expanded', 'false'); }));
  let toastTimer;
  function toast(message) { const t = document.querySelector('.toast'); t.textContent = message; t.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('visible'), 2500); }
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(button.dataset.copy); toast('Copied to clipboard'); }
    catch { const area = document.createElement('textarea'); area.value = button.dataset.copy; area.style.position = 'fixed'; area.style.opacity = '0'; document.body.append(area); area.select(); const ok = document.execCommand('copy'); area.remove(); toast(ok ? 'Copied to clipboard' : 'Please select and copy the text manually'); }
  }));
  const search = document.querySelector('#publication-search');
  if (search) {
    let year = 'all'; const rows = [...document.querySelectorAll('.pub-row')];
    const filters = [...document.querySelectorAll('[data-year-filter]')];
    const update = () => { const query = search.value.trim().toLowerCase(); let shown = 0;
      rows.forEach(row => { row.hidden = !((year === 'all' || row.dataset.year === year) && row.dataset.search.includes(query)); if (!row.hidden) shown++; });
      document.querySelector('#pub-count').textContent = `${shown} publication${shown === 1 ? '' : 's'}`;
      document.querySelector('#no-results').hidden = shown > 0;
      filters.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.yearFilter === year)));
    };
    filters.forEach(b => b.addEventListener('click', () => { year = b.dataset.yearFilter; update(); }));
    search.addEventListener('input', update);
    document.querySelector('#clear-filters').addEventListener('click', () => { year = 'all'; search.value = ''; update(); search.focus(); });
  }
  const graph = document.querySelector('#encoding-graph');
  if (graph) {
    const pairs = []; for (let j = 2; j <= 6; j++) for (let i = 1; i < j; i++) pairs.push([i, j]);
    const points = [[90,55],[250,55],[315,170],[250,285],[90,285],[25,170]];
    const example = [1,0,1,1,0,0,1,0,1,1,0,1,0,0,1]; let bits = [...example];
    const buttons = pairs.map(([i,j], index) => { const b = document.createElement('button'); b.type = 'button'; b.addEventListener('click', () => { bits[index] = 1 - bits[index]; update(); }); document.querySelector('#bit-grid').append(b); return b; });
    function update() {
      let markup = '<g>';
      pairs.forEach(([i,j],k) => { const a = points[i-1], b = points[j-1]; if (bits[k]) markup += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"/>`; buttons[k].textContent = bits[k]; buttons[k].setAttribute('aria-pressed', String(Boolean(bits[k]))); buttons[k].setAttribute('aria-label', `Edge ${i}–${j}: ${bits[k] ? 'present' : 'absent'}`); });
      markup += '</g>'; points.forEach(([x,y],i) => { markup += `<circle cx="${x}" cy="${y}" r="17"/><text x="${x}" y="${y+1}">${i+1}</text>`; });
      graph.innerHTML = markup; const total = bits.reduce((a,b) => a+b, 0); document.querySelector('.encoding-count').textContent = `6 vertices · ${total} of 15 possible edges`;
    }
    document.querySelectorAll('[data-preset]').forEach(b => b.addEventListener('click', () => { bits = b.dataset.preset === 'all' ? Array(15).fill(1) : b.dataset.preset === 'none' ? Array(15).fill(0) : [...example]; update(); })); update();
  }
})();
