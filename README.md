Swiss Meds API
==============

Uses [oddb2xml][] to create Swiss drug XML files from various sources, then imports these into Couchbase, which replicates to ElasticSearch.
A **Flask** app runs a web server with an API to retrieve information about medications.
The repo is set up to run the full stack via [Docker][].


## API Calls

### `/search/{term}`

Query all documents for the given search term.
Search is [performed by Elasticsearch][elastic-api-search] and this API endpoint accepts any Elasticsearch query.

### `/suggest/{term}?lang=X`

Suggest terms similar to the term given.
Supported for `lang` currently are **d** and **f**, default is **d**.
Suggestions are [performed by Elasticsearch][elastic-api-suggest].

### `/ean/{ean-13}`

Retrieve all documents (products and articles) for the given EAN-13 code.


## Installation

Use Docker to create a machine and build and start the [couchbase][docker-couchbase] [elasticsearch-couchbase][docker-elasticsearch-couchbase] images.
The latter combines [elasticsearch][] and the [Couchbase Transport Plugin][elasticsearch-couchbase] for Elasticsearch.

```bash
docker-machine create --driver virtualbox smeds
(or: docker-machine start smeds)
eval "$(docker-machine env smeds)"
docker-compose up -d
```

[There are some issues](https://hub.docker.com/r/_/elasticsearch/) when mounting ElasticSearch directories on Mac, below is a way to fix them.

```bash
docker-compose run elastic /bin/bash -c 'usermod -u 1000 elasticsearch; \
gosu elasticsearch elasticsearch'
```

### Setup Couchbase

Now you can login to the Couchbase admin interface and set up the database at [192.168.99.100:8091](http://192.168.99.100:8091).
We'll use a bucket named _default_, you can set the administrator name and password yourself.

### Setup Elasticsearch

To [make Couchbase replicate to Elasticsearch][elasticsearch-couchbase-install], the template is installed, an index named `data` is created and we update our Couchbase's server max concurrent replications.
The former two commands are performed by the Docker build, for reference:

```bash
curl -X PUT http://192.168.99.100:9200/_template/couchbase -d @couchbase_template.json
curl -X PUT http://192.168.99.100:9200/data
```

To change the max number of concurrent replications you can do:

```bash
curl -X POST -u Administrator:password http://192.168.99.100:8091/internalSettings -d xdcrMaxConcurrentReps=8
```

### Configure Replication

1. Go back to the [Couchbase web console](http://192.168.99.100:8091/) and select the **XDCR** tab.
2. Create a cluster reference to the Couchbase-enabled Elasticsearch cluster running at [http://192.168.99.100:9091], username and password for now are fixed at _root_ and _foobar_.
3. Create a replication from this cluster's _default_ bucket to the ES-cluster's _data_ bucket; you must click “Advanced Settings” and choose the v1 transport protocol.

Two Elasticsearch plugins were also installed (_head_ and _kopf_) that allow you to see replication status via browser at [192.168.99.100/_plugins/kopf](http://192.168.99.100/_plugins/kopf) (or .../head).
[Here's][elasticcouchbase-presentation] a presentation introducing the topic.

### Install Python Dependencies

Our import tool runs on Flask and has some dependencies that need to be installed.
The couchbase library needs to have _libcouchbase_ installed, here's how you'd install that on a Mac with Homebrew, adapt accordingly:

```bash
brew install libcouchbase

virtualenv -p python3 env
./env/bin/activate
pip install -r requirements.txt
```

### Create Views

Create a view named `gtin` in design document `gtin` to enable querying for EAN-13 codes.


## Import

When the server is up, run the import:

```bash
. env/bin/activate
./run_import.sh
```

### N1QL

To start the N1QL console:

```bash
docker run -it couchbase /opt/couchbase/bin/cbq \
-engine=http://$(docker-machine ip smeds):8093
```


[oddb2xml]: http://www.ywesee.com/Oddb2xml/Index
[Docker]: https://www.docker.com
[docker-couchbase]: https://hub.docker.com/r/couchbase/server/
[docker-elasticsearch-couchbase]: https://hub.docker.com/r/clakech/elastic-couchbase/
[elastic-api-search]: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-uri-request.html
[elastic-api-suggest]: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html
[elasticsearch-couchbase]: https://github.com/couchbaselabs/elasticsearch-transport-couchbase
[elasticsearch-couchbase-install]: http://developer.couchbase.com/documentation/server/4.1/connectors/elasticsearch-2.1/install-intro.html
[elasticcouchbase-presentation]: http://www.couchbase.com/nosql-resources/presentations/couchbase-server-2.0-full-text-search-integration[3].html
