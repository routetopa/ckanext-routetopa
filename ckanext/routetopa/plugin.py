import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from logging import getLogger
from ckan.plugins.toolkit import Invalid

log = getLogger(__name__)

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
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'routetopa')
    def get_validators(self):
    	return {'check_license': check_license, 'check_tags': check_tags }
    
