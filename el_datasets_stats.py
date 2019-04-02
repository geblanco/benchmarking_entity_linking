#!/usr/bin/env python

"""Get basic stats from QA-EL datasets

Given an EL dataset get some basic stats like
number of unique questions, entities and total
number of samples.
"""

from utils import clean_str
from collections import defaultdict

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import json
import sys

if len(sys.argv) < 2:
  print('Usage dataset_stats.py <dataset>')
  sys.exit(0)

# allow raise error
data = json.load(open(sys.argv[1], 'r'))
samples = data['questions']

unique_questions = defaultdict(int)
unique_entities = defaultdict(int)

for sample in samples:
  question = clean_str(sample['question'])
  dbr = clean_str(sample['dbr'])
  unique_questions[question] +=1
  unique_entities[dbr] += 1

print('Unique Questions {}'.format(len(unique_questions)))
print('Unique Entities {}'.format(len(unique_entities)))
print('Total Samples {}'.format(len(samples)))
