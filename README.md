Swiss Meds API
==============

Uses [oddb2xml]() to create Swiss drug XML files from various sources, then imports these into a NoSQL database.
The repo is set up to create a Docker image with Couchbase and import all data into the Docker-controller Couchbase instance.

Info on oddb2xml data: <http://www.ywesee.com/Oddb2xml/Bemerkungen>


## API Calls

### `/ean/{ean-13}`

Retrieve all documents (products and articles) for the given EAN-13 code.


## Installation


### Run Import

```bash
docker-machine create --driver virtualbox smeds
docker-machine start smeds
eval "$(docker-machine env smeds)"
docker-compose up -d
```

Now you can login to the Couchbase admin interface and set up the database at [192.168.99.100:8091](http://192.168.99.100:8091).
When the server is up, run the import:

```bash
brew install libcouchbase

virtualenv -p python3 env
./env/bin/activate
pip install couchbase

./run_import.sh
```

### N1QL

To start the N1QL console:

```bash
docker run -it couchbase /opt/couchbase/bin/cbq \
-engine=http://$(docker-machine ip smeds):8093
```
