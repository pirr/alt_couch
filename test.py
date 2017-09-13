import alt_path
from header import *
from vb.couch import Q


cfg = alt.cfg.read()
root_url = 'http://' + cfg.root_url
db = vb.couch.DB(cfg.db)
heap_db = vb.couch.DB(cfg.db + '_heap')

data1 = db.find(reestr_name__eq=u'Иркутск', limit=50)
data2 = db.find(Q(reestr_name__eq=u'Иркутск')
                & (Q(полезное_ископаемое__название_нормализованное__in=['золото россыпное', 'золото рудное'])
                    | Q(полезное_ископаемое__название_нормализованное__eq="бром")), limit=40)
print('data1 length', len(data1))
print('data2 length', len(data2))
print('data2 docs:')
for doc in data2:
    print(doc['reestr_name'],
          doc['название_объекта'],
          doc['полезное_ископаемое']['название_нормализованное'])