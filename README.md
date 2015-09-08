# CKAN route to PA extension 

Adds TET extenstions to CKAN platform 

## Build instructions 

activate python virtual env 

```sh
. /usr/lib/ckan/default/bin/activate
```

clone git repository

```sh
git@gitlab.insight-centre.org:egov/ckanext-routetopa.git
cd ckanext-routetopa
```

build the plugin

```sh
python setup.py develop
```

enable routetopa plugin 
```sh
python setup.py develop
```

Add 'routetopa' plugin to CKAN config file :
```sh
ckan.plugins = stats text_view recline_view routetopa
```

start ckan
```sh
paster serve /etc/ckan/default/development.ini
```
