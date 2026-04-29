import urllib.request, json
req1 = urllib.request.Request('http://localhost:8000/api/auth/login/', data=b'{"email":"admin@admin.com", "password":"admin"}', headers={'Content-Type': 'application/json'})
res1 = urllib.request.urlopen(req1)
token = json.loads(res1.read())['token']['access_token']
req2 = urllib.request.Request('http://localhost:8000/api/competencia/create/', data=b'{"name":"T","description":"D","date_start":"2026-06-01T00:00","date_end":"2026-06-02T00:00","category":"explorador","max_teams":16}', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
try:
    res2 = urllib.request.urlopen(req2)
    print(res2.status, res2.read().decode())
except Exception as e:
    if hasattr(e, 'read'):
        print(e.code, e.read().decode())
    else:
        print(e)
