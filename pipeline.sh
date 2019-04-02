#!/bin/bash

./el_datasets_prepare.py

el_datasets_dir="$(pwd)/datasets_el"
if [[ ! -d "$el_datasets_dir" ]]; then
  mkdir "$el_datasets_dir"
fi

stats="$(pwd)/stats"

if [[ -f $stats ]]; then
  rm $stats
fi

for dataset in $(find datasets -iname "*.json"); do
  el_dataset="$el_datasets_dir/$(basename $dataset)"
  if [[ ! -f "$el_dataset" ]]; then
    echo "-> build $dataset"
    python el_datasets_build.py -d $dataset -o $el_dataset -s >> $stats
  fi
done

results="$(pwd)/results"

if [[ -f $results ]]; then
  rm $results
fi

processed_dir="$(pwd)/datasets_processed"
rm -rf "$processed_dir"
mkdir -p "$processed_dir"

evaluate_dir="$(pwd)/datasets_evaluated"
rm -rf "$evaluate_dir"
mkdir -p "$evaluate_dir"

compare_dir="$(pwd)/datasets_compared"
rm -rf "$compare_dir"
mkdir -p "$compare_dir"

merge_dir="$(pwd)/datasets_to_merge"
rm -rf "$merge_dir"
mkdir -p "$merge_dir"

datasets=$(find datasets_el -iname "*.json")
for dataset in $datasets; do
  # process dataset and evaluate it
  base_dataset=$(basename $dataset)
  process_dataset="datasets_processed/${base_dataset}_process.json"
  baseline_dataset="datasets_processed/${base_dataset}_baseline.json"
  evaluate_process_dataset="datasets_evaluated/${base_dataset}_process_evaluated.json"
  evaluate_baseline_dataset="datasets_evaluated/${base_dataset}_baseline_evaluated.json"
  echo "$dataset -> $process_dataset"
  python el_benchmark.py -d $dataset -p -o $process_dataset
  echo "$dataset -> $baseline_dataset"
  python el_benchmark.py -d $dataset -p -b -o $baseline_dataset
  echo "======= $dataset =======" >> $results
  echo "-> $process_dataset" >> $results
  python el_benchmark.py -d $process_dataset -e -k -o $evaluate_process_dataset >> $results
  echo "-> $baseline_dataset" >> $results
  python el_benchmark.py -d $baseline_dataset -e -k -o $evaluate_baseline_dataset >> $results
  echo "==============================" >> $results
  python el_datasets_compare.py -d $process_dataset -d $baseline_dataset -o "${compare_dir}/${base_dataset}.json"
  cp $evaluate_process_dataset "${merge_dir}/${base_dataset}_process_evaluated.json"
done

python el_datasets_merge.py --dir $merge_dir -o "Complex-EL4QA.json"