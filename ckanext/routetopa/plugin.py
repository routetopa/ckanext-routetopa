import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from logging import getLogger
from ckan.plugins.toolkit import Invalid
from ckan.lib.base import BaseController
from ckan.common import json, response, request
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

#Helper function
def get_config():
    path = os.path.dirname(__file__)
    with open( path + '/config.json') as json_file:
        json_data = json.load(json_file)
    return json_data

class RoutetopaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

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
         m.connect('getroles', '/api/3/util/tet/getroles',
            controller='ckanext.routetopa.plugin:RtpaApi', action='get_roles')
         m.connect('autocomplete', '/api/3/util/tet/autocomplete',
            controller='ckanext.routetopa.plugin:RtpaApi', action='autocomplete')
         return m

    #IPackageController
    def before_search(self, search_params):
        if "q" in search_params.keys() and search_params["q"].startswith("role::"):
            role = search_params["q"].replace("role::","")
            search_params["q"] = role
        return search_params

    #ITemplateHelpers
    def get_helpers(self):
        return {'get_config': get_config}

class RtpaApi(BaseController):
    def get_schema(self):
        response.content_type = 'application/json; charset=UTF-8'
        path = os.path.dirname(__file__)
        with open( path + '/tet_dataset.json') as json_file:
            json_data = json.load(json_file)
        res = {}
        for item in json_data["dataset_fields"]:
            resitem = {}
            if "required" in item.keys():
                resitem["required"] = item["required"]
            if "validators" in item.keys():
                resitem["validators"] = item["validators"]
            res["field-" + item["field_name"]] = resitem
        return json.dumps(res)

    def get_roles(self):
        response.content_type = 'application/json; charset=UTF-8'
        return json.dumps(get_config()["roles"])

    def autocomplete(self):
        response.content_type = 'application/json; charset=UTF-8'
        q = request.params["incomplete"]
        roles = get_config()["roles"]
        data = {"ResultSet" : {}}
        data["ResultSet"] ["Result"] = [role for role in roles if (q.lower() in role.lower())]
        return json.dumps(data)



