#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	2016-02-19	Created by Pascal Pfiffner

import uuid
import logging
import xml.etree.ElementTree as ET

import doc_handler as DH


class ImportableFile(object):
	""" Base class for files to import.
	"""
	def __init__(self, filepath):
		self.path = filepath
	
	def handle_documents(self, doc_handler):
		logging.error("{} cannot handle documents".format(self))
	
	def __str__(self):
		return "{} at {}".format(self.__class__, self.path)


class ImportableXMLFile(ImportableFile):
	
	@classmethod
	def node_to_json(cls, node, rm_ns=None):
		js = {}
		for key, val in node.attrib.items():
			js[key.lower()] = val
		txt = node.text.strip() if node.text else ''
		for child in node:
			leaf = cls.node_to_json(child, rm_ns=rm_ns)
			if leaf is not None and len(leaf) > 0:
				tag = child.tag.lower()
				if rm_ns and len(rm_ns) > 0:
					for ns in rm_ns:
						tag = tag.replace(ns, '')
				js[tag] = leaf
			if child.tail:
				txt += child.tail.strip()
		
		if len(js) > 0:
			if txt:
				js['_txt'] = txt
			return js
		return txt


class ImportableArticleFile(ImportableXMLFile):
	
	def handle_documents(self, doc_handler):
		for evt, node in ET.iterparse(self.path, events=('end',)):
			if 'end' != evt:
				continue
			if 'ART' == node.tag[-3:]:
				doc = self.__class__.node_to_json(node, rm_ns=['{http://wiki.oddb.org/wiki.php?pagename=swissmedic.datendeklaration}'])
				if doc is not None:
					del doc['sha256']             # we don't need this one
					gtin = doc.get('artbar', {}).get('bc', uuid.uuid4())
					doc['_id'] = 'article-{}'.format(gtin)
					doc['type'] = 'article'
					doc_handler.addDocument(doc)
			else:
				logging.debug("Skipping <{}>".format(node.tag))
