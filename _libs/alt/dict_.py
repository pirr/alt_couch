import yaml, json, copy

class dict_(dict):
    
    def __init__(self, *args, **kwargs):
        super(dict_, self).__init__(*args, **kwargs)
        for name,item in self.items():
            if isinstance(item,dict):
                self[name] = dict_(item)
            if isinstance(item,list):
                for ilist,listitem in enumerate(item):
                    if isinstance(listitem,dict):
                        item[ilist]=dict_(listitem)
        self.__dict__ = self

    def set_(self, path, value):

        pos = path.find('.')
        if pos==-1:
            self[path] = value
        else:
            if path[:pos] not in self:
                self[path[:pos]] = dict_()
            self[path[:pos]].set_(path[pos+1:], value)

    def get_(self, path, default=None):

        pos = path.find('.')
        if pos==-1:
            if path in self:
                return self[path]
            else:
                return default
        else:
            if path[:pos] not in self:
                return default
            else:
                return self[path[:pos]].get_(path[pos+1:], default=default)

    def del_(self, path):

        pos = path.find('.')
        if pos==-1:
            if path in self:
                del self[path]
        else:
            if path[:pos] in self:
                self[path[:pos]].del_(path[pos+1:])
                if not self[path[:pos]]:
                    del self[path[:pos]]

    def remove_empty(self):

        remove = []
        for name, value in self.items():
            if isinstance(value, (str, dict_, dict, list)) and not value:
                remove.append(name)
                continue
            if isinstance(value,dict):
                self[name].remove_empty()
            elif isinstance(value,list):
                for ilist, listvalue in enumerate(value):
                    if isinstance(listvalue,dict):
                        value[ilist].remove_empty()
        for name in remove:
            del self[name]

    def equal(self, doc, ignore=[]):

        self_doc = copy.deepcopy(self)
        for field in ignore:
            if field in self_doc:
                del self_doc[field]
            if field in doc:
                del doc[field]

        return json.dumps(self_doc) == json.dumps(doc)

    def to_yaml(self):

        self_doc = copy.deepcopy(self)

        return yaml.dump(self_doc)



