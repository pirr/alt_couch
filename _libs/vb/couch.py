import couchdb, glob, os, socket, cherrypy
from functools import reduce
from alt.dict_ import dict_
import alt.time, vb.cfg


def create(db_name):
    server = couchdb.Server()
    server.resource.credentials = ('admin', 'admin')
    if db_name not in server:
        server.create(db_name)


class Q:
    '''
        Основной объект для составления запроса
    '''
    OR = '$or'
    AND = '$and'

    def __init__(self, **kwarg):
        self.field_cond = list(kwarg.keys())[0]
        self.val = list(kwarg.values())[0]

    @property
    def P(self):
        field_cond_list = self.field_cond.split('__')
        field = field_cond_list[:-1]
        cond = '$' + field_cond_list[-1]
        parsed_field_cond = reduce(lambda x, y: {y: x},
                                   reversed(field + [cond, self.val]))
        return parsed_field_cond

    def _combine(self, other, cond):
        query = dict()
        query[cond] = [self.P, other.P]
        return _FQ(query)

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)


class _FQ(Q):
    '''
        Вспомогательный объект для составления запросов
    '''
    def __init__(self, val):
        self.val = val

    @property
    def P(self):
        return self.val


class DB:
    def __init__(self, name, admin=False, user_id=None):

        self.name = name
        self.host = socket.gethostname()
        self.server = couchdb.Server()
        self.user_id = user_id
        if admin:
            self.server.resource.credentials = ('admin', 'admin')
        self.db = self.server[name]

    def __contains__(self, doc_id):

        return doc_id in self.db

    def __getitem__(self, doc_id):

        return dict_(self.db[doc_id])

    def __setitem__(self, doc_id, doc):

        if 'type' not in doc:
            raise Exception('No type')
        doc.mhost = self.host
        doc.mtime = alt.time.mtime()
        self.db[doc_id] = doc

    def __delitem__(self, key):

        del self.db[key]

    def check(self, doc, user_id=None):

        if 'type' not in doc:
            raise Exception('No type in doc')
        if user_id is None:
            if self.user_id is not None:
                doc.user_id = self.user_id
            else:
                doc.user_id = cherrypy.session['user_id']
        else:
            doc.user_id = user_id
        if 'user_id' not in doc:
            raise Exception('No user_id in doc')
        doc.mhost = self.host
        doc.mtime = alt.time.mtime()

    def new_id(self, doc, user_id=None):

        self.check(doc, user_id=user_id)
        doc_id, _ = self.db.save(doc)
        print('Saved', doc_id)

        return doc_id

    def new(self, doc_id, doc, user_id=None):

        self.check(doc, user_id=user_id)
        self.db[doc_id] = doc
        print('Saved', doc_id)

    def save(self, doc_id, doc, user_id=None, exception=True):

        self.check(doc, user_id=user_id)
        doc.remove_empty()
        try:
            if doc_id in self.db:
                if doc.equal(self.db[doc_id], ignore=['host', 'mtime', 'user_id']):
                    if exception:
                        raise Exception('Nothing changed')
                    else:
                        return 'SAME'
            self.db[doc_id] = doc
        except couchdb.ResourceConflict:
            if exception:
                raise Exception('Version conflict')
            else:
                return 'CONFLICT'

        return ''

    def view(self, name, **options):

        return self.db.view(name + '/' + name, **options)

    def force_save(self, doc_id, doc):

        self.check(doc)
        doc.remove_empty()
        for itry in range(10):
            try:
                if doc_id in self.db:
                    if doc.equal(self.db[doc_id], ignore=['host', 'mtime', 'user_id']):
                        return 'SAME'
                    rev = self.db[doc_id]['_rev']
                    doc._rev = rev
                self.db[doc_id] = doc
            except couchdb.ResourceConflict:
                continue

    def install_views(self, prefix):

        server = couchdb.Server()
        server.resource.credentials = ('admin', 'admin')
        db = server[self.name]
        prefix = prefix + '-'

        views_ids_to_delete = []
        for row in db.view('_all_docs')["_design/":"_design0"]:
            if not row.id.split('/')[1].startswith(prefix):
                continue
            views_ids_to_delete.append(row.id)

        name = 'heap_db' if self.name.endswith('_heap') else 'db'
        views_dir = vb.cfg.main_dir() + '_views/' + name + '/'
        if not os.path.exists(views_dir):
            print(views_dir)
            print('Skip %s views' % name)
            return

        view_files = glob.glob(views_dir + '*.py')
        for view_file in view_files:
            view_name = os.path.basename(view_file[:-3])
            if view_name == 'install':
                continue
            view_name = prefix + view_name
            view_id = '_design/' + view_name
            view_doc = {'language': 'python', 'views': {view_name: {}}}
            with open(view_file) as f:
                text = f.read()
            debug_pos = text.find('# debug')
            if debug_pos != -1:
                text = text[:debug_pos]
            reduce_pos = text.find('def reduce(')
            if reduce_pos == -1:
                map_text = text
                reduce_text = None
            else:
                map_text = text[:reduce_pos]
                reduce_text = text[reduce_pos:]
            view_doc['views'][view_name]['map'] = map_text
            if reduce_text:
                view_doc['views'][view_name]['reduce'] = reduce_text

            if view_id in db:
                old_view_doc = dict_(db[view_id])
                del old_view_doc._rev
                del old_view_doc._id
                if old_view_doc == view_doc:
                    views_ids_to_delete.remove(view_id)
                    continue
                else:
                    print('Deleting', view_id)
                    del db[view_id]

            print('Saving', view_id)
            db[view_id] = view_doc
            if view_id in views_ids_to_delete:
                views_ids_to_delete.remove(view_id)

        for design_id in views_ids_to_delete:
            print('Deleting', design_id)
            del db[design_id]

    def find(self, *args, **kwargs):
        '''
        Поиск документов в БД CouchDB 2 через /db/_find - http://docs.couchdb.org/en/2.0.0/api/database/find.html
        :param args: Q объекты с условиями запроса
                    Пример запроса:
                    find(Q(reestr_name__eq=u'Test1') | Q(reestr_name__eq=u'Test2')
                            & Q(pi__normal__in=[u'золото', u'серебро']))
                    __eq, __in - селекторы (см. CouchDB 2.0 селекторы)
                    Через двойное нижнее подчеркивание ('__') передаются вложенные поля:
                    pi__normal = doc['pi']['normal']
        :param kwargs:
                    параметры:
                    limit - кол-во документов
                    простой запрос:
                    find(reestr_name__eq=u'Test1')
        :return: документы соответсвующие запросу
        '''
        limit = kwargs.get('limit', 25)
        if args:
            query = args[0].P
        elif kwargs:
            query = Q(**kwargs).P
        else:
            raise Exception('Need query, for example: name__eq = "Name" or used Q for complex conditions')
        _, _, data = self.db.resource.post_json('_find', body={"selector": query, "limit": limit}, headers={
            'Content-Type': 'application/json'}
                                                )
        return data['docs']
