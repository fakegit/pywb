from urllib import urlencode
from urlparse import parse_qs


#=================================================================
class CDXQuery(object):
    def __init__(self, **kwargs):
        self.params = kwargs

    @property
    def key(self):
        return self.params['key']

    @property
    def end_key(self):
        return self.params['end_key']

    def set_key(self, key, end_key):
        self.params['key'] = key
        self.params['end_key'] = end_key

    @property
    def url(self):
        try:
            return self.params['url']
        except KeyError:
            msg = 'A url= param must be specified to query the cdx server'
            raise CDXException(msg)

    @property
    def match_type(self):
        return self.params.get('matchType', 'exact')

    @property
    def is_exact(self):
        return self.match_type == 'exact'

    @property
    def allow_fuzzy(self):
        return self._get_bool('allowFuzzy')

    @property
    def output(self):
        return self.params.get('output', 'text')

    @property
    def limit(self):
        return int(self.params.get('limit', 100000))

    @property
    def collapse_time(self):
        return self.params.get('collapseTime')

    @property
    def resolve_revisits(self):
        return self._get_bool('resolveRevisits')

    @property
    def filters(self):
        return self.params.get('filter', [])

    @property
    def fields(self):
        v = self.params.get('fields')
        return v.split(',') if v else None

    @property
    def closest(self):
        # sort=closest is not required
        return self.params.get('closest')

    @property
    def reverse(self):
        # sort=reverse overrides reverse=0
        return (self._get_bool('reverse') or
                self.params.get('sort') == 'reverse')

    @property
    def secondary_index_only(self):
        return self._get_bool('showPagedIndex')

    @property
    def process(self):
        return self._get_bool('processOps', True)

    def set_process(self, process):
        self.params['processOps'] = process

    def _get_bool(self, name, def_val=False):
        v = self.params.get(name)
        if v:
            try:
                v = int(v)
            except ValueError as ex:
                v = (v.lower() == 'true')
        else:
            v = def_val

        return bool(v)

    def urlencode(self):
        return urlencode(self.params, True)

    @staticmethod
    def from_wsgi_env(env):
        """ utility function to extract params and create a CDXQuery
        from a WSGI environment dictionary
        """
        params = parse_qs(env['QUERY_STRING'])

        if not 'output' in params:
            params['output'] = 'text'

        # parse_qs produces arrays for single values
        # cdx processing expects singleton params for all params,
        # except filters, so convert here
        # use first value of the list
        for name, val in params.iteritems():
            if name != 'filter':
                params[name] = val[0]

        return CDXQuery(**params)
