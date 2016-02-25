#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
import couchbase


class ElasticHost(object):
	
	def __init__(self, host):
		if host is None or len(host) < 13:
			raise Exception("You must provide the host URL, including index name")
		self.host = host
	
	def search(self, query, couch, max_hits=100):
		if not query:
			raise Exception("No query provided")
		if not isinstance(couch, couchbase.bucket.Bucket):
			raise Exception("Must provide a couchbase Bucket instance, provided {}"
				.format(couch))
		url = "{}/_search".format(self.host)
		ret = requests.get(url, params={'q': query, '_source': False, 'size': max_hits-1})
		ret.raise_for_status()
		data = ret.json()
		
		# request documents from Couchbase (hits are sorted by score)
		hits = data.get('hits', {}).get('hits', [])
		if len(hits) > 0:
			ids = [d['_id'] for d in hits]
			docs = [v.value for k, v in couch.get_multi(ids).items()]
		else:
			docs = []
		
		return docs, {
			'timed_out': data['timed_out'],
			'max_score': data['hits']['max_score'],
			'total': data['hits']['total'],
		}
	
	def suggest(self, term, lang=None):
		if not term:
			raise Exception("No term provided")
		url = "{}/_suggest".format(self.host)
		
		lang = lang[:2]
		lang = 'de' if lang not in ['de', 'fr'] else lang
		field = 'doc.dscrd' if 'de' == lang else 'doc.dscrf'
		query = {
			'text': term,
			'suggestion': {
				'term': {
					'field' : field,
				},
			},
		}
		
		ret = requests.post(url, json=query)
		ret.raise_for_status()
		data = ret.json()
		suggestions = []
		for sd in data.get('suggestion', []):
			[suggestions.append(opt) for opt in sd.get('options', [])]
		
		return suggestions, {'lang': lang}
	
	def hit_documents(self, hits):
		return hits
		docs = []
		for hit in hits:
			score = hit.get('_score')
			hitdoc = hit.get('_source', {}).get('doc')
			docs.append((score, hitdoc))
		return docs
		
		
