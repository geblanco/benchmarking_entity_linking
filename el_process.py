"""Perform mention processing over QA dataset for EL mention
Benchmark, includes both the custom, trigram based and baseline
methods from the paper."""

from nltk.metrics import edit_distance
from utils import clean_str, ngrams, str_to_trigrams_dict, overlap_trigrams_score, MinStore, MentionSet

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

def get_mentions(dbr, question):
  tris = str_to_trigrams_dict(dbr.lower())
  sets = []
  best_guess = MinStore()
  current_mention = MentionSet()
  for index, word in enumerate(question.split(' ')):
    word_trigrams = ngrams(word.lower())
    prob = overlap_trigrams_score(tris, word_trigrams)
    if not current_mention.append(word, index, prob):
      mention = MentionSet(mention=[word], indexes=[index], prob=prob)
      best_guess.store(mention, prob)
      if not current_mention.is_empty():
        sets.append(current_mention)
      current_mention = MentionSet()
  
  if not current_mention.is_empty():
    sets.append(current_mention)

  if len(sets) == 0:
    # no match found, best guess time
    best_guess = best_guess.get_item()
    sets = [best_guess]

  return sets

def dist(mention, dbr):
  ment = ' '.join(mention) if type(mention) is list else mention
  ment_len = len(''.join(mention))
  return edit_distance(ment, dbr) / ment_len

def match_by_trigrams(raw_dbr, raw_question):
  dbr = raw_dbr.lower()
  question = raw_question.lower()
  mentions = get_mentions(dbr, question)
  best_mention = MinStore(cmp='min_metric')
  for mention in mentions:
    m = MentionSet(mention=mention.get_mention(), indexes=mention.get_indexes(), prob=mention.prob)
    mention.reduce(dbr)
    mention_distance = dist(' '.join(mention.get_mention()), dbr)
    best_mention.store(mention, mention_distance)

  best_mention = best_mention.get_item()
  if best_mention is not None:
    question_parts = raw_question.split(' ')
    best_mention = ' '.join([question_parts[idx] for idx in best_mention.get_indexes()])

  return best_mention

def simple_match(raw_dbr, raw_question):
  dbr = raw_dbr.lower()
  question = raw_question.lower()
  question_parts = question.split(' ')
  # all the spans of size equal to the number of tokens in dbr
  n_tokens = len(dbr.split(' '))
  parts = [(question_parts[i:i+n_tokens], i, i+n_tokens)
            for i in range(0, len(question_parts)-(n_tokens-1))]
  # get the span that minimizes edit distance
  best_mention = MinStore(cmp='min_metric')
  # print('simple_match parts', parts)
  for part, word_start, word_end in parts:
    indexes = list(range(word_start, word_end))
    part_mention = ' '.join(part)
    distance = dist(part_mention, dbr)
    mention = MentionSet(mention=part, indexes=indexes, prob=distance)
    best_mention.store(mention, distance)

  best_mention = best_mention.get_item()
  if best_mention is not None:
    question_parts = raw_question.split(' ')
    best_mention = ' '.join([question_parts[idx] for idx in best_mention.get_indexes()])

  return best_mention

def merge(raw_dbr, mention_1, mention_2):
  dbr = raw_dbr.lower()
  if mention_1 is None or type(mention_1) is not str:
    return mention_2
  if mention_2 is None or type(mention_2) is not str:
    return mention_1
  ed_1 = edit_distance(mention_1.lower(), dbr)
  ed_2 = edit_distance(mention_2.lower(), dbr)
  ret = mention_2
  if ed_1 < ed_2:
    ret = mention_1
  return ret

def process(eval_tuple, baseline=False):
  dbr = clean_str(eval_tuple['dbr'])
  question = clean_str(eval_tuple['question'])
  match_fn = simple_match if baseline else match_by_trigrams
  mention = match_fn(dbr, question)
  # mention = merge(dbr, match_by_trigrams(dbr, question), simple_match(dbr, question))
  if mention is None:
    mention = ''
  output = eval_tuple.copy()
  output['mention'] = mention
  return output

__all__ = [ process ]
