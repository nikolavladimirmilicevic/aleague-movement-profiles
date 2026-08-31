"""
A-League Player Style Profiler - build site data
Source: SkillCorner Open Data, season aggregates, A-League 2024/25
"""
import pandas as pd, numpy as np, glob, json

MIN_MATCHES = 8
AGG = 'data/aggregates/'

# label, category, higher-is-better (for strength/weakness wording)
FEATURES = [
    # --- Physical -----------------------------------------------------------
    ('total_metersperminute_full_all',    'Distance / min',        'Physical'),
    ('hi_count_full_all',                 'High-intensity actions','Physical'),
    ('sprint_count_full_all',             'Sprints',               'Physical'),
    ('psv99',                             'Peak speed',            'Physical'),
    ('highaccel_count_full_all',          'High accelerations',    'Physical'),
    ('highdecel_count_full_all',          'High decelerations',    'Physical'),
    # --- Off-ball movement --------------------------------------------------
    ('offballrun_count_p30tip',           'Off-ball runs',         'Movement'),
    ('offballrun_count_dangerous_p30tip', 'Dangerous runs',        'Movement'),
    ('offballrun_count_received_p30tip',  'Runs receiving ball',   'Movement'),
    ('offballrun_count_penaltyarea_p30tip','Runs into the box',    'Movement'),
    ('behindrun_count_p30tip',            'Runs in behind',        'Movement'),
    ('supportrun_count_p30tip',           'Support runs',          'Movement'),
    ('overlaprun_count_p30tip',           'Overlaps',              'Movement'),
    ('pullinghalfspacerun_count_p30tip',  'Half-space runs',       'Movement'),
    ('crossreceiverrun_count_p30tip',     'Cross-receiver runs',   'Movement'),
    ('droppingoffrun_count_p30tip',       'Dropping off',          'Movement'),
    # --- Passing ------------------------------------------------------------
    ('pass_count_attempted_p30tip',       'Passes attempted',      'Passing'),
    ('pass_pct_completed',                'Pass completion %',     'Passing'),
    ('pass_avgdistance',                  'Avg pass distance',     'Passing'),
    ('pass_count_linebreak_attempted_p30tip','Line-breaking passes','Passing'),
    ('pass_count_dangerous_attempted_p30tip','Dangerous passes',   'Passing'),
    ('pass_count_torun_attempted_p30tip', 'Passes to runs',        'Passing'),
    ('pass_count_longrange_attempted_p30tip','Long-range passes',  'Passing'),
    ('pass_count_onetouch_attempted_p30tip','One-touch passes',    'Passing'),
    ('pass_count_shotwithin10s_p30tip',   'Passes into shots',     'Passing'),
]

ph = pd.read_csv(glob.glob(AGG + '*physical*.csv')[0])
ob = pd.read_csv(glob.glob(AGG + '*obr*.csv')[0])
pa = pd.read_csv(glob.glob(AGG + '*passing*.csv')[0])

# 1. rows are player x position_group -> keep each player's primary role
def primary(df, col):
    return df.sort_values(col, ascending=False).drop_duplicates('player_id', keep='first')
ph = primary(ph, 'count_match')
ob = primary(ob, 'performance_included_count')
pa = primary(pa, 'performance_included_count')

# 2. merge on player_id, avoiding duplicate metadata columns
def slim(df, cols):
    return df[['player_id'] + [c for c in cols if c in df.columns]]
cols = [c for c, _, _ in FEATURES]
df = (ph[['player_id', 'player_short_name', 'player_name', 'team_name',
          'position_group', 'count_match', 'minutes_full_all', 'player_birthdate']
         + [c for c in cols if c in ph.columns]]
      .merge(slim(ob, cols), on='player_id')
      .merge(slim(pa, cols), on='player_id'))

df = df[df.count_match >= MIN_MATCHES].reset_index(drop=True)
FEATURES = [(k, l, c) for k, l, c in FEATURES if k in df.columns]

# 3. percentile rank WITHIN position group
pct = pd.DataFrame(index=df.index)
for k, _, _ in FEATURES:
    pct[k] = (df.groupby('position_group')[k].rank(pct=True, na_option='keep') * 100)

# 4. age
def age(b):
    try: return int((pd.Timestamp('2025-06-01') - pd.Timestamp(b)).days / 365.25)
    except Exception: return None

players = []
for i, r in df.iterrows():
    players.append({
        'id':   int(r.player_id),
        'name': r.player_short_name,
        'full': r.player_name if isinstance(r.player_name, str) else r.player_short_name,
        'team': r.team_name.replace(' Football Club', '').replace(' FC', ''),
        'pos':  r.position_group,
        'mp':   int(r.count_match),
        'min':  round(float(r.minutes_full_all), 1),
        'age':  age(r.player_birthdate),
        'p':    [None if pd.isna(pct.loc[i, k]) else round(float(pct.loc[i, k]), 1)
                 for k, _, _ in FEATURES],
        'v':    [None if pd.isna(r[k]) else round(float(r[k]), 2)
                 for k, _, _ in FEATURES],
    })

out = {
    'meta': {
        'source': 'SkillCorner Open Data',
        'competition': 'A-League Men 2024/25',
        'min_matches': MIN_MATCHES,
        'n_players': len(players),
    },
    'features': [{'key': k, 'label': l, 'cat': c} for k, l, c in FEATURES],
    'players': sorted(players, key=lambda x: x['name']),
}
json.dump(out, open('/home/claude/site_data.json', 'w'), ensure_ascii=False)
print(f"{len(players)} players, {len(FEATURES)} features")
print("by position:", df.position_group.value_counts().to_dict())
print("coverage: %.1f%% of percentile cells filled" %
      (100 * pct.notna().mean().mean()))
