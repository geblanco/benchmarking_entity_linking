#!/usr/bin/env python

"""Process a QA dataset for EL mention Benchmark

Given a QA dataset, transform it to output a dataset with
one datapoint for each entity, and unique questions. Every datapoint
holds the original QA question id, which maybe repeated because
a QA datapoint may comprise various EL mention datapoints (one
for each entity), a unique auto-generated id, the natural language
question and the entity to be linked against.

Also, extract basic statistics about the dataset:
 Number of Questions, Questions with dbrs, Avg dbr per Question and Unique dbrs
"""

from utils import clean_str

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import re
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
  '-d',
  '--dataset',
  type=str,
  required=True,
  help='The lquad json dataset to process.')
parser.add_argument(
  '-s',
  '--stats',
  required=False,
  dest='stats',
  action='store_true',
  default=False,
  help='Whether to output dataset stats or not.')
parser.add_argument(
  '-o',
  '--output',
  type=str,
  default=None,
  help='The output file to store the processed dataset.')

FLAGS, unparsed = parser.parse_known_args()

DBR_REG = re.compile('<(http://dbpedia.org/resource/[^>]+)>')

def process_sparql(sparql_str):
  dbrs = DBR_REG.findall(sparql_str)
  return dbrs

data = json.load(open(FLAGS.dataset, 'r'))

# stats:
# #Q, #Q with dbrs, #Avg #dbr per Q, #Unique dbrs
questions_with_dbr = []
unique_dbrs = []
avg_dbrs_question = []

unique_questions = []
output_questions = []
for eval_tuple in data['questions']:
  try:
    question = eval_tuple['question'][0]['string']
    dbrs = process_sparql(eval_tuple['query']['sparql'])
    # filter repeated questions
    if len(dbrs):
      # stats
      questions_with_dbr.append(question)
      avg_dbrs_question.append(len(dbrs))
      for dbr in dbrs:
        d = clean_str(dbr)
        if d not in unique_dbrs:
          unique_dbrs.append(d)
      # dataset build
      if question not in unique_questions:
        unique_questions.append(question)
        for dbr in dbrs:
          datapoint = {
            'id': len(output_questions) +1,
            'question_id': int(eval_tuple['id']),
            'question': question,
            'dbr': dbr
          }
          output_questions.append(datapoint)
  except Exception as e:
    raise e

if FLAGS.output is not None:
  json.dump(fp=open(FLAGS.output, 'w'), obj={ 'questions': output_questions }, ensure_ascii=False)

if FLAGS.stats:
  print('Dataset: {}'.format(FLAGS.dataset))
  print('-> Questions: {}'.format(len(data['questions'])))
  print('-> Questions with dbr {}'.format(len(questions_with_dbr)))
  print('-> Avg #dbr per Question {:.2f}'.format(sum(avg_dbrs_question)/len(questions_with_dbr)))
  print('-> Unique dbrs {}'.format(len(unique_dbrs)))