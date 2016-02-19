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
				tag = child.tag
				if rm_ns and len(rm_ns) > 0:
					for ns in rm_ns:
						tag = tag.replace('{'+ns+'}', '')
				js[tag.lower()] = leaf
			if child.tail:
				txt += child.tail.strip()
		
		if len(js) > 0:
			if txt:
				js['_txt'] = txt
			return js
		return txt


class ImportableODDB2XMLFile(ImportableXMLFile):
	tag = None
	tag_ns = 'http://wiki.oddb.org/wiki.php?pagename=Swissmedic.Datendeklaration'
	
	def handle_documents(self, doc_handler):
		k = self.__class__
		if not k.tag:
			raise Exception("Class must define which tag to iterate over")
		
		full_tag = '{{{}}}{}'.format(k.tag_ns, k.tag) if k.tag_ns else k.tag
		result_tag = '{{{}}}RESULT'.format(k.tag_ns) if k.tag_ns else 'RESULT'
		num_found = 0
		num_expect = None
		
		for evt, node in ET.iterparse(self.path, events=('end',)):
			if 'end' != evt:
				continue
			
			# found the tag we're interested in
			if full_tag == node.tag:
				num_found += 1
				doc = k.node_to_json(node, rm_ns=[k.tag_ns])
				doc = self.clean_document(doc)
				if doc is not None:
					doc_handler.addDocument(doc)
			
			# <RESULT> usually appears at the end of the XML
			elif result_tag == node.tag:
				rec = node.find('NBR_RECORD')
				if rec and rec.text:
					num_expect = int(rec.text)
			else:
				logging.debug("Skipping <{}>".format(node.tag))
		
		doc_handler.finalize()
		
		# validate
		if num_expect is not None and num_expect != num_found:
			raise Exception("Expect {} nodes but found {}"
				.format(num_expect, num_found))
	
	def clean_document(self, doc):
		return doc


class ImportableArticleFile(ImportableODDB2XMLFile):
	tag = 'ART'
	
	def clean_document(self, doc):
		if doc is not None:
			del doc['sha256']             # we don't need this one
			gtin = doc.get('artbar', {}).get('bc', uuid.uuid4())
			doc['_id'] = 'article-{}'.format(gtin)
			doc['type'] = 'article'
		return doc


class ImportableProductFile(ImportableODDB2XMLFile):
	tag = 'PRD'
	
	def clean_document(self, doc):
		if doc is not None:
			del doc['sha256']             # we don't need this one
			gtin = doc.get('gtin', uuid.uuid4())
			doc['_id'] = 'product-{}'.format(gtin)
			doc['type'] = 'product'
		return doc


class ImportableInteractionFile(ImportableODDB2XMLFile):
	tag = 'IX'
	
	def clean_document(self, doc):
		if doc is not None:
			del doc['sha256']             # we don't need this one
			ixno = doc.get('ixno', uuid.uuid4())
			doc['_id'] = 'interact-{}'.format(ixno)
			doc['type'] = 'interact'
		return doc


class ImportableSubstanceFile(ImportableODDB2XMLFile):
	tag = 'SB'
	
	def clean_document(self, doc):
		if doc is not None:
			del doc['sha256']             # we don't need this one
			subno = doc.get('subno', uuid.uuid4())
			doc['_id'] = 'substance-{}'.format(subno)
			doc['type'] = 'substance'
		return doc


class ImportableLimitationFile(ImportableODDB2XMLFile):
	tag = 'LIM'
	
	def clean_document(self, doc):
		if doc is not None:
			del doc['sha256']             # we don't need this one
			doc['_id'] = 'limitation-{}'.format(uuid.uuid4())
			doc['type'] = 'limitation'
		return doc

