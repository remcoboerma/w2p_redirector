# -*- coding: utf-8 -*-
__author__ = 'remco'
#
# © Copyright 2013 Dutveul
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains
# the property of Dutveul and its suppliers, if any.  The intellectual
# and technical concepts contained herein are proprietary to Dutveul and
# its suppliers and may be covered by Dutch and Foreign Patents, patents
# in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from Dutveul.
# http://www.dutveul.nl
#

## version/build: 20150729.1342
from gluon import current
import re, os, platform, os.path, functools


# http://web2py.com/book/default/chapter/04 - Accessing the API from Python modules

def memoize(obj):
    # https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        return cache.setdefault(key, obj(*args, **kwargs))

    return memoizer


class SoD(object):
    """
    State of Development support class. 
    Use .load('PRD') to load the class from request.vars.sod or
    if not available try to keep it alive from the session, or 
    if not available create a new one defaulting to the given parameter
    or 'PRD' if not given.
    
    available are: 
    .ont, .tst, .uat, .prd, .fak 
        booleans
    .stage 
        the first 3 characters from the sodstring. 
    .develop 
        boolean (ont|tst)
    .test 
        boolean (ont|tst|uat)
    .production 
        boolean (uat|prd)
    .fake 
        boolean (fak)
    
    Access the json payload through the keys in the payload, it is 
    automatically converted to python and ready to be read using
    .<jsonkeyname>
    /!\ write-access is not iplemented
    
    Convert to string using the str function to retreive the 
    original sodstring used to construct the sod. 
    
    """

    def __init__(self, sodstring):
        # set defaults
        self.ont = False;
        self.tst = False
        self.uat = False;
        self.prd = False;
        self.fak = False
        self._as_string = sodstring  # store for quick retrieval
        # set the right booleans
        self.stage = sodstring[0:3]  # first 3 chars
        assert self.stage in ('ONT', 'TST', 'UAT', 'PRD', 'FAK')
        setattr(self, self.stage.lower(), True)
        self.develop = self.ont or self.tst
        self.test = self.ont or self.tst or self.uat
        self.production = self.uat or self.prd
        self.fake = self.fak

        if len(sodstring) > 3:
            import json
            self.payload = json.loads(sodstring[3:])
        else:
            self.payload = {}

    def __str__(self):
        return self._as_string

    def __getattr__(self, name):
        # we don't have this as our own property, so we can fake it
        return self.payload.get(name, None)

    def __getstate__(self):
        # allow pickling to save in session store
        return self.__dict__

    def __setstate__(self, dict):
        # allow unpickling to load from the session store
        self.__dict__.update(dict)


import copy_reg


def pickle_SoD(s):
    return SoD, (str(s),)


copy_reg.pickle(SoD, pickle_SoD)


def find_uplevel_file(path, filename):
    """
    >>> find_uplevel_file('c:/users/4388/desktop/web2py','noflex.txt')
    'c:\\noflex.txt'

    :param path: path to start search in
    :param filename: filename to search for (exact match)
    :return: full filepath of the found file or None
    """
    up = path
    while up:
        path = os.path.abspath(path)
        up = os.path.split(path)[0]
        if up == path:
            return None
        path = up
        fullname = os.path.join(path, filename)
        if os.path.exists(fullname):
            return fullname


@memoize
def find_and_read_sod_file(path, filename='sod.flag'):
    """
    print find_and_read_sod_file('c:/users/4388/desktop/web2py',default='PRD')
    :param path: path to start search at
    :type path: string
    :param filename: filename to search for (exact match)
    :type filename: string
    :return: return contents of the found file or None
    :type return: string or None
    """
    uplevel_file = find_uplevel_file(path, filename)
    if uplevel_file:
        f = open(uplevel_file, 'r')
        content = f.read().strip()
        f.close()
        return content
    else:
        return None


def load(default='PRD'):
    """
    Load the SoD into current.session.sod from:
      1. the current web requests variables
      2. the current session
    or if not available create a new sod based on:
      1. rpc hostname (requested hostname matching the rpc_hostname_or regexp)
      2. the hostname of the machine matching the rpc_hostname regexp
      3. the environment variable SOD
         bash: sod=PRD python web2py.py -K myapp
         sitewide: /etc/environment (which may not show up in the apache CGI passed environment)
         setenv under apache config (which may not always work?)
      4. the contents of an sod.flag file from the current.request.folder or up
         (this value is cached, restart the webserver to reload)
      5. the default parameter
    """
    if current.request.vars.sod:
        current.session.sod = SoD(current.request.vars.sod)
    elif type(current.session.sod) is SoD:
        pass  # that's a good sod
    else:
        current.session.sod = SoD(rpc_hostname_or(find_and_read_sod_file(current.request.folder) or default))
    return current.session.sod


def rpc_hostname_or(default, use_env='SOD'):
    """
    Returns the SoD as a string based on the hostname 
    used to get to thise webcall, aimed at the RPC interface and 
    naming scheme. Defaults to default is the name does not match. 
    This function can be used as the parameter for the load statement. 
    The default is passed through as is, so it should be uppercase. 
    The stage derived from the hostname is uppercased. 
    
    sod = stageofdevelopment.load(stageofdevelopment.rpc_hostname_or('ONT'))
    
    See http://dienst.wiki.drenthecollege.nl/TabDba/RpcIndex
    "https://<sod>-<functienaam>-<app/functioneel domein>.secure.drenthecollege.nl zowel voor intern als extern"
    :param default: default value if the SoD cannot be determined by hostname, requested server_name or environment var
    :type default: string
    :param use_env: name of the environment variable to use if hostname did not resolve
    :type use_env: string
    :return: state of development string
    :type return: string
    """
    RPCHostnameRegexp = r'(\w+)-(\w+)-(\w+)\.secure\.drenthecollege\.nl'
    system_hostname = platform.uname()[1]
    match = re.match(RPCHostnameRegexp, current.request.env.server_name or system_hostname, re.I)
    if match:
        # if matches on named used  in request, the first group is the SOD given
        return match.groups()[0].upper()
    else:
        # if no match found, we seek an environment variable, or default to the value of default
        # or if the env variable is not found.
        from_env = os.environ.get(use_env, None)
        return from_env if use_env and from_env else default
