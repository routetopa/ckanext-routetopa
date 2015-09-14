import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from logging import getLogger
from ckan.plugins.toolkit import Invalid
from ckan.lib.base import BaseController
from ckan.common import json, response
import os

log = getLogger(__name__)

#Validators
def check_license(value):
    if value == "notspecified":
    	raise Invalid('Select a valid license');
    return value

def check_tags(value):
    if type(value) is unicode and len(value.split(",")) < 3:
    	raise Invalid('Provide at least three tags for the dataset');
    return value

class RoutetopaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'routetopa')

    # IValidator
    def get_validators(self):
    	return {'check_license': check_license, 'check_tags': check_tags }

    # IRoutes
    @staticmethod
    def after_map(m):
         m.connect('getschema', '/api/3/util/tet/getschema',
            controller='ckanext.routetopa.plugin:RtpaApi', action='get_schema')
         return m

class RtpaApi(BaseController):
    def get_schema(self):
        response.content_type = 'application/json; charset=UTF-8'
        path = os.path.dirname(__file__)
        with open( path + '/tet_dataset.json') as json_file:
            json_data = json.load(json_file)
        return json.dumps(json_data)
