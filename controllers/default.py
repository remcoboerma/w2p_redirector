# -*- coding: utf-8 -*-
# Copyright 2015 Remco Boerma
# This file is licensed under the LGPLv3. See LICENSE for details.

def index():
    # read the slug from the parameters
    slug = '/'.join(request.args)
    # the query is submitted to the database. this is the 'where' part of the statement.
    # * find a row for the requisted slug within a valid timeframe
    query = (db.redirects.slug.lower() == slug.lower()) & (
        db.redirects.active_from <= request.now) & (
                db.redirects.active_to >= request.now)
    # request these fields:
    fields = db.redirects.redirect_to, db.redirects.redirect_method, db.redirects.client_side
    # do the lookup
    rows = db(query).select(*fields)
    if rows:
        # we found one or more matches, use the first match
        row = rows.first()
    else:
        # we din't find a match. Search for the default slug  (without a timeframe)
        set = db(db.redirects.slug == '').select(*fields)
        if set:
            # if a default is set, use this row to redirect to
            row = set.first()
        else:
            # if no default is found, raise with a frown and apologize.
            raise HTTP(500,"I aplogize. I have no idea where to send you.")
    # let web2py handle the redirect
    redirect(
        row.redirect_to,
        row.redirect_method,
        client_side=row.client_side
    )

# enable the following line to disable the edit interface for non authorized.
# @auth.requires_membership(role='admins')
def edit():
    is_admin = auth.has_membership(role='admins')
    grid = SQLFORM.grid(db.redirects,
                        deletable=is_admin,
                        editable=is_admin,
                        create=is_admin,
                        csv=is_admin)
    return locals()


def user():
    return dict(form=auth())
