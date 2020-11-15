#!/bin/sh
echo "Processing webpages ..."
python3 starter_code_v2.5.py [path to your WARC file] > your_WARC_predictions.tsv
echo "Computing the scores ..."
python3 score.py [annotation] your_WARC_predictions.tsvs
