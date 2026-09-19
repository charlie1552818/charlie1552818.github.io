(()=>{
  const summary=window.PAPER_LIBRARY_SUMMARY||{};
  document.querySelectorAll('[data-paper-total]').forEach(el=>el.textContent=Number(summary.total||0).toLocaleString());

  const activities=Array.isArray(window.RECENT_ACTIVITY)?window.RECENT_ACTIVITY.slice(0,4):[];
  const count=document.getElementById('rail-activity-count');
  const recentCount=document.getElementById('rail-recent-count');
  const recentList=document.getElementById('rail-recent-list');
  if(count)count.textContent=activities.length;
  if(recentCount)recentCount.textContent=activities.length;
  if(recentList){
    recentList.innerHTML='';
    activities.forEach(item=>{
      const el=document.createElement(item.href?'a':'div');
      el.className='rail-recent-item';
      if(item.href){el.href=item.href;el.target='_blank';el.rel='noreferrer'}
      const meta=document.createElement('span');
      meta.textContent=(item.date||'')+' · '+(item.category||'BUILD');
      const title=document.createElement('b');
      title.textContent=item.title||'Untitled';
      el.append(meta,title);
      recentList.appendChild(el);
    });
  }

  const links=[...document.querySelectorAll('[data-rail-target]')];
  const sections=links.map(a=>document.getElementById(a.dataset.railTarget)).filter(Boolean);
  const bar=document.getElementById('rail-progress'),pct=document.getElementById('rail-percent');
  const update=()=>{
    const max=Math.max(1,document.documentElement.scrollHeight-innerHeight),progress=Math.max(0,Math.min(1,scrollY/max));
    if(bar)bar.style.width=(progress*100).toFixed(1)+'%';
    if(pct)pct.textContent=String(Math.round(progress*100)).padStart(2,'0')+'%';
    const probe=scrollY+Math.min(innerHeight*.34,310);
    let current=sections[0]?.id;
    for(const sec of sections)if(sec.offsetTop<=probe)current=sec.id;
    links.forEach(a=>{
      const active=a.dataset.railTarget===current;
      a.classList.toggle('active',active);
      if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');
    });
  };
  addEventListener('scroll',update,{passive:true});addEventListener('resize',update,{passive:true});update();

  const backdrop=document.querySelector('.side-backdrop');
  const toggles=[...document.querySelectorAll('[data-drawer-toggle]')];
  const panels=[...document.querySelectorAll('.side-panel')];
  const closeAll=()=>{
    panels.forEach(p=>p.classList.remove('drawer-open'));
    toggles.forEach(b=>b.setAttribute('aria-expanded','false'));
    document.body.classList.remove('drawer-active');
  };
  toggles.forEach(btn=>btn.addEventListener('click',()=>{
    const panel=document.getElementById(btn.dataset.drawerToggle);
    const open=panel?.classList.contains('drawer-open');
    closeAll();
    if(panel&&!open){
      panel.classList.add('drawer-open');
      btn.setAttribute('aria-expanded','true');
      document.body.classList.add('drawer-active');
    }
  }));
  backdrop?.addEventListener('click',closeAll);
  links.forEach(a=>a.addEventListener('click',()=>{if(innerWidth<=1180)closeAll()}));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeAll()});
})();