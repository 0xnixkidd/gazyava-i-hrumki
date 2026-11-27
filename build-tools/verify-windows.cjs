const fs = require('node:fs');
(async () => {
  const pages = await (await fetch('http://127.0.0.1:9223/json')).json();
  const ws = new WebSocket(pages.find(p => p.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.onopen=resolve; ws.onerror=reject; });
  let next=0; const pending=new Map();
  ws.onmessage=e=>{const r=JSON.parse(e.data);if(r.id){pending.get(r.id)?.(r);pending.delete(r.id);}};
  const call=(method,params={})=>new Promise(resolve=>{const id=++next;pending.set(id,resolve);ws.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{
    const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(r.result.exceptionDetails) throw Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };
  const initial=await evaluate(`(() => ({ title:document.title,three:THREE.REVISION,canvas:!!document.querySelector('canvas'),webgl:!!(document.querySelector('canvas').getContext('webgl2')||document.querySelector('canvas').getContext('webgl')),error:document.querySelector('.err')?.textContent||null,buttons:[...document.querySelectorAll('button')].map(b=>({id:b.id,text:b.textContent})) }))()`);
  console.log(JSON.stringify(initial,null,2));
  if(initial.error || !initial.webgl) throw Error('Game did not initialize');
  const shot=await call('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync('build-tools/windows-menu.png',Buffer.from(shot.result.data,'base64'));
  console.log(await evaluate(`(() => { const b=document.getElementById('go'); if(!b) return 'No go button'; b.click(); return 'Started'; })()`));
  await new Promise(r=>setTimeout(r,1500));
  const running=await evaluate(`({error:document.querySelector('.err')?.textContent||null,body:document.body.innerText.slice(0,750)})`);
  fs.writeFileSync('build-tools/windows-verification.json',JSON.stringify({initial,running},null,2));
  console.log(JSON.stringify(running,null,2));
  ws.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
