"""Daily checker (no API needed). Fetches official pages, detects changes, and conservatively extracts dates/tests with regex."""
import json,hashlib,re,datetime as dt,urllib.request
F='docs/data.json'; T=dt.date.today(); d=json.load(open(F))
M='jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'; MI={m:i+1 for i,m in enumerate(M.split('|'))}
DT=re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+('+M+r')[a-z]*\.?,?\s+(20\d\d)|\b('+M+r')[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)',re.I)
KEY=re.compile(r'deadline|due|apply by|closing date|closes|last date',re.I)
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 masters-tracker'})
    h=urllib.request.urlopen(r,timeout=25).read().decode('utf-8','ignore')
    h=re.sub(r'(?s)<(script|style).*?</\1>','',h); return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',h))
def dates(t):
    out=[]
    for m in DT.finditer(t):
        a=m.groups(); day,mon,yr=(a[0],a[1],a[2]) if a[0] else (a[4],a[3],a[5])
        try: x=dt.date(int(yr),MI[mon.lower()[:3]],int(day))
        except ValueError: continue
        ctx=t[max(0,m.start()-160):m.end()+60]
        if KEY.search(ctx) and T<=x<=T+dt.timedelta(days=420):
            bad=re.search(r'spring|summer|winter',ctx,re.I) and not re.search(r'fall|autumn',ctx,re.I)
            if not bad: out.append((bool(re.search(r'fall|autumn|international|2027',ctx,re.I)),x))
    pref=[x for g,x in out if g] or [x for g,x in out]
    return min(pref) if pref else None
def tests(t):
    r={}
    m=re.search(r'IELTS[^0-9]{0,40}(\d(?:\.\d)?)',t)
    if m and 5.5<=float(m.group(1))<=8.5: r['ielts']=m.group(1)
    m=re.search(r'TOEFL[^0-9]{0,40}(\d{2,3})',t)
    if m and 60<=int(m.group(1))<=120: r['toefl']=m.group(1)+' iBT'
    m=re.search(r'GRE[^.]{0,80}?(not required|optional|required|waived)',t,re.I)
    if m: r['gre']=m.group(1).capitalize()
    return r
for k in ('programs','scholarships'):
    for it in d[k]:
        if not it.get('link'): continue
        try: txt=get(it['link'])
        except Exception: it['check']='fetch failed'; continue
        h=hashlib.sha256(txt.encode()).hexdigest()[:16]
        if it.get('hash') and it['hash']!=h: it['changed']=T.isoformat()
        it['hash']=h; it['checked']=T.isoformat(); it['check']='ok'
        x=dates(txt)
        if x:
            cur=it.get('deadline')
            if not cur: it['deadline']=x.isoformat(); it['conf']='Auto-detected - verify'
            elif cur!=x.isoformat() and not str(it.get('conf','')).startswith('Auto'): it['seen']='Page now mentions '+x.isoformat()+' - verify'
            elif str(it.get('conf','')).startswith('Auto'): it['deadline']=x.isoformat()
        if k=='programs':
            for f,v in tests(txt).items():
                if str(it.get(f,'Check')).startswith('Check'): it[f]=v; it['conf']=it['conf'] if it['conf'].startswith(('High','Medium')) else 'Auto-detected - verify'
d['meta']['updated']=T.isoformat()
json.dump(d,open(F,'w'),ensure_ascii=False,separators=(',',':'))
