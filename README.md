# skynet2
Pointouts system for Scona Swim Team, way overengineered

# Input features - Individual
## Tier 1
- Divs rank
- Divs time
- Seed time

## Tier 2
- Swimmer age
- Stroke of event (Discrete)
- Distance of event
- Seed time compared to mean/median (pct?)
- Divs time compared to mean/median (pct?)

## Tier 3
- Types of strokes swimmer is on overall
- Number of relays swimmer does

# Notes on model performance
- Baseline: divsRank to finalRank:
  - Simple lin reg: 1.6394
  - Robust lin reg: 1.6348
- Linear regression, robust linear with divsRank, seconds improved per meter: 1.639
- Lin reg simple with divsRank, z-scored seconds improved per meter: 1.5273
- Guassian process squared exp GPR: 1.5174