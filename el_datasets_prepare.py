#!/usr/bin/env python

"""Prepare QA datasets for EL Benchmark

Download, extract and convert any version of
QALD or LC-QuAD datasets to a suitable format
for EL Benchmark, conveting xml to json.
"""

__author__ = "Guillermo Echegoyen"
__credits__ = ["Guillermo Echegoyen"]
__license__ = "GPL v3"
__version__ = "1.0.0"
__maintainer__ = "Guillermo Echegoyen"
__email__ = "gblanco@lsi.uned.es"
__status__ = "Production"

import sys, os, re, json
import xmltodict

if sys.version_info.major == 2:
  from urllib import urlretrieve as download
else:
  from urllib.request import urlretrieve as download

def correct_sparql_query(key, value):
  return key, { 'sparql': resolve_prefixes(value) }

# global prefix_def
def resolve_prefixes(query):
  global prefix_def
  rest_query_lines = []
  prefixes = []
  for line in query.split('\n'):
    if line.lower().startswith('prefix'):
      prefixes.append(line)
    else:
      rest_query_lines.append(line)
  rest_query = '\n'.join(rest_query_lines)
  prefix_substitutions = list(map(lambda prefix: prefix_def.findall(prefix)[0], prefixes))
  for sub, uri in prefix_substitutions:
    r1 = r'{}:(\w+)'.format(sub)
    r2 = r'<{}\1>'.format(uri)
    rest_query = re.sub(r1, r2, rest_query)
  return rest_query

# global xml_path_subs
def processor(path, key, value):
  global xml_path_subs
  # path comes as
  # [('dataset', None), ('question', OrderedDict([('id', '11')])), ('string', None)]
  # prepare as 'dataset.question.string
  parsed_path = '.'.join(list(zip(*path))[0])
  if parsed_path in xml_path_subs.keys():
    for xml_path, xml_fn in xml_path_subs.items():
      if xml_path == parsed_path:
        key, value = xml_fn(key, value)
        break
  if key.startswith('@'):
    key = key[1:]
  return key, value

def check_key(obj, key):
  ret = False
  if key.find('.') == -1:
    ret = obj.get(key, None) is not None
  else:
    subk = key.split('.')
    if obj.get(subk[0]) is not None:
      ret = check_key(obj[subk[0]], '.'.join(subk[1:]))
  return ret

def check_keys(question, keys=None):
  if keys is None:
    keys = ['question', 'query.sparql']
  for key in keys:
    if not check_key(question, key):
      return None
    
  return question

def multilingual_question(question):
  # Comes as array of lang and text for the question and
  # keywords, pair to make a question[{string, keywords, language}]
  # filter bad questions
  if check_keys(question, ['string', 'query.sparql']) is None:
    # no cookie for you
    return None
  
  question = json.loads(json.dumps(obj=question, ensure_ascii=False))

  # correct non array questions
  if type(question['string']) is dict:
    question['string'] = [question['string']]

  if question.get('keywords') is None:
    question['keywords'] = [{} for _ in range(len(question['string']))]

  question_str = question['string']
  question_keywords = question['keywords']
  assert len(question_str) == len(question_keywords)
  question_value = []
  for q_str, q_kw in zip(question_str, question_keywords):
    question_value.append({
      'string': q_str.get('#text', ''),
      'language': q_str.get('lang', 'en'),
      'keywords': q_kw.get('#text', '')
    })
  del question['string'], question['keywords']
  question['question'] = question_value
  return question

def monolingual_question(question):
  # Comes as:
  #   'string': 'Who was the wife of President Lincoln?'
  question_value = question['string']
  del question['string']
  question['question'] = [{ 'string': question_value, 'language': 'en'}]
  return question

def maybe_convert_to_json(file, multilingual=True):
  full_basename = os.path.splitext(file)[0]
  json_file_name = full_basename + '.json'
  if file.endswith('xml') and not os.path.exists(json_file_name):
    xml_parsed = xmltodict.parse(open(file, 'r').read(),
        process_namespaces=True, postprocessor=processor)
    questions = xml_parsed['dataset']['question']
    del xml_parsed['dataset']['question']
    xml_parsed['dataset']['id'] = '{}_{}'.format(
      os.path.basename(full_basename), xml_parsed['dataset']['id'])
    process_fn = multilingual_question if multilingual else monolingual_question
    xml_parsed['questions'] = list(filter(lambda q: q is not None,
      map(lambda q: process_fn(q), questions)))
    json.dump(fp=open(json_file_name, 'w'), obj=xml_parsed, ensure_ascii=False)

  else:
    dataset = json.load(open(json_file_name, 'r'))
    dataset['questions'] = list(filter(lambda q: check_keys(q) is not None, dataset['questions']))
    json.dump(fp=open(json_file_name, 'w'), obj=dataset, ensure_ascii=False)

def maybe_download(url, file, multilingual=True):
  if not os.path.exists(file):
    download(url, file)
  maybe_convert_to_json(file, multilingual)

base_url = 'https://raw.githubusercontent.com/ag-sc/QALD/master'
monolingual_indexes = [0, 1]
# 1, 2 are monolingual, processing step is okay
# 3, 4, 5 are multilingual
qald_uris = [
  ('dbpedia-train.xml', False),
  ('dbpedia-train.xml', False),
  ('dbpedia-train.xml', True),
  ('qald-4_multilingual_train.xml', True),
  ('qald-5_train.xml', True),
  ('qald-6-test-multilingual.json', True)
]

lcquad_url = 'https://ndownloader.figshare.com/files/10505914'
lcquad_name = 'LC-QuAD_v1.json'

datasets = []
for index, (qald_uri, multilingual) in enumerate(qald_uris):
  target = index +1
  name = 'QALD_{}{}'.format(target, os.path.splitext(qald_uri)[1])
  url = '{}/{}/data/{}'.format(base_url, target, qald_uri)
  datasets.append((name, url, multilingual))

datasets.append((lcquad_name, lcquad_url, True))

prefix_def = re.compile('PREFIX ([^:]+):\s*<([^>]+)>')
xml_path_subs = {
  'dataset.question.query': correct_sparql_query
}

datasets_dir = os.path.join(os.getcwd(), 'datasets')

if not os.path.exists(datasets_dir):
  os.mkdir(datasets_dir)

# download & process datasets
for dataset in datasets:
  name, url, multilingual = dataset
  file = os.path.join(datasets_dir, name)
  print('{} -> {}'.format(name, url))
  maybe_download(url, file, multilingual=multilingual)

