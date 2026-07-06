import json
from collections import defaultdict

with open('/home/vfalbor/pamabai/journal/vol1/07-newsletter/bench/competitors/enriched.json') as f:
    data = json.load(f)

def spearman(pairs):
    # pairs: list of (x, y), both numeric, no None
    n = len(pairs)
    if n < 3:
        return None, n
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    def rank(vals):
        sorted_idx = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0] * len(vals)
        i = 0
        while i < len(sorted_idx):
            j = i
            while j + 1 < len(sorted_idx) and vals[sorted_idx[j+1]] == vals[sorted_idx[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1  # 1-indexed
            for k in range(i, j+1):
                ranks[sorted_idx[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(xs)
    ry = rank(ys)
    n = len(rx)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i]-mean_rx)*(ry[i]-mean_ry) for i in range(n))
    denx = sum((rx[i]-mean_rx)**2 for i in range(n)) ** 0.5
    deny = sum((ry[i]-mean_ry)**2 for i in range(n)) ** 0.5
    if denx == 0 or deny == 0:
        return None, n
    rho = num / (denx * deny)
    return rho, n

# valid subset: has stars (gh_status==200)
valid = [d for d in data if d.get('gh_status') == 200 and d.get('stars') is not None]
print(f"n total sampled: {len(data)}, n with valid github data: {len(valid)}")

missing_stars = len(data) - len(valid)
print(f"missing/failed github lookups: {missing_stars}")

# score vs stars
pairs_score_stars = [(d['total_score'], d['stars']) for d in valid if d.get('total_score') is not None]
rho1, n1 = spearman(pairs_score_stars)
print(f"\nscore vs stars: rho={rho1}, n={n1}")

# score vs hn_points
pairs_score_hn = [(d['total_score'], d['hn_points']) for d in valid if d.get('total_score') is not None and d.get('hn_points') is not None]
rho2, n2 = spearman(pairs_score_hn)
print(f"score vs hn_points: rho={rho2}, n={n2}")

# stars vs hn_points (community internal agreement)
pairs_stars_hn = [(d['stars'], d['hn_points']) for d in valid if d.get('hn_points') is not None]
rho3, n3 = spearman(pairs_stars_hn)
print(f"stars vs hn_points: rho={rho3}, n={n3}")

# hn_sentiment score (from scores_json) vs actual hn_points
pairs_sent_hn = [(d['hn_sentiment_score'], d['hn_points']) for d in valid if d.get('hn_sentiment_score') is not None and d.get('hn_points') is not None]
rho4, n4 = spearman(pairs_sent_hn)
print(f"hn_sentiment criterion vs actual hn_points: rho={rho4}, n={n4}")

# community score (from scores_json) vs actual hn_points, for reference
pairs_comm_hn = [(d['community_score'], d['hn_points']) for d in valid if d.get('community_score') is not None and d.get('hn_points') is not None]
rho5, n5 = spearman(pairs_comm_hn)
print(f"community criterion vs actual hn_points: rho={rho5}, n={n5}")

# also score vs forks
pairs_score_forks = [(d['total_score'], d['forks']) for d in valid if d.get('total_score') is not None and d.get('forks') is not None]
rho6, n6 = spearman(pairs_score_forks)
print(f"score vs forks: rho={rho6}, n={n6}")

# Badge sanity
by_badge = defaultdict(list)
for d in valid:
    badge = d.get('recommendation')
    by_badge[badge].append(d)

print("\n--- Badge tier stats (mean stars, mean hn_points) ---")
badge_table = {}
for badge, items in by_badge.items():
    stars_list = [x['stars'] for x in items]
    hn_list = [x['hn_points'] for x in items if x.get('hn_points') is not None]
    mean_stars = sum(stars_list)/len(stars_list) if stars_list else None
    median_stars = sorted(stars_list)[len(stars_list)//2] if stars_list else None
    mean_hn = sum(hn_list)/len(hn_list) if hn_list else None
    badge_table[badge] = {
        'n': len(items),
        'mean_stars': mean_stars,
        'median_stars': median_stars,
        'mean_hn_points': mean_hn,
    }
    print(f"{badge}: n={len(items)}, mean_stars={mean_stars:.1f}, median_stars={median_stars}, mean_hn={mean_hn}")

summary = {
    'n_sampled': len(data),
    'n_valid_github': len(valid),
    'n_missing_github': missing_stars,
    'correlations': {
        'score_vs_stars': {'rho': rho1, 'n': n1},
        'score_vs_hn_points': {'rho': rho2, 'n': n2},
        'stars_vs_hn_points': {'rho': rho3, 'n': n3},
        'hn_sentiment_criterion_vs_actual_hn_points': {'rho': rho4, 'n': n4},
        'community_criterion_vs_actual_hn_points': {'rho': rho5, 'n': n5},
        'score_vs_forks': {'rho': rho6, 'n': n6},
    },
    'badge_table': badge_table,
}

with open('/home/vfalbor/pamabai/journal/vol1/07-newsletter/bench/competitors/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nWrote summary.json")
