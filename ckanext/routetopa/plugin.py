import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from logging import getLogger
from ckan.plugins.toolkit import Invalid
from ckan.lib.base import BaseController
from ckan.common import json, response, request
import ckan.model as model
import os
from ckan.lib.base import c, g, h

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
    results = {}
    config = json_data
    for item in config.keys():
        results[item] = {}
        for tag_name in config[item]:
            try:
                tag_count = len(model.Tag.get(tag_name).packages)
            except Exception:
                tag_count = 0
            results[item][tag_name] = tag_count
    return results

def get_recommended_datasets(pkg_id):
    log.debug("PKG_ID:"+pkg_id)
    log.debug("type of:"+str(type(pkg_id)))
    package = toolkit.get_action('package_show')(None, {'id': pkg_id.strip()})
    response_data  = {}
    if "linked_datasets" in package and package["linked_datasets"] != "":
        l = []
        pkgs = package["linked_datasets"].split(",")
        for pkg in pkgs:
            log.debug("PKG_ID:"+pkg_id)
            log.debug("type of:"+str(type(pkg_id)))
            p = toolkit.get_action('package_show')(None, {'id': pkg})
            item = {}
            item ["name"] = pkg
            item ["title"] = p["title"]
            item ["notes"] = p["notes"]
            l.append(item)
            response_data["datasets"] = l
    else:
        q= ''
        if "category" in package and not package["category"] == "" : q += "category:\"" + package["category"] + "\"~25"
        if len(q) > 0  : q += " OR " 
        if "target_audience" in package and not package["target_audience"] == "" : q += "target_audience:\"" + package["target_audience"] + "\"~25"
        data_dict = {
            'qf':'target_audience^4 category^4 name^4 title^4 tags^2 groups^2 text',
            'q': q,
            'rows': 5
        }
        log.debug(q)
        response_data["datasets"] = toolkit.get_action('package_search')(None, data_dict)["results"]
        for ds in response_data["datasets"]:
            if ds["name"] == pkg_id:
                response_data["datasets"].remove(ds)
    return response_data

def get_recommended_datasets_for_user():
    q = "" 
    dataset_dict  = {}
    if c.user:
        extra_data = {}
        try:
            user_data = json.loads(toolkit.get_action('user_show')({}, {'id': c.user})["about"])
            extra_data["role"] = user_data["role"]
            extra_data["category"] = user_data["category"]
        except Exception:
            extra_data["role"] = ""
            extra_data["category"] = ""
        if not extra_data["category"] == "" : q += extra_data["category"] + ' '
        if not extra_data["role"] == "" : q += extra_data["role"] + ' '
    data_dict = {
       'qf':'target_audience^4 category^4 name^4 title^4 tags^2 groups^2 text',
       'q': q,
       'rows': 5
    }
    return toolkit.get_action('package_search')(None, data_dict)

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
    def before_map(m):
        m.connect('/user/register',
            controller='ckanext.routetopa.controller:CustomUserController',
            action='register')
        m.connect('/user/edit',
            controller='ckanext.routetopa.controller:CustomUserController',
            action='edit')
        m.connect('/user/edit/{id:.*}',
            controller='ckanext.routetopa.controller:CustomUserController',
            action='edit')
        return m

    @staticmethod
    def after_map(m):
         m.connect('getschema', '/api/3/util/tet/getschema',
            controller='ckanext.routetopa.plugin:RtpaApi', action='get_schema')
         m.connect('getroles', '/api/3/util/tet/getconfig',
            controller='ckanext.routetopa.plugin:RtpaApi', action='get_configuration')
         m.connect('autocomplete', '/api/3/util/tet/autocomplete',
            controller='ckanext.routetopa.plugin:RtpaApi', action='autocomplete')
         return m

    #IPackageController
    def before_search(self, search_params):
        if c.user and "personalized" in request.params:
            extra_data = {}
            try:
                user_data = json.loads(toolkit.get_action('user_show')({}, {'id': c.user})["about"])
                extra_data["role"] = user_data["role"]
                extra_data["category"] = user_data["category"]
            except Exception:
                extra_data["role"] = ""
                extra_data["category"] = ""

        if "q" in search_params.keys() and search_params["q"].startswith("role::"):
            role = search_params["q"].replace("role::","")
            search_params["q"] = role 
            search_params["qf"] = "target_audience"
        if "q" in search_params.keys() and search_params["q"].startswith("category::"):
            category = search_params["q"].replace("category::","")
            search_params["q"] = category
            search_params["qf"] = "category"
        try:
            if not search_params["q"]: search_params["q"]  = ""
            search_params["qf"] = "target_audience^4 category^4 name^4 title^4 tags^2 groups^2 text"
            if not extra_data["category"] == "" : search_params["q"] += extra_data["category"] + ' '
            if not extra_data["role"] == "" : search_params["q"] += extra_data["role"] + ' '
            log.debug(search_params)
        except Exception:
            log.info("Peronalized search failed.")
        return search_params

    def before_index(self, pkg_dict):
        return pkg_dict

    #ITemplateHelpers
    def get_helpers(self):
        return {'get_config': get_config, 
                'get_req_usr': get_recommended_datasets_for_user,
                'get_req': get_recommended_datasets }

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

    def get_configuration(self):
        response.content_type = 'application/json; charset=UTF-8'
        return json.dumps(get_config())

    def autocomplete(self):
        response.content_type = 'application/json; charset=UTF-8'
        q = request.params["incomplete"]
        s = request.params["s"]
        roles = get_config()[s]
        data = {"ResultSet" : {}}
        data["ResultSet"] ["Result"] = [role for role in roles if (q.lower() in role.lower())]
        return json.dumps(data)



