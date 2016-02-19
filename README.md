Swiss Meds API
==============

Uses [oddb2xml]() to create Swiss drug XML files from various sources, then imports these into a NoSQL database.
The repo is set up to create a Docker image with Couchbase and import all data into the Docker-controller Couchbase instance.

Info on oddb2xml data: <http://www.ywesee.com/Oddb2xml/Bemerkungen>


### Run Import

```bash
docker-machine create --driver virtualbox smeds
docker-machine start smeds
eval "$(docker-machine env smeds)"
docker-compose up -d

brew install libcouchbase

virtualenv -p python3 env
./env/bin/activate
pip install couchbase

./run_import.sh
```
