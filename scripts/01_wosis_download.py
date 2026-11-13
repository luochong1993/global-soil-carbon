import requests, json, csv, time, sys
URL="https://graphql.isric.org/wosis/graphql"
Q="""{ wosisLatestLayers(first:%d, offset:%d, filter:{upperDepth:{lessThan:30}}, orderBy:LAYER_ID_ASC){ profileId layerId upperDepth lowerDepth date
 phaqValues(first:1){valueAvg} tceqValues(first:1){valueAvg} orgcValues(first:1){valueAvg}
 profile{latitude longitude year countryName} } }"""
out=open('data/wosis_topsoil_layers.csv','w',newline=''); w=csv.writer(out)
w.writerow(['profileId','layerId','top','bot','date','year','lat','lon','country','phaq','tceq','orgc'])
off=0; N=1000; n=0
while True:
    for t in range(5):
        try:
            r=requests.post(URL,json={'query':Q%(N,off)},timeout=300); d=r.json()['data']['wosisLatestLayers']; break
        except Exception as e:
            print('retry',off,e,flush=True); time.sleep(10)
    else: sys.exit('fail')
    if not d: break
    for L in d:
        p=L['profile'] or {}
        f=lambda k: (L[k][0]['valueAvg'] if L[k] else '')
        if L['phaqValues'] or L['tceqValues']:
            w.writerow([L['profileId'],L['layerId'],L['upperDepth'],L['lowerDepth'],L['date'],p.get('year'),p.get('latitude'),p.get('longitude'),p.get('countryName'),f('phaqValues'),f('tceqValues'),f('orgcValues')]); n+=1
    off+=N; print(off,n,flush=True)
out.close()
