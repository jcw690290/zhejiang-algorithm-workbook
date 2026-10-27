import fs from 'node:fs/promises';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import vm from 'node:vm';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
await fs.mkdir(new URL('artifacts/',import.meta.url),{recursive:true});
const html=await fs.readFile(new URL('index.html',import.meta.url),'utf8');
for(const script of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) if(!script[0].includes('application/json')) new vm.Script(script[1]);
const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html)});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await chromium.launch({headless:true,...(process.env.TEST_BROWSER_CHANNEL?{channel:process.env.TEST_BROWSER_CHANNEL}:{})});
const page=await browser.newPage({viewport:{width:1280,height:960}});
const errors=[],requests=[],checks=[];
page.on('pageerror',e=>errors.push(e.message));
let mode='ok',lastBody,held;
await page.route('https://mock.example/**',async route=>{
  requests.push(route.request());
  if(route.request().method()==='OPTIONS'){await route.fulfill({status:204,headers:{'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Authorization, Content-Type'}});return;}
  lastBody=route.request().postDataJSON();
  if(mode==='wait'){held=route;return;}
  const headers={'Access-Control-Allow-Origin':'*','Content-Type':'application/json'};
  if(mode==='401')return route.fulfill({status:401,headers,body:'secret-test-key SHOULD NOT APPEAR'});
  if(mode==='invalid')return route.fulfill({status:200,headers,body:'not JSON'});
  if(mode==='empty')return route.fulfill({status:200,headers,body:JSON.stringify({choices:[{message:{content:null}}]})});
  if(mode==='reasoning')return route.fulfill({status:200,headers,body:JSON.stringify({choices:[{message:{content:null,reasoning_content:'测试推理'},finish_reason:'length'}]})});
  if(mode==='large')return route.fulfill({status:200,headers,body:'x'.repeat(1024*1024+1)});
  if(mode==='network')return route.abort('failed');
  return route.fulfill({status:200,headers,body:JSON.stringify({choices:[{message:{content:'先看变量 i。\n<img src=x onerror="window.aiXSS=true">\n再检查循环边界。'},finish_reason:mode==='length'?'length':'stop'}]})});
});
const status=()=>page.locator('#aiStatus').textContent();
const waitStatus=async text=>page.waitForFunction(t=>document.getElementById('aiStatus').textContent.includes(t),text);
const clickSend=async text=>{await page.locator('#aiPrompt').fill(text);await page.locator('#aiSend').click()};
try{
  await page.goto(`http://127.0.0.1:${server.address().port}`);
  await page.locator('#homeAll').click();
  await page.locator('#aiButton').click();
  await page.locator('#aiProvider').selectOption('custom');
  assert.equal(requests.length,0);checks.push('无自动 API 请求');
  await page.locator('#aiSend').click();assert.match(await status(),/完整 API 地址/);
  await page.locator('#aiEndpoint').fill('http://evil.example/v1');await page.locator('#aiSend').click();assert.match(await status(),/HTTPS/);
  await page.locator('#aiEndpoint').fill('https://mock.example/v1?api_key=bad');await page.locator('#aiSend').click();assert.match(await status(),/查询参数/);
  await page.locator('#aiEndpoint').fill('https://mock.example/v1/');
  await page.locator('#aiModel').fill('mock-model');await page.locator('#aiKey').fill('secret-test-key');
  await page.locator('#aiRemember').check();checks.push('无效 URL、明文远程接口、URL 密钥阻止发送');
  await page.locator('#aiTest').click();await waitStatus('连接成功');
  assert.equal(lastBody.messages.length,1);assert.equal(lastBody.max_tokens,128);assert(!JSON.stringify(lastBody).includes('202301'));assert.equal(await page.locator('.ai-message').count(),0);
  assert(requests.at(-1).url().endsWith('/v1/chat/completions'));
  assert.equal(requests.at(-1).headers()['authorization'],'Bearer secret-test-key');checks.push('连接测试使用最小请求且不发送题目');
  await page.locator('[data-ai-prompt="variables"]').click();
  await page.locator('#aiSend').click();await waitStatus('回答完成');
  assert.equal(lastBody.stream,false);assert.equal(lastBody.model,'mock-model');assert.equal(lastBody.max_tokens,2048);
  assert.match(lastBody.messages[1].content,/202301-Q10/);assert(!lastBody.messages[1].content.includes('【参考答案】'));
  assert.equal(await page.locator('.ai-assistant img').count(),0);assert.equal(await page.evaluate(()=>window.aiXSS),undefined);checks.push('本题文字上下文、请求参数正确，模型 HTML 不执行');
  await page.locator('#aiIncludeAnswer').check();await clickSend('继续解释');await waitStatus('回答完成');
  assert.equal(lastBody.messages.length,5);assert.match(lastBody.messages[1].content,/【参考答案】/);checks.push('多轮追问及按需附带解析');
  await page.locator('[data-close="aiDialog"]').click();
  await page.locator('[data-choice="B"]').click();
  await page.locator('#askAI').click();await page.locator('[data-ai-prompt="check"]').click();await page.locator('#aiSend').click();await waitStatus('回答完成');
  assert.match(lastBody.messages[1].content,/【我的本题作答】\nB/);checks.push('选择题作答随用户选择发送');
  await page.locator('[data-close="aiDialog"]').click();await page.locator('[data-qid="202301-Q11"]').first().click();await page.locator('#askAI').click();
  assert.equal(await page.locator('.ai-message').count(),0);await clickSend('解释这题');await waitStatus('回答完成');
  assert.equal(lastBody.messages.length,3);assert.match(lastBody.messages[1].content,/202301-Q11/);assert(!lastBody.messages[1].content.includes('202301-Q10'));checks.push('切题后上下文与历史隔离');
  for(const [m,expected] of [['401','HTTP 401'],['invalid','有效 JSON'],['empty','未收到'],['large','超过 1 MB'],['network','连接失败'],['length','输出上限']]){
    mode=m;await clickSend('错误场景测试');await waitStatus(expected);
    assert(!(await status()).includes('secret-test-key'));
    assert.equal(await page.locator('#aiSend').isEnabled(),true);
  }
  checks.push('鉴权、JSON、空回复、超大响应、网络失败与截断提示');
  mode='reasoning';await page.locator('#aiTest').click();await waitStatus('连接成功');assert.match(await status(),/推理内容/);
  await clickSend('推理预算测试');await waitStatus('没有最终回答');checks.push('推理模型的小额连接测试与无最终答案提示');
  mode='wait';await clickSend('慢请求');await waitStatus('等待 AI');await page.locator('#aiStop').click();await waitStatus('已停止');assert.equal(await page.locator('#aiSend').isEnabled(),true);
  if(held){await held.abort().catch(()=>{});held=null;}
  await clickSend('关闭测试');await waitStatus('等待 AI');await page.locator('[data-close="aiDialog"]').click();await page.locator('#aiButton').click();assert.equal(await page.locator('#aiSend').isEnabled(),true);
  if(held){await held.abort().catch(()=>{});held=null;}
  checks.push('停止与关闭面板中止请求并恢复控件');
  await page.clock.install();
  await clickSend('超时测试');await waitStatus('等待 AI');await page.clock.runFor(120001);await waitStatus('超过 120 秒');assert.equal(await page.locator('#aiSend').isEnabled(),true);
  if(held){await held.abort().catch(()=>{});held=null;}
  checks.push('120 秒超时恢复控件');
  mode='ok';await page.locator('#aiClear').click();assert.equal(await page.locator('.ai-message').count(),0);
  const stored=await page.evaluate(()=>JSON.stringify({...localStorage}));assert(!stored.includes('secret-test-key'));assert(!stored.includes('先看变量'));checks.push('密钥与对话未写入本地存储');
  await page.reload();await page.locator('#aiButton').click();assert.equal(await page.locator('#aiKey').inputValue(),'');assert.equal(await page.locator('#aiModel').inputValue(),'mock-model');assert.equal(await page.locator('.ai-message').count(),0);checks.push('刷新清空密钥与对话，保留允许的设置');
  await page.locator('#aiKey').fill('secret-test-key');await page.locator('#aiLimitField').selectOption('max_completion_tokens');await page.locator('#aiTest').click();await waitStatus('连接成功');assert.equal(lastBody.max_completion_tokens,128);assert.equal(lastBody.max_tokens,undefined);checks.push('可切换输出上限参数');
  await page.locator('#aiForget').click();assert.equal(await page.locator('#aiKey').inputValue(),'');
  await page.locator('#aiRemember').uncheck();assert.equal(await page.evaluate(()=>localStorage.getItem('zj-algorithm-ai-settings-v1')),null);checks.push('清除密钥与取消记住设置');
  await page.screenshot({path:'artifacts/AI面板桌面.png',fullPage:false});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth));
  assert(await page.locator('#aiDialog').evaluate(e=>e.scrollWidth<=e.clientWidth));
  await page.screenshot({path:'artifacts/AI面板手机.png',fullPage:false});checks.push('390px 手机布局无水平溢出');
  await page.locator('[data-close="aiDialog"]').click();await page.locator('#search').fill('202301-Q15');await page.locator('#draft').fill('（1）测试草稿');await page.locator('#askAI').click();await page.locator('[data-ai-prompt="check"]').click();assert.match(await page.locator('#aiContextPreview').textContent(),/测试草稿/);checks.push('非选择题草稿可选附带');
  await page.locator('#aiSettings > summary').click();
  await page.screenshot({path:'artifacts/AI对话手机.png',fullPage:false});
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:checks.length,checks,pageErrors:errors},null,2));
  await fs.writeFile(new URL('ai-verification.json',import.meta.url),JSON.stringify({passed:checks.length,checks,pageErrors:errors},null,2));
}finally{await browser.close();server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
