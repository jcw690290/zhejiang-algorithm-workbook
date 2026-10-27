import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const {marked}=require('marked');
const here=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(here,'data.json'),'utf8'));
const traces=JSON.parse(await fs.readFile(path.join(here,'traces.json'),'utf8'));
marked.setOptions({gfm:true,breaks:false});
for(const q of data.questions){
  for(const key of ['statement','original','explanation'])q[key]=marked.parse(q[key]);
  q.trace=traces[q.id]||null;
}
const template=await fs.readFile(path.join(here,'template.html'),'utf8');
const ai=await fs.readFile(path.join(here,'ai.js'),'utf8');
const aiPanel=await fs.readFile(path.join(here,'ai-panel.html'),'utf8');
const html=template.replace('/*__DATA__*/',()=>JSON.stringify(data).replaceAll('<','\\u003c')).replace('<!--__AI_PANEL__-->',()=>aiPanel).replace('/*__AI_SCRIPT__*/',()=>ai);
const out=path.join(here,'index.html');
await fs.writeFile(out,html);
console.log(JSON.stringify({output:out,bytes:Buffer.byteLength(html),questions:data.questions.length,images:Object.keys(data.images).length}));
