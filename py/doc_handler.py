#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	2016-02-19	Imported from py-umls


class DocHandler(object):
	""" Superclass for simple database import.
	"""
	
	def __init__(self):
		self.documents = []
	
	def addDocument(self, doc):
		if doc is not None:
			self.documents.append(doc)
	
	def finalize(self):
		pass


class DebugDocHandler(DocHandler):
	""" Simply logs each new document.
	"""
	def addDocument(self, doc):
		print(doc)
	
	def __str__(self):
		return "Debug logger"


class CouchbaseDocHandler(DocHandler):
	""" Handles documents for storage in Couchbase.
	"""
	
	def __init__(self, couch_url=None):
		super().__init__()
		db_host = couch_url if couch_url else 'couchbase://localhost/default'
		
		import couchbase.bucket     # imported here so it's only imported when using Couchbase
		self.cb = couchbase.bucket.Bucket(db_host)
		self.fmt = couchbase.FMT_JSON
	
	def addDocument(self, doc):
		super().addDocument(doc)
		if len(self.documents) > 50:
			self._insertAndClear()
	
	def finalize(self):
		self._insertAndClear()
	
	def _insertAndClear(self):
		if len(self.documents) > 0:
			self.cb.upsert_multi({d['_id']: d for d in self.documents}, format=self.fmt)
			self.documents.clear()
	
	def __str__(self):
		return "Couchbase at {}".format(self.cb)


class MongoDocHandler(DocHandler):
	""" Handles documents for storage in MongoDB.
	"""
	
	def __init__(self, db_host='localhost', db_port=27017, db_name='default', db_bucket='medi', db_user=None, db_pass=None):
		super().__init__()
		import pymongo		# imported here so it's only imported when using Mongo
		conn = pymongo.MongoClient(host=db_host, port=db_port)
		db = conn[db_name]
		
		# authenticate
		if db_user and db_pass:
			db.authenticate(db_user, db_pass)
		
		self.mng = db[db_bucket]
		self.mng.ensure_index('ndc')
		self.mng.ensure_index('label', text=pymongo.TEXT)
	
	def addDocument(self, doc):
		lbl = doc.get('label')
		if lbl and len(lbl) > 1010:			# indexed, cannot be > 1024 in total
			doc['fullLabel'] = lbl
			doc['label'] = lbl[:1010]
		
		super().addDocument(doc)
		if len(self.documents) > 50:
			self._insertAndClear()
	
	def finalize(self):
		self._insertAndClear()
	
	def _insertAndClear(self):
		if len(self.documents) > 0:
			self.mng.insert(self.documents)
			self.documents.clear()
	
	def __str__(self):
		return "MongoDB at {}".format(self.mng)


class CSVHandler(DocHandler):
	""" Handles CSV export. """
	
	def __init__(self):
		super().__init__()
		self.csv_file = 'rxnorm.csv'
		self.csv_handle = open(self.csv_file, 'w')
		self.csv_handle.write("rxcui,tty,ndc,name,va_classes,treating,ingredients\n")
	
	def addDocument(self, doc):
		self.csv_handle.write('{},"{}","{}","{}","{}","{}","{}"{}'.format(
			doc.get('rxcui', '0'),
			doc.get('tty', ''),
			doc.get('ndc', ''),
			doc.get('label', ''),
			';'.join(doc.get('drugClasses') or []),
			';'.join(doc.get('treatmentIntents') or []),
			';'.join(doc.get('ingredients') or []),
			"\n"
		))
	
	def __str__(self):
		return 'CSV file "{}"'.format(self.csv_file)

