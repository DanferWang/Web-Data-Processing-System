#!/bin/sh
echo "Processing webpages ..."
python3 NeuroNER.py
python3 linking.py > sample_predictions.tsv
echo "Computing the scores ..."
python3 score.py data/sample_annotations.tsv sample_predictions.tsv
