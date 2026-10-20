"""Daily checker. Fetches each item's official page, detects changes, optionally extracts fields with Claude."""
import json,hashlib,re,os,datetime as dt,urllib.request
F='docs/data.json'; today=dt.date.today().isoformat()
d=json.load(open(F)); key=os.environ.get('ANTHROPIC_API_KEY'); model=os.environ.get('CLAUDE_MODEL','claude-sonnet-5-5')
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 masters-tracker'})
    h=urllib.request.urlopen(r,timeout=25).read().decode('utf-8','ignore')
    h=re.sub(r'(?s)<(script|style).*?</\1>','',h); return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',h))
def extract(text,name):
    body=json.dumps({"model":model,"max_tokens":400,"messages":[{"role":"user","content":f"From this official page text for '{name}', return ONLY JSON: {{\"deadline\":\"YYYY-MM-DD or null\",\"ielts\":str|null,\"toefl\":str|null,\"gre\":str|null,\"fee\":str|null}}. Use the next intake (Fall 2027 / 2027-28). Never guess; null if absent.\n\n{text[:14000]}"}]}).encode()
    r=urllib.request.Request('https://api.anthropic.com/v1/messages',body,{'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'})
    t=json.load(urllib.request.urlopen(r,timeout=60))['content'][0]['text']
    return json.loads(re.search(r'\{.*\}',t,re.S).group(0))
for k in ('programs','scholarships'):
    for it in d[k]:
        if not it.get('link'): continue
        try: txt=get(it['link'])
        except Exception as e: it['check']='fetch failed'; continue
        h=hashlib.sha256(txt.encode()).hexdigest()[:16]
        if it.get('hash') and it['hash']!=h: it['changed']=today
        need=(it.get('changed')==today) or not it.get('deadline') or not it.get('hash')
        it['hash']=h; it['checked']=today; it['check']='ok'
        if key and need:
            try:
                x=extract(txt,it.get('uni') or it.get('name'))
                if x.get('deadline') and re.match(r'\d{4}-\d\d-\d\d$',x['deadline']): it['deadline']=x['deadline']; it['conf']='Auto-extracted - verify'
                for f in ('ielts','toefl','gre','fee'):
                    if x.get(f) and k=='programs': it[f]=x[f]
            except Exception as e: it['check']='extract failed'
d['meta']['updated']=today
json.dump(d,open(F,'w'),ensure_ascii=False,separators=(',',':'))
