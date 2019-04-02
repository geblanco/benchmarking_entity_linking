#!/usr/bin/env python

"""Perform process or evaluation operations over QA-EL dataset for EL mention Benchmark

Given the QA dataset prepared for EL, either process it to get the
mentions or evaluate the already processed mentions.
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

from os.path import splitext, abspath, basename
from el_process import process
from el_evaluate import evaluate_from_dbr, evaluate_from_annotation, evaluate_from_annotation_set
from utils import find_question, find_error

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
  '-d',
  '--dataset',
  type=str,
  required=True,
  help='LCQuad dataset to process.')
parser.add_argument(
  '-a',
  '--annotations',
  type=str,
  required=False,
  default=None,
  help='LCQuad dataset annotations to compare against.')
parser.add_argument(
  '-o',
  '--output',
  type=str,
  required=False,
  default=None,
  help='Output path to place the results.')
parser.add_argument(
  '-p',
  '--process',
  required=False,
  dest='process',
  action='store_true',
  default=True,
  help='Process dataset with custom approach (read paper for further explanation).')
parser.add_argument(
  '-b',
  '--baseline',
  required=False,
  dest='baseline',
  action='store_true',
  default=False,
  help='Process dataset with baseline (read paper for further explanation).')
parser.add_argument(
  '-e',
  '--evaluate',
  required=False,
  dest='evaluate',
  action='store_true',
  default=False,
  help='Evaluate baseline.')
parser.add_argument(
  '-k',
  '--keep',
  required=False,
  dest='keep',
  action='store_true',
  default=False,
  help='Keep answers that were wrong in a separate file.')

FLAGS, unparsed = parser.parse_known_args()
dataset = abspath(FLAGS.dataset)
output = FLAGS.output

if output is None:
  output = splitext(dataset)[0] + '_processed.json'

data = json.load(open(dataset, 'r'))
output_dataset = {}
output_dataset['dataset'] = data.get('dataset', { 'id': basename(dataset) })
output_questions = []

# either process
if not FLAGS.evaluate:
  for eval_tuple in data['questions']:
    output_questions.append(process(eval_tuple, baseline=FLAGS.baseline))
else:
  total = len(data['questions'])
  hits = 0
  # or evaluate
  if not FLAGS.annotations:
    for eval_tuple in data['questions']:
      if evaluate_from_dbr(eval_tuple):
        hits +=1
      elif FLAGS.keep:
        output_questions.append(eval_tuple)
    print('Acc {:.4f} ({}/{})'.format(hits/total, hits, total))
  # evaluate from annotations
  else:
    annotations_dataset = json.load(open(abspath(FLAGS.annotations), 'r'))
    annotations = annotations_dataset['total']['annotated']
    annotations_errors = annotations_dataset['total']['errors']
    total = len(annotations)
    errors = { k: [] for k in annotations_errors }
    for annotation in annotations:
      question = find_question(annotation, data['questions'])
      assert(question is not None)
      if evaluate_from_annotation(question, annotation):
        hits +=1
      else:
        error_key = find_error(annotation, annotations_errors)
        errors[error_key].append([question['id'], question['question_id']])
        if FLAGS.keep:
          output_questions.append(question)
    print(json.dumps(errors, ensure_ascii=False))

  print('Acc {:.4f} ({}/{})'.format(hits/total, hits, total))

output_dataset['questions'] = output_questions
if not FLAGS.evaluate or FLAGS.keep:
  json.dump(obj=output_dataset, fp=open(output, 'w'), ensure_ascii=False)
