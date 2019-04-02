#!/usr/bin/env python

"""Prepare web questions dataset for EL Benchmarking"""

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import json, sys

if len(sys.argv) < 2:
  print('Usage prepare_web_questions.py <web questions.json>')
  sys.exit(0)

output = []
dataset = json.load(open(sys.argv[1], 'r'))
for question in dataset:
  datapoint = {
    'id': len(output) +1,
    'question': question['utterance'],
    'dbr': question['url'].replace('http://www.freebase.com/view/en', 'http://dbpedia.org/resource')
  }
  output.append(datapoint)

json.dump(fp=open(sys.argv[1] + '_el_prepared.json', 'w'), obj={ 'questions': output }, ensure_ascii=False)