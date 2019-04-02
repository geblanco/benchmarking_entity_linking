from collections import defaultdict

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import re
import unicodedata

trim_reg = [
  [re.compile('_\([^\)]+\)$'), ''],
  [re.compile('\?$'), ''],
  [re.compile('^,'), ''],
  [re.compile(',$'), ''],
  [re.compile('\.$'), ''],
  [re.compile('-'), ' '],
  [re.compile('_'), ' '],
  [re.compile('\s+'), ' ']]

def ngrams(word, n=3):
  if len(word) < n:
    return [word]
  grams = []
  for i in range(len(word) -(n-1)):
    grams.append(word[i:i+n])
  return grams

# global trim_reg
def clean_str(data):
  global trim_reg
  ret = data.replace('http://dbpedia.org/resource/', '')
  # remove dissambiguation from dbpedia (eg: TNT -> TNT_(TV_channel))
  for reg, repl in trim_reg:
    ret = re.sub(reg, repl, ret)
  # remove accents, umlaude... François -> Francois
  # https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-
  # accents-in-a-python-unicode-string
  ret = unicodedata.normalize('NFKD', ret.strip())
  return str(u"".join([c for c in ret if not unicodedata.combining(c)]))

def str_to_trigrams_dict(data):
  tris = defaultdict(int)
  for point in data.split(' '):
    trigrams = ngrams(point)
    for tr in trigrams:
      tris[tr] = 1
  return tris

def overlap_trigrams_score(trigrams_dict, word_trigrams):
  max_com = max(1, len(word_trigrams))
  common_tri = 0
  for gram in word_trigrams:
    if trigrams_dict[gram] == 1:
      common_tri += 1
  prob = common_tri/max_com
  return prob

def find_question(question, dataset):
  for q in dataset:
    if question['question_id'] == q['question_id'] and \
      question['dbr'] == q['dbr']:
      return q
  return None

def find_error(question, errors):
  search = [question['id'], question['question_id']]
  for error_key in errors:
    if search in errors[error_key]:
      return error_key
  return None

class MinStore(object):
  def __init__(self, item=None, metric=None, cmp=None):
    self.item = item
    self.metric = metric
    self.empty = item is None and metric is None
    if cmp == 'min_metric':
      self.cmp = self._min_metric_min_len
    else:
      # if cmp != 'max_metric':
      # unkown metric
      self.cmp = self._max_metric_min_len

  def _max_metric_min_len(self, old_metric, new_metric, old_item, new_item):
    cmp_new_item = new_item[0] if type(new_item) is list else str(new_item)
    cmp_old_item = old_item[0] if type(old_item) is list else str(old_item)
    return (old_metric < new_metric or (old_metric == new_metric and
      len(cmp_new_item) < len(cmp_old_item)))

  def _min_metric_min_len(self, old_metric, new_metric, old_item, new_item):
    cmp_new_item = new_item[0] if type(new_item) is list else str(new_item)
    cmp_old_item = old_item[0] if type(old_item) is list else str(old_item)
    return (new_metric < old_metric or (new_metric == old_metric and
       len(cmp_new_item) < len(cmp_old_item)))

  def store(self, item, metric):
    if self.empty:
      self.item = item
      self.metric = metric
    elif self.cmp(self.metric, metric, self.item, item):
      # maximize metric, minimize size
      self.item = item
      self.metric = metric
    self.empty = item is None and metric is None

  def get_item(self):
    return self.item

class MentionSet(object):
  def __init__(self, mention=None, indexes=None, prob=0.0):
    indexes = [] if indexes is None else indexes
    mention = [] if mention is None else mention
    self.mention = mention
    self.indexes = indexes
    self.prob = prob
    self.prob_thr = 0.7

  def __len__(self):
    return ''.join(self.mention)

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return 'Mention: {}, Index {}'.format(self.get_mention(), self.get_indexes())

  def get_mention(self):
    return self.mention

  def get_indexes(self):
    return self.indexes

  def is_empty(self):
    return len(self.mention) == 0

  def append(self, word, index, prob):
    if prob > self.prob_thr:
      self.mention.append(word)
      self.indexes.append(index)
      self.prob = prob
    return prob > self.prob_thr

  # global overlap_trigrams_score, str_to_trigrams_dict
  def align(self, dbr_part):
    global overlap_trigrams_score, str_to_trigrams_dict
    # alignment part trigrams
    trigrams = str_to_trigrams_dict(dbr_part)
    scores = [overlap_trigrams_score(trigrams, ngrams(mention)) for mention in self.mention]
    score_max = max(scores)
    trim = None
    if score_max > 0.7:
      trim = scores.index(score_max)
    return trim

  def _get_trim_indexes(self, dbr):
    start_trim = 0
    end_trim = len(self.mention)
    dbr_parts = dbr.lower().split(' ')
    if len(dbr_parts) < 2:
      return start_trim, end_trim

    start_trim = self.align(dbr_parts[0])
    end_trim = self.align(dbr_parts[-1])
    start_trim = start_trim if start_trim is not None else 0
    # starts from 0, compensate
    end_trim = (end_trim +1) if end_trim is not None else len(self.mention)

    if start_trim > end_trim or (end_trim - start_trim) == 0:
      # print('Warning! Bad trimming', self.mention, dbr)
      start_trim = 0
      end_trim = len(self.mention)

    return start_trim, end_trim

  def reduce(self, dbr):
    start_trim, end_trim = self._get_trim_indexes(dbr)
    self.mention = self.mention[start_trim:end_trim]
    self.indexes = self.indexes[start_trim:end_trim]

__all__ = [
  ngrams,
  find_question,
  find_error,
  clean_str,
  str_to_trigrams_dict,
  overlap_trigrams_score,
  MinStore,
  MentionSet
]
