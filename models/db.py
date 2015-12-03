import stageofdevelopment
import pydoc
from gluon import current # current.auth nodig voor  dc_py_lib

textrepr = pydoc.TextRepr()
textrepr.maxstring = textrepr.maxother = 1000
pydoc.text.repr = textrepr.repr
USE_CAS = False

# load the SoD, making it global for use. 
sod = stageofdevelopment.load(stageofdevelopment.find_and_read_sod_file(request.folder))
# or, if you have very specific needs and can validate on another hostname
# sod = stageofdevelopment.load('PRD' if 'wachtwoord.drenthecollege.nl' in request.env.server_name  else 'ONT')


#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    if sod.production: 
        dburi = 'sqlite://database.sqlite'
        db = DAL(dburi,pool_size=0,check_reserved=['all'],
                fake_migrate = False,migrate_enabled=False) 
    else: 
        dburi = 'sqlite://database.sqlite'
        db = DAL(dburi,pool_size=0,check_reserved=['all'],
                fake_migrate = False,migrate_enabled=True)
    # FreeTDS requirement: 
    #db.executesql('set quoted_identifier on')
    # sql server requirement
    #for key in ['reference','reference FK']:
        #t = db._adapter.types
        #t[key]=t[key].replace('%(on_delete_action)s','NO ACTION')

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate


if USE_CAS: 
    auth = Auth(db,cas_provider = 'your_cas_uri_here')
    ## create all tables needed by auth if not custom tables
    auth.define_tables(username=True, signature=False)
    auth.settings.update_fields = ['first_name','last_name','email']
else:
    auth = Auth(db)
    ## create all tables needed by auth if not custom tables
    auth.define_tables(username=True, signature=False)
    # don't update fields, since we're not using cas. 
# save current auth for dc_py_lib
current.auth = auth

crud, service, plugins = Crud(db), Service(), PluginManager()

## configure email
#http://www.web2py.com/book/default/chapter/08#Simple-text-email
mail = auth.settings.mailer
mail.settings.server = 'logging'
mail.settings.sender = 'noreply@example.com'
mail.settings.login = None
mail.settings.tls = False # deze moest ik toevoegen

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
import datetime

db.define_table("redirects",
    Field("slug",comment="leeg is default redirect, ook voor niet gevonden"),
    Field("redirect_to",
        label = "Destination",
        requires = IS_URL()),
    Field("redirect_method","integer",
        requires = IS_IN_SET({301:'Permanent',303:'Default',307:'Temporary'}),
        label = "Method",
        default = 303),
    Field("client_side","boolean",
        label = "Client side", 
        comment = "Ajax support may require this"),
    Field("active_from","date",default=request.now),
    Field("active_to","date",default=datetime.datetime(2100,1,1)),
    Field("note","text")
)
