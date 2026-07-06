import json, re, time, urllib.request, urllib.error

with open('/home/vfalbor/pamabai/journal/vol1/07-newsletter/bench/competitors/raw_apps.json') as f:
    apps = json.load(f)

def extract_owner_repo(url):
    m = re.search(r'github\.com/([^/]+)/([^/?#]+)', url)
    if not m:
        return None, None
    owner, repo = m.group(1), m.group(2)
    repo = repo.replace('.git', '')
    return owner, repo

results = []
calls = 0
MAX_CALLS = 55

for app in apps:
    owner, repo = extract_owner_repo(app['url'])
    entry = {
        'url': app['url'],
        'title': app.get('title'),
        'total_score': app.get('total_score'),
        'recommendation': app.get('recommendation'),
        'hn_points': app.get('hn_points'),
        'hn_comments': app.get('hn_comments'),
        'tested_at': app.get('tested_at'),
        'owner': owner,
        'repo': repo,
        'stars': None,
        'forks': None,
        'gh_status': None,
    }
    # extract hn_sentiment score and community score from scores_json
    try:
        sj = json.loads(app.get('scores_json') or '{}')
        entry['hn_sentiment_score'] = sj.get('hn_sentiment', {}).get('score')
        entry['community_score'] = sj.get('community', {}).get('score')
    except Exception:
        entry['hn_sentiment_score'] = None
        entry['community_score'] = None

    if owner and repo and calls < MAX_CALLS:
        api_url = f'https://api.github.com/repos/{owner}/{repo}'
        req = urllib.request.Request(api_url, headers={'User-Agent': 'benchmark-study'})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                entry['stars'] = data.get('stargazers_count')
                entry['forks'] = data.get('forks_count')
                entry['gh_status'] = 200
        except urllib.error.HTTPError as e:
            entry['gh_status'] = e.code
        except Exception as e:
            entry['gh_status'] = f'error:{e}'
        calls += 1
        time.sleep(2)
    else:
        entry['gh_status'] = 'skipped_rate_limit' if owner else 'no_repo_parsed'

    results.append(entry)
    print(entry['url'], entry['gh_status'], entry['stars'])

with open('/home/vfalbor/pamabai/journal/vol1/07-newsletter/bench/competitors/enriched.json', 'w') as f:
    json.dump(results, f, indent=2)

print('DONE', calls, 'calls made')
