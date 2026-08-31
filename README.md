# A-League movement profiles

Percentile movement profiles and style-similarity search for 146 A-League Men players,
2024/25 season, built on [SkillCorner Open Data](https://github.com/SkillCorner/opendata).

Live: `https://<username>.github.io/<repo>/`

## What it does

Broadcast tracking data captures where players are, not just what they do on the ball.
This tool turns that into a readable profile for each player:

- **25 metrics** across three areas: physical output, off-ball movement, and passing.
- **Percentiles within position group**, because eight kilometres from a centre-back and
  eight from a winger are not the same thing.
- **Style similarity**: which other players in the league move like this one. This measures
  likeness, not quality.
- **Overlay**: pin a second player onto the profile to compare directly.

## Method

Rates come normalised per 30 minutes of team possession, so a player at a possession-heavy
club is not flattered by volume. Peak speed is the 99th percentile of sprint velocity, which
discards tracking noise at the top end.

Three decisions worth stating, because they change the output:

1. **Sample floor.** Players with fewer than 8 matches are excluded. This drops the pool from
   406 to 146 but removes profiles built on one or two appearances.
2. **Duplicate rows.** The source has one row per player *and position group*, so a player who
   changed role appears twice. The role he played most is kept.
3. **Similarity.** Euclidean distance across all 25 percentiles, restricted to the same
   position group.

## Does the data behave?

Median raw values by position, as a sanity check. None of this is encoded in the code; it
falls out of the data.

| | Centre-back | Full-back | Midfield | Wide attacker | Centre forward |
|---|---|---|---|---|---|
| Runs in behind | 0.00 | 0.67 | 0.24 | 3.20 | 8.58 |
| Long-range passes | 4.93 | 2.02 | 2.22 | 1.14 | 0.40 |
| Runs into the box | 0.16 | 1.85 | 1.33 | 5.32 | 10.07 |
| Overlaps | 0.00 | 2.29 | 0.28 | 0.88 | 0.13 |
| Metres per minute | 104.2 | 113.9 | 124.2 | 117.9 | 114.5 |

Runs in behind and box entries rise up the pitch, long passing falls, overlapping is a
full-back's move, and midfielders cover the most ground per minute.

## Build

```bash
git clone https://github.com/SkillCorner/opendata.git
cp build_data.py build_site.py opendata/ && cd opendata
python3 build_data.py     # aggregates -> site_data.json
python3 build_site.py     # site_data.json -> index.html
```

`index.html` is self-contained: data is embedded, there are no runtime dependencies and no
build step for the browser.

## Limitations

Broadcast tracking sees only what the camera shows, so off-screen players are extrapolated
rather than measured. One league and one season means the percentiles describe this
population only. And a movement profile says how a player plays, not how well.
