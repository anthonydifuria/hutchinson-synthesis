#!/usr/bin/env bash
# render_all.sh -- renders all 21 population-density beta variants in sequence.
#
# Uses a scratch copy of the hutchinson_pure engine, at the repo root
# (../../../_render_scratch_population_sweep from here) so the real hutchinson_pure/
# is never touched. Delete that scratch folder yourself once you're
# happy with the results (rm -rf) -- this script does not delete it.
set -e

SWEEP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="$SWEEP_DIR/../../../_render_scratch_population_sweep"

if [ ! -d "$ENGINE_DIR" ]; then
  echo "ERRORE: motore scratch non trovato in $ENGINE_DIR"
  exit 1
fi
if ! command -v csound >/dev/null 2>&1 && ! command -v csound6 >/dev/null 2>&1; then
  echo "ATTENZIONE: csound non trovato nel PATH -- il render fallira'."
fi

n=0
total=$(ls -d "$SWEEP_DIR"/beta_*/ | wc -l | tr -d ' ')

for dir in "$SWEEP_DIR"/beta_*/; do
  n=$((n+1))
  beta_name=$(basename "$dir")
  echo ""
  echo "=== [$n/$total] Rendering $beta_name ==="
  cp "$dir/config.py" "$ENGINE_DIR/config.py"
  ( cd "$ENGINE_DIR" && python3 main_v1_independent.py )
  cp "$ENGINE_DIR/output/hutchinson_v1.wav" "$dir/${beta_name}.wav"
  cp "$ENGINE_DIR/output/freq.png" "$dir/${beta_name}.png"
  cp "$ENGINE_DIR/output/spazio2d.png" "$dir/${beta_name}_spazio2d.png"
  cp "$ENGINE_DIR/output/sfera3d.png" "$dir/${beta_name}_sfera3d.png"
  cp "$ENGINE_DIR/output/azimuth.png" "$dir/${beta_name}_azimuth.png"
  cp "$ENGINE_DIR/output/elevation.png" "$dir/${beta_name}_elevation.png"
  echo "=== [$n/$total] Fatto: $dir${beta_name}.wav ==="
done

echo ""
echo "Tutti i $total render completati."
echo "Puoi cancellare $ENGINE_DIR quando vuoi (rm -rf), non serve piu'."
