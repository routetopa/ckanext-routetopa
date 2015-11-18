import sys
from ckan.lib.base import request
from pylons import config
from ckan.lib.base import c, g, h
from ckan.lib.base import model
from ckan.lib.base import render
from ckan.lib.base import _
from ckan.lib.navl.validators import not_empty
from ckan.controllers.user import UserController
from logging import getLogger
from ckan.common import json
from ckan.common import request, response
import ckan.lib.base as base
import ckan.logic as logic
import ckan.lib.captcha as captcha
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.authz as authz

log = getLogger(__name__)
unflatten = dictization_functions.unflatten
abort = base.abort
render = base.render
DataError = dictization_functions.DataError
check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
UsernamePasswordError = logic.UsernamePasswordError

class CustomUserController(UserController):
    """This custom user controller for CKAN, its used to add more details to 
    ckan user profile using the "about" field  
    """

    new_user_form = 'user/new_user_form.html'
    edit_user_form = 'user/edit_user_form.html'

    def _save_new(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')

            json_data = {}
            json_data["role"] = data_dict["role"]
            json_data["category"] = data_dict["category"]
            data_dict["about"]= json.dumps(json_data)
            
            captcha.check_recaptcha(request)
            user = get_action('user_create')(context, data_dict)
            
        except NotAuthorized:
            abort(401, _('Unauthorized to create user %s') % '')
        except NotFound, e:
            abort(404, _('User not found'))
        except DataError:
            abort(400, _(u'Integrity Error'))
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.new(data_dict)
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)
        if not c.user:
            rememberer = request.environ['repoze.who.plugins']['friendlyform']
            identity = {'repoze.who.userid': data_dict['name']}
            response.headerlist += rememberer.remember(request.environ,
                                                       identity)
            h.redirect_to(controller='user', action='me', __ckan_no_root=True)
        else:
            h.flash_success(_('User "%s" is now registered but you are still '
                            'logged in as "%s" from before') %
                            (data_dict['name'], c.user))
            return render('user/logout_first.html')

    def _save_edit(self, id, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            
            json_data = {}
            json_data["role"] = data_dict["role"]
            json_data["category"] = data_dict["category"]
            data_dict["about"]= json.dumps(json_data)

            context['message'] = data_dict.get('log_message', '')
            data_dict['id'] = id
            if data_dict['password1'] and data_dict['password2']:
                identity = {'login': c.user,
                            'password': data_dict['old_password']}
                auth = authenticator.UsernamePasswordAuthenticator()

                if auth.authenticate(request.environ, identity) != c.user:
                    raise UsernamePasswordError

            if 'activity_streams_email_notifications' not in data_dict:
                data_dict['activity_streams_email_notifications'] = False

            user = get_action('user_update')(context, data_dict)
            h.flash_success(_('Profile updated'))
            h.redirect_to(controller='user', action='read', id=user['name'])
        except NotAuthorized:
            abort(401, _('Unauthorized to edit user %s') % id)
        except NotFound, e:
            abort(404, _('User not found'))
        except DataError:
            abort(400, _(u'Integrity Error'))
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.edit(id, data_dict, errors, error_summary)
        except UsernamePasswordError:
            errors = {'oldpassword': [_('Password entered was incorrect')]}
            error_summary = {_('Old Password'): _('incorrect password')}
            return self.edit(id, data_dict, errors, error_summary)

    def edit(self, id=None, data=None, errors=None, error_summary=None):
        context = {'save': 'save' in request.params,
                   'schema': self._edit_form_to_db_schema(),
                   'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj
                   }
        if id is None:
            if c.userobj:
                id = c.userobj.id
            else:
                abort(400, _('No user specified'))
        data_dict = {'id': id}

        try:
            check_access('user_update', context, data_dict)
        except NotAuthorized:
            abort(401, _('Unauthorized to edit a user.'))

        if (context['save']) and not data:
            return self._save_edit(id, context)

        try:
            old_data = get_action('user_show')(context, data_dict)
            extra_data = {}
            try:
                extra_data = json.loads(old_data["about"])
            except Exception:
                extra_data["role"] = ""
                extra_data["category"] = ""

            old_data["role"] = extra_data["role"]
            old_data["category"] = extra_data["category"]
            schema = self._db_to_edit_form_schema()
            if schema:
                old_data, errors = \
                    dictization_functions.validate(old_data, schema, context)

            c.display_name = old_data.get('display_name')
            c.user_name = old_data.get('name')
            log.debug(old_data)
            data = data or old_data

        except NotAuthorized:
            abort(401, _('Unauthorized to edit user %s') % '')
        except NotFound:
            abort(404, _('User not found'))

        user_obj = context.get('user_obj')

        if not (authz.is_sysadmin(c.user)
                or c.user == user_obj.name):
            abort(401, _('User %s not authorized to edit %s') %
                  (str(c.user), id))

        errors = errors or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        self._setup_template_variables({'model': model,
                                        'session': model.Session,
                                        'user': c.user or c.author},
                                       data_dict)

        c.is_myself = True
        c.show_email_notifications = h.asbool(
            config.get('ckan.activity_streams_email_notifications'))
        c.form = render(self.edit_user_form, extra_vars=vars)

        return render('user/edit.html')

    def _add_to_schema(self, schema):     
        schema['role'] = [unicode]
        schema['category'] = [unicode]
        schema['twitter'] = [unicode]

    def _new_form_to_db_schema(self):
        schema = super(CustomUserController, self)._new_form_to_db_schema()
        self._add_to_schema(schema)
        return schema

    def _edit_form_to_db_schema(self):
        schema = super(CustomUserController, self)._edit_form_to_db_schema()
        self._add_to_schema(schema)
        return schema

