#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import couchbase.bucket
import py.view_query as view_query
import py.elasticsearch as elasticsearch
from defaults import *
try:
	from settings import *
except:
	pass

from flask import Flask, request, abort, redirect, jsonify, send_from_directory


app = Flask(__name__)
version = '0.0.1'
couch = couchbase.bucket.Bucket(couch_host)
elastic = elasticsearch.ElasticHost(elastic_host)


@app.route('/')
def index():
	return jsonify(service="up", version=version)

@app.route('/search/')
@app.route('/search/<query>')
def api_query(query=None):
	if query:
		try:
			data, extra = elastic.search(query, couch=couch)
			return jsonify(status='ok', data=data, **extra)
		except Exception as e:
			logging.error("Exception in `api_query()`: {}".format(e))
			return abort500()
	return abort400("Please supply a query term like so: `/search/{term}`")

@app.route('/suggest/<term>')
def api_suggest(term=None):
	if term:
		try:
			data, extra = elastic.suggest(term, lang=request.args.get('lang'))
			return jsonify(status='ok', data=data, **extra)
		except Exception as e:
			logging.error("Exception in `api_suggest()`: {}".format(e))
			return abort500()
	return abort400("Please supply a term like so: `/suggest/{term}`")

@app.route('/ean/<ean>')
def api_ean(ean=None):
	if ean:
		try:
			view = view_query.ViewQuerySingle(couch, 'gtin', 'gtin')			
			docs = []
			for result in view.iterator(ean):
				docs.append(result.doc.value)
			return jsonify(status='ok', data=docs)
		except Exception as e:
			logging.error("Exception in `api_ean()`: {}".format(e))
			return abort500()
	return abort400("No EAN-13 code specified")


# handlers
def abort400(msg):
	return jsonify(status='Bad Request', message=msg), 400

def abort500():
	return jsonify(status='Server Error'), 500

@app.errorhandler(404)
def page_not_found(e):
	return jsonify(status='Not Found'), 404


# if starting directly, put into debug mode
if '__main__' == __name__:
	logging.basicConfig(level=logging.DEBUG)
	app.run(debug=True, port=8000)
