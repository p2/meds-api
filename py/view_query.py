#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	2016-02-22	Created by Pascal Pfiffner

import logging
import couchbase


class ViewQuery(object):
	
	def __init__(self, bucket, name_design, name_view):
		self.bucket = bucket
		self.name_design = name_design
		self.name_view = name_view
	
	def iterator(self, keys_from, keys_to=None):
		raise Exception('Abstract class use, use `ViewQuerySingle` or `ViewQueryMulti`')


class ViewQuerySingle(ViewQuery):
	
	def iterator(self, keys_from, keys_to=None):
		if keys_to is not None:
			logging.warning('`ViewQuerySingle` ignores the `keys_to` parameter')
		q = couchbase.views.params.Query(stale=False, inclusive_end=True, mapkey_single=keys_from)
		logging.debug('searching for “{}” in view “{}.{}” with query {}'.format(keys_from, self.name_design, self.name_view, q))
		
		return couchbase.views.iterator.View(self.bucket, self.name_design, self.name_view, query=q, include_docs=True)


class ViewQueryMulti(ViewQuery):
	
	def iterator(self, keys_from, keys_to=None):
		kt = keys_to
		kt.append(couchbase.views.params.Query.STRING_RANGE_END)
		q = couchbase.views.params.Query(stale=False, inclusive_end=True, mapkey_range=[keys_from, kt])
		logging.debug('searching for “{}” - “{}” in view “{}.{}” with query {}'.format(key_from, keys_to, self.name_design, self.name_view, q))
		
		return couchbase.views.iterator.View(self.bucket, self.name_design, self.name_view, query=q, include_docs=True)
