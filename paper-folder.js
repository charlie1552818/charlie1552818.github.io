(()=>{
  const connect=document.getElementById('connect-folder');
  const status=document.getElementById('connection-status');
  window.PAPER_LOCAL_FILES=new Map();
  if(!connect||!status)return;

  const hex=buf=>[...new Uint8Array(buf)].map(b=>b.toString(16).padStart(2,'0')).join('');
  const stableId=async rel=>(hex(await crypto.subtle.digest('SHA-1',new TextEncoder().encode(rel)))).slice(0,16);

  const openDb=()=>new Promise((resolve,reject)=>{
    const req=indexedDB.open('charlie-paper-desk',1);
    req.onupgradeneeded=()=>req.result.createObjectStore('handles');
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error);
  });
  const putHandle=async handle=>{
    const db=await openDb();
    await new Promise((resolve,reject)=>{
      const tx=db.transaction('handles','readwrite');
      tx.objectStore('handles').put(handle,'research-root');
      tx.oncomplete=resolve; tx.onerror=()=>reject(tx.error);
    });
    db.close();
  };
  const getHandle=async()=>{
    try{
      const db=await openDb();
      const value=await new Promise((resolve,reject)=>{
        const tx=db.transaction('handles','readonly');
        const req=tx.objectStore('handles').get('research-root');
        req.onsuccess=()=>resolve(req.result); req.onerror=()=>reject(req.error);
      });
      db.close(); return value||null;
    }catch{return null}
  };

  async function walk(dir,prefix=''){
    for await(const [name,handle] of dir.entries()){
      const rel=prefix?prefix+'/'+name:name;
      if(handle.kind==='directory'){
        await walk(handle,rel);
      }else if(name.toLowerCase().endsWith('.pdf')){
        window.PAPER_LOCAL_FILES.set(await stableId(rel),handle);
      }
    }
  }

  async function attach(handle,{request=false}={}){
    let permission='granted';
    if(handle.queryPermission) permission=await handle.queryPermission({mode:'read'});
    if(permission!=='granted'&&request&&handle.requestPermission) permission=await handle.requestPermission({mode:'read'});
    if(permission!=='granted'){
      status.textContent='Saved folder found · permission required';
      connect.textContent='Reconnect research folder';
      return false;
    }
    connect.disabled=true;
    status.textContent='Indexing local PDFs…';
    window.PAPER_LOCAL_FILES.clear();
    try{
      await walk(handle);
      status.textContent='Connected · '+window.PAPER_LOCAL_FILES.size.toLocaleString()+' PDFs matched locally';
      connect.textContent='Reconnect research folder';
      dispatchEvent(new CustomEvent('paper-folder-indexed'));
      return true;
    }catch(err){
      status.textContent='Folder indexing failed · reconnect';
      return false;
    }finally{
      connect.disabled=false;
    }
  }

  if(!window.showDirectoryPicker){
    connect.disabled=true;
    connect.textContent='Folder connection unavailable';
    status.textContent='Use Open local PDF for individual files';
    return;
  }

  connect.addEventListener('click',async()=>{
    try{
      const handle=await window.showDirectoryPicker({mode:'read'});
      await putHandle(handle);
      await attach(handle,{request:true});
    }catch(err){
      if(err?.name!=='AbortError')status.textContent='Connection cancelled or unavailable';
    }
  });

  (async()=>{
    const saved=await getHandle();
    if(saved)await attach(saved,{request:false});
  })();
})();