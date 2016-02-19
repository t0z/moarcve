from datetime import datetime
from flask_restful import Resource, reqparse
from flask import send_file
import os
import moarcve.database as db
import moarcve.util as util

__LIMIT_DEFAULT__ = 100
__LIMIT_MAX__ = 1000


def argparse_cve():
    parser = reqparse.RequestParser()
    location = ['headers', 'values']

    def add(*a, **ka):
        ka['location'] = location
        parser.add_argument(*a, **ka)
    add('limit', default=__LIMIT_DEFAULT__, type=int)
    add('offset', default=0, type=int)
    add('order_by', default=['year', 'cve_id'],
        choices=util.__SAFE_PROPERTY__,
        action='append')
    add('sort', default='asc', choices=['asc', 'desc'])
    args = parser.parse_args()
    if args.limit < 1 or args.limit > __LIMIT_MAX__:
        args.limit = __LIMIT_DEFAULT__
    if args.offset < 0:
        args.offset = 0
    return args


class Static(Resource):

    def get(self, path=None):
        if path is None:
            path = 'index.html'
        print('path: %s' % path)
        static_path = os.path.join(self.static_path, path)
        static_path = static_path.replace('..', '').replace('//', '/')
        static_path = os.path.abspath(static_path)
        print('static: %s' % static_path)
        return send_file(static_path)


class Cve(Resource):

    def get(self, year=None, cve_id=None):
        year = int(year) if year is not None else None
        cve_id = int(cve_id) if cve_id is not None else None
        if year is not None and (0 > year > 65535):
            year = datetime.utcnow().year
        args = argparse_cve()
        with db.session_scope() as session:
            query = session.query(db.Cve)
            if cve_id is not None:
                query = query.filter(db.Cve.cve_id == cve_id)
            elif year is not None:
                query = query.filter(db.Cve.year == year)
            for colname in args.order_by:
                query = query.order_by(
                        getattr(getattr(db.Cve, colname), args.sort)())
            total = int(query.count())
            query = query.offset(args.offset).limit(args.limit)
            if args.offset > (total / args.limit):
                args.offset = int(total / args.limit)
            return {
                    'items': [util.res2dct(row) for row in query.all()],
                    'query': {
                        'year': year,
                        'cve_id': cve_id,
                        'total': total,
                        'sort': args.sort,
                        'order_by': args.order_by,
                        'offset': args.offset,
                        'limit': args.limit,
                    }
            }, 200
