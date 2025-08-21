// Generic table sorting (first click desc, second asc) for tables with class 'sortable-table'.
(function(){
  function getCellValue(row, index){
    const cell = row.children[index];
    if(!cell) return '';
    let txt = cell.textContent.trim();
    return txt;
  }
  function parseValue(val, type){
    if(type === 'number'){
      const num = parseFloat((val || '').replace(/[^0-9+\-\.]/g,'').replace(/\.+/,'$&'));
      return isNaN(num) ? -Infinity : num;
    }
    return (val || '').toLowerCase();
  }
  function clearIndicators(ths){
    ths.forEach(th => { th.dataset.sortDirection=''; th.classList.remove('sorted-asc','sorted-desc'); const base=th.dataset.baseText; if(base) th.textContent=base; });
  }
  function applyIndicator(th, dir){
    th.classList.remove('sorted-asc','sorted-desc');
    th.classList.add(dir==='asc'?'sorted-asc':'sorted-desc');
    const base = th.dataset.baseText || th.textContent.replace(/[▲▼]\s*$/,'');
    th.dataset.baseText = base;
    th.textContent = base + (dir==='asc'?' ▲':' ▼');
  }
  function init(){
    document.querySelectorAll('table.sortable-table').forEach(table => {
      const ths = Array.from(table.querySelectorAll('thead th'));
      ths.forEach((th, idx) => {
        if(th.dataset.sortable === 'false') return;
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
          const type = th.dataset.type || 'text';
          let dir = th.dataset.sortDirection === 'desc' ? 'asc' : 'desc';
          clearIndicators(ths);
          th.dataset.sortDirection = dir;
          applyIndicator(th, dir);
          const tbody = table.querySelector('tbody');
          if(!tbody) return;
          const rows = Array.from(tbody.querySelectorAll('tr'));
          rows.sort((a,b)=>{
            const va = parseValue(getCellValue(a, idx), type);
            const vb = parseValue(getCellValue(b, idx), type);
            if(va < vb) return dir==='asc' ? -1 : 1;
            if(va > vb) return dir==='asc' ? 1 : -1;
            return 0;
          });
          const frag = document.createDocumentFragment();
          rows.forEach(r=>frag.appendChild(r));
          tbody.appendChild(frag);
        });
      });
    });
  }
  if(document.readyState !== 'loading') init(); else document.addEventListener('DOMContentLoaded', init);
})();
(function(){
  const css = `.sorted-asc, .sorted-desc{position:relative;}`;
  const style = document.createElement('style');
  style.textContent = css; document.head.appendChild(style);
})();
