# CKAN route to PA extension 

Adds TET extenstions to CKAN platform 

## Prerequisites

* Install lastest version of CKAN 
* Install [CKAN scheming plugin](https://github.com/open-data/ckanext-scheming)

## Build instructions 

activate python virtual env 

```sh
. /usr/lib/ckan/default/bin/activate
```

clone git repository

```sh
git clone https://github.com/routetopa/ckanext-routetopa.git
cd ckanext-routetopa
```

add following lines in 'fields' section of '/etc/solr/conf/schema.xml'

```xml
<field name="target_audience" type="text" indexed="true" stored="true" />
<field name="category" type="text" indexed="true" stored="true" />
```

retstart solar

```sh
sudo service jetty restart
```

build the plugin

```sh
python setup.py develop
```

add following line to CKAN config file :

```sh
scheming.dataset_schemas = ckanext.routetopa:tet_dataset.json
```

Add 'routetopa' plugin to CKAN config file :
```sh
ckan.plugins = stats text_view recline_view scheming_datasets routetopa
```

start ckan
```sh
paster serve /etc/ckan/default/development.ini
```

License
-------------------

The code licensed under the GNU Affero General Public License (AGPL) v3.0

Dvelopment of TET extenstion is supported by European Commision through the [ROUTE-TO-PA project](http://routetopa.eu/) 
