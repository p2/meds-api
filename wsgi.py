#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import couchbase.bucket
import py.view_query as view_query

from flask import Flask, request, abort, redirect, jsonify, send_from_directory


app = Flask(__name__)
version = '0.0.1'
couch_host = 'couchbase://192.168.99.100/default'
couch_connection = couchbase.bucket.Bucket(couch_host)


@app.route('/')
def index():
	return jsonify(service="up", version=version)

@app.route('/ean/<ean>')
def query_ean(ean=None):
	if ean:
		try:
			view = view_query.ViewQuerySingle(couch_connection, 'gtin', 'gtin')			
			docs = []
			for result in view.iterator(ean):
				docs.append(result.doc.value)
			return jsonify(status='ok', data=docs)
		except Exception as e:
			logging.error("Exception in `query_ean()`: {}".format(e))
			return abort(500, "Error")
	return abort(400, "No EAN-13 code specified")


# if starting directly, put into debug mode
if '__main__' == __name__:
	logging.basicConfig(level=logging.DEBUG)
	app.run(debug=True, port=8000)
