from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace('<title>9/4–9/5 親友幫抽抽｜FUNBOX</title>', '<title>本週親友幫抽抽｜FUNBOX</title>')
s = s.replace('<h1>9/4–9/5｜親友幫抽抽2</h1>', '<h1 id="pageTitle">本週｜親友幫抽抽2</h1>')
s = s.replace('抽選期間為 <strong>9/4–9/5</strong>', '抽選期間為 <strong id="waveLabel">讀取最新抽選中…</strong>')

s = s.replace("  const STORAGE_KEY = 'aping_beyblade_20260904_0905_visited';", "  let STORAGE_KEY = 'aping_beyblade_visited';")
s = s.replace("  const WAVE_DATES = ['2026/09/04','2026/09/05'];", "  let WAVE_DATES = [];")
s = s.replace("  function isExcluded(product){ return EXCLUDE_CODE.test(product) || EXCLUDE_WORDS.test(product) || /BX-00\\s*暴風天馬3-70RA/i.test(product); }", "  function isExcluded(product){ return EXCLUDE_CODE.test(product) || EXCLUDE_WORDS.test(product); }")
s = s.replace("    const m=s.match(/(2026)\\/(\\d{2})\\/(\\d{2})(?:\\s+(\\d{1,2}):(\\d{2}))?/);", "    const m=s.match(/(\\d{4})\\/(\\d{2})\\/(\\d{2})(?:\\s+(\\d{1,2}):(\\d{2}))?/);")

old_timing = '''  function timing(text){
    const now=new Date();
    const startMatch=text.match(/2026\\/09\\/04\\s+(\\d{1,2}):(\\d{2})/);
    const endMatch=text.match(/~\\s*(2026\\/09\\/0[45]\\s+\\d{1,2}:\\d{2})/);
    const start=startMatch?new Date(2026,8,4,+startMatch[1],+startMatch[2]):null;
    const end=endMatch?parseDateTime(endMatch[1]):null;
    if(end && now>end) return {label:'已截止', cls:'closed', disabled:true};
    if(start && now<start) return {label:`${pad(start.getHours())}:${pad(start.getMinutes())} 開抽`, cls:'future', disabled:true};
    if(start && now>=start) return {label:'現在可抽', cls:'live', disabled:false};
    return {label:'抽選連結已公布', cls:'', disabled:false};
  }'''

new_timing = '''  function timing(text){
    const now=new Date();
    const start=parseDateTime(text);
    const endMatch=text.match(/~\\s*(\\d{4}\\/\\d{2}\\/\\d{2}\\s+\\d{1,2}:\\d{2})/);
    const end=endMatch?parseDateTime(endMatch[1]):null;
    if(end && now>end) return {label:'已截止', cls:'closed', disabled:true};
    if(start && now<start) return {label:`${pad(start.getHours())}:${pad(start.getMinutes())} 開抽`, cls:'future', disabled:true};
    if(start && now>=start) return {label:'現在可抽', cls:'live', disabled:false};
    return {label:'抽選連結已公布', cls:'', disabled:false};
  }'''

if old_timing in s:
    s = s.replace(old_timing, new_timing, 1)

marker = "  function extract(html){\n    const doc=new DOMParser().parseFromString(html,'text/html');\n    const rows=[];"

helper = r'''  function chooseWaveDates(doc){
    const dates=[...new Set($$('.draw-start',doc).map(el=>{
      const m=(el.textContent||'').match(/(\d{4}\/\d{2}\/\d{2})/);
      return m?m[1]:null;
    }).filter(Boolean))].sort();
    if(!dates.length) return [];
    const today=new Date(); today.setHours(0,0,0,0);
    const parsed=dates.map(d=>({d,t:parseDateTime(d)})).filter(x=>x.t);
    const upcoming=parsed.filter(x=>x.t>=today);
    const base=upcoming.length?upcoming[0]:parsed[parsed.length-1];
    if(!base) return [dates[dates.length-1]];
    return [...new Set(parsed.filter(x=>Math.abs(x.t-base.t)<=86400000).map(x=>x.d))].sort();
  }

  function updateWaveCopy(){
    if(!WAVE_DATES.length) return;
    const short=WAVE_DATES.map(d=>{const p=d.split('/');return `${+p[1]}/${+p[2]}`;});
    const label=short.length===1?short[0]:`${short[0]}–${short[short.length-1]}`;
    const h=$('#pageTitle'); if(h) h.textContent=`${label}｜親友幫抽抽2`;
    const w=$('#waveLabel'); if(w) w.textContent=label;
    document.title=`${label} 親友幫抽抽｜FUNBOX`;
    STORAGE_KEY='aping_beyblade_'+WAVE_DATES.join('_').replace(/\//g,'')+'_visited';
  }

  function extract(html){
    const doc=new DOMParser().parseFromString(html,'text/html');
    WAVE_DATES=chooseWaveDates(doc);
    updateWaveCopy();
    const rows=[];'''

if marker not in s:
    raise SystemExit('extract marker not found')

s = s.replace(marker, helper, 1)
p.write_text(s, encoding='utf-8')
