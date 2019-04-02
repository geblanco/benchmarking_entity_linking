#!/usr/bin/env python

"""Merge various QA-EL datasets

Given a directory with QA-EL datasets, merge them into
a single file avoiding repetitions.
"""

from os.path import dirname, basename, splitext, abspath, join

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import sys, os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d',
    '--dir',
    type=str,
    required=True,
    help='Dir with datasets to merge.')
parser.add_argument(
    '-o',
    '--output',
    type=str,
    required=False,
    default=None,
    help='Output path to place the results.')

FLAGS, unparsed = parser.parse_known_args()

output = FLAGS.output
if output is None:
  output = splitext(abspath(FLAGS.dataset[0]))[0] + '_merged.json'

datasets = []
for dataset_path in os.listdir(FLAGS.dir):
  datasets.append(json.load(open(abspath(join(FLAGS.dir, dataset_path)), 'r'))['questions'])

questions = []
hashes = []
for dataset in datasets:
  for datapoint in dataset:
    question_str = datapoint['question']
    question_dbr = datapoint['dbr']
    question_hash = question_str + question_dbr
    if question_hash not in hashes:
      question_out = {
        'id': len(questions)+1,
        'question_id': datapoint['question_id'],
        'question': question_str,
        'dbr': question_dbr
      }
      questions.append(question_out)

obj = { 'dataset': { 'id': basename(output) }, 'questions': questions }
json.dump(fp=open(output, 'w'), obj=obj, ensure_ascii=False)
