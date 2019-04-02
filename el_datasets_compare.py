#!/usr/bin/env python

"""Compare various QA-EL datasets

Given two or more QA datasets, compare it's mention field
and output the result to a new file.
"""

from os.path import dirname, basename, splitext, abspath

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--dataset',
    '-d',
    type=str,
    required=True,
    action='append',
    help='Datasets to process.')
parser.add_argument(
    '--output',
    '-o',
    type=str,
    required=False,
    default=None,
    help='Output path to place the results.')

FLAGS, unparsed = parser.parse_known_args()

if len(FLAGS.dataset) < 2:
  parser.error('Provide two datasets to compare!')

output = FLAGS.output
if output is None:
  output = splitext(abspath(FLAGS.dataset[0]))[0] + '_processed.json'

datasets = []
for dataset_path in FLAGS.dataset:
  datasets.append(json.load(open(abspath(dataset_path), 'r'))['questions'])

n_datasets = len(datasets)
questions = []
for data in zip(*datasets):
  for index in range(n_datasets-1):
    assert(data[index]['id'] == data[index+1]['id'])
    assert(data[index]['question_id'] == data[index+1]['question_id'])
  diffs = []
  mentions = [d['mention'] for d in data]
  for index in range(n_datasets-1):
    mention_src = mentions[index]
    for left in range(index+1, n_datasets):
      if mention_src != mentions[left]:
        name = 'mention_d{}'.format(index+1)
        diffs.append(( name, mention_src ))
        name = 'mention_d{}'.format(left+1)
        diffs.append(( name, mentions[left] ))

  if len(diffs):
    question = dict(id=data[0]['id'], question_id=data[0]['question_id'],
        dbr=data[0]['dbr'], question=data[0]['question'])
    for diff in diffs:
      question[diff[0]] = diff[1]
    questions.append(question)

if len(questions):
  obj = dict()
  for idx, dataset_path in enumerate(FLAGS.dataset):
    obj['d{}'.format(idx+1)] = abspath(dataset_path)
    
  obj['questions'] = questions
  
  json.dump(fp=open(output, 'w'), obj=obj, ensure_ascii=False)
else:
  print('No differences!')
