import requests
import itertools

sortkeys = ['age', 'activity', 'answers', 'votes', 'relevance']
sortdir = ['asc', 'desc']
sort_choices = ['%s-%s' % k for k in itertools.product(sortkeys, sortdir)]
scope_choices = ['all', 'unanswered']

class LimitExceeded(Exception):
    pass

class Askbot (object):
    def __init__(self, endpoint=None):
        if endpoint is None:
            raise ValueError('you must provide an endpoint url')

        self.endpoint = endpoint

    def questions(self, author=None, scope=None,
                  sort=None, tags=None, query=None,
                  limit=None):
        s = requests.Session()

        if scope is not None:
            if not scope in scope_choices:
                raise ValueError('%s is invalid for scope' % scope)
            s.params['scope'] = scope

        if sort is not None:
            if not sort in sort_choices:
                raise ValueError('%s is invalid for sort' % sort)
            s.params['sort'] = sort

        if author is not None:
            if not author.isdigit():
                raise ValueError('author must be numeric')
            s.params['author'] = author

        if query is not None:
            s.params['query'] = query

        if tags is not None:
            s.params['tags'] = ','.join(tags)

        qcount=0
        try:
            for page in itertools.count(1):
                res = s.get('%s/questions' % self.endpoint,
                            params=dict(page=page)).json()

                for q in res['questions']:
                    yield q
                    qcount += 1
                    if limit and qcount >= limit:
                        raise LimitExceeded()

                if page >= res['pages']:
                    break
        except LimitExceeded:
            pass

