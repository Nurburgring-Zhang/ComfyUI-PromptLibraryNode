import urllib.request, json
req = urllib.request.Request(
    'https://api.github.com/repos/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/commits/880afe4fa134e78373e1248d214f34f0d729b2e1',
    headers={'Authorization': 'token GITHUB_PAT_PLACEHOLDER_3HiLNCBmRVPmA0WNQvHjy04AZ6f', 'User-Agent': 'Mavis'}
)
data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
print('files:', len(data.get('files', [])))
for f in data.get('files', [])[:20]:
    s = f['status']
    fn = f['filename']
    a = f['additions']
    d = f['deletions']
    print('  {}: {} (+{}-{})'.format(s, fn, a, d))
