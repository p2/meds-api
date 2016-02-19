#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	2016-02-19	Created by Pascal Pfiffner

import os
import sys
import signal
import logging
import xml.etree.ElementTree as ET

import importable_file as IF
import doc_handler as DH


def doRunImport(files, doc_handler):
	""" Run the actual linking.
	
	:param files: A list of Tuples (filename, ImportableClass)
	:param doc_handler: A :class:`DocHandler` subclass which will handle the
	documents, for example store them to Couchbase with CouchbaseDocHandler.
	These classes are defined in `doc_handler.py`.
	"""
	if doc_handler is None or not isinstance(doc_handler, DH.DocHandler):
		raise Exception("Must specify a `DocHandler`, but got {}".format(doc_handler))
	
	# install keyboard interrupt handler
	def signal_handler(signal, frame):
		print("\nx>  Aborted")
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	
	print('->  Processing to {}'.format(doc_handler))
	
	# run files
	for filepath, fileclass in files:
		print('-->  Processing {} from {}'.format(filepath, fileclass))
		file = fileclass(filepath)
		file.handle_documents(doc_handler)
	
	doc_handler.finalize()
	
	print('->  Done')


def runImport(files, handler_type=None):
	""" Create the desired handler and run import.
	"""
	if handler_type is not None and len(handler_type) > 0:
		
		try:
			if 'mongo' == handler_type:
				db_host = os.environ.get('MONGO_HOST', 'localhost')
				db_port = int(os.environ.get('MONGO_PORT', '27017'))
				db_name = os.environ.get('MONGO_DB', 'default')
				db_bucket = os.environ.get('MONGO_BUCKET')
				db_user = os.environ.get('MONGO_USER')
				db_pass = os.environ.get('MONGO_PASS')
				handler = DH.MongoDocHandler(db_host=db_host, db_port=db_port, db_name=db_name, db_bucket=db_bucket, db_user=db_user, db_pass=db_pass)
			elif 'couch' == handler_type:
				couch_url = os.environ.get('COUCH_URL')
				handler = DH.CouchbaseDocHandler(couch_url=couch_url)
			elif 'csv' == handler_type:
				handler = DH.CSVHandler()
			# elif 'sqlite' == handler_type:
				# handler = SQLiteDocHandler()
			else:
				raise Exception('Unsupported handler type: {}'.format(handler_type))
		except Exception as e:
			logging.error(e)
			sys.exit(1)
	else:
		logging.warn('''  Running linking without document handler, meaning no document will be stored.
               Adjust and run `run_import.sh` for more control.''')
		handler = DH.DebugDocHandler()
	
	doRunImport(files, doc_handler=handler)


if '__main__' == __name__:
	logging.basicConfig(level=logging.INFO)
	
	cmd_arg = sys.argv[1] if len(sys.argv) > 1 else None
	handler_type = os.environ.get('HANDLER_TYPE') or cmd_arg
	
	# hardcode the files to import
	files = [
		('oddb2xml/oddb_article.xml', IF.ImportableArticleFile),
	]
	runImport(files, handler_type)
