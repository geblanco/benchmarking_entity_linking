"""Perform evaluation over QA-EL dataset for EL mention
Benchmark"""

from utils import clean_str, find_question

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"


def evaluate_from_dbr(eval_tuple):
  question = clean_str(eval_tuple['mention'].lower())
  dbr = clean_str(eval_tuple['dbr'].lower())
  return question == dbr

def evaluate_from_annotation(eval_tuple, annot_tuple):
  m1 = clean_str(eval_tuple['mention'].lower())
  m2 = clean_str(annot_tuple['mention'].lower())
  return m1 == m2

def evaluate_from_annotation_set(eval_tuple, annotations):
  annotation = find_question(eval_tuple, annotations)
  assert(annotation is not None)
  return evaluate_from_annotation(eval_tuple, annotation)

__all__ = [ evaluate_from_dbr, evaluate_from_annotation, evaluate_from_annotation_set ]
