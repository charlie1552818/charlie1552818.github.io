(()=>{
  const toc=document.querySelector('.toc');
  if(!toc)return;
  const originalLinks=[...toc.querySelectorAll('a')];
  const summary=window.PAPER_LIBRARY_SUMMARY||{};
  const activities=Array.isArray(window.RECENT_ACTIVITY)?window.RECENT_ACTIVITY.slice(0,3):[];

  toc.innerHTML='';
  const profile=document.createElement('section');
  profile.className='sidebar-card sidebar-profile';
  profile.innerHTML='<div class="sidebar-avatar">C</div><h3>Charlie</h3><p>Automation · GDUT<br>Control · Robotics · Autonomous Systems</p><div class="sidebar-stats"><div><strong>4</strong><span>tracks</span></div><div><strong>'+Number(summary.total||0).toLocaleString()+'</strong><span>papers</span></div><div><strong>'+activities.length+'</strong><span>updates</span></div></div><div class="sidebar-actions"><a href="../papers.html">Paper Desk ↗</a><a href="../index.html#activity">Activity ↗</a></div>';
  toc.appendChild(profile);

  const tocCard=document.createElement('section');
  tocCard.className='sidebar-card toc-card';
  const links=document.createElement('div'); links.className='toc-links';
  originalLinks.forEach((a,i)=>{
    const clone=a.cloneNode(true);
    const label=clone.textContent.replace(/^\d+\s*/,'');
    clone.innerHTML='<span>'+String(i+1).padStart(2,'0')+'</span><b>'+label+'</b>';
    links.appendChild(clone);
  });
  tocCard.innerHTML='<div class="toc-card-title"><span>ON THIS PAGE</span><em>'+originalLinks.length+'</em></div>';
  tocCard.appendChild(links); toc.appendChild(tocCard);

  const lib=document.createElement('section');
  lib.className='sidebar-card sidebar-library';
  lib.innerHTML='<div class="sidebar-title"><span>RESEARCH LIBRARY</span><span>↗</span></div><div class="paper-count">'+Number(summary.total||0).toLocaleString()+'<small>PAPERS</small></div><p>Browse the categorized library, open local PDFs and keep reading notes beside the paper.</p><a href="../papers.html">Open Paper Desk</a>';
  toc.appendChild(lib);

  const recent=document.createElement('section');
  recent.className='sidebar-card sidebar-recent';
  recent.innerHTML='<div class="sidebar-title"><span>RECENT ACTIVITY</span><span>'+activities.length+'</span></div>';
  const list=document.createElement('div'); list.className='recent-list';
  for(const item of activities){
    const a=document.createElement(item.href?'a':'div'); a.className='recent-item';
    if(item.href){a.href=item.href; a.target='_blank'; a.rel='noreferrer'}
    a.innerHTML='<span>'+String(item.date||'')+' · '+String(item.category||'BUILD')+'</span><b></b>';
    a.querySelector('b').textContent=item.title||'Untitled';
    list.appendChild(a);
  }
  recent.appendChild(list); toc.appendChild(recent);

  const sectionEls=[...document.querySelectorAll('.copy section[id]')], newLinks=[...links.querySelectorAll('a')];
  const update=()=>{
    const max=Math.max(1,document.documentElement.scrollHeight-innerHeight);
    let bar=document.querySelector('.case-progress');
    if(!bar){bar=document.createElement('div');bar.className='case-progress';document.body.prepend(bar)}
    bar.style.width=(Math.max(0,Math.min(1,scrollY/max))*100)+'%';
    const probe=scrollY+Math.min(innerHeight*.34,260);
    let current=sectionEls[0]?.id;
    for(const sec of sectionEls)if(sec.offsetTop<=probe)current=sec.id;
    newLinks.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+current));
  };
  addEventListener('scroll',update,{passive:true}); addEventListener('resize',update,{passive:true}); update();
})();