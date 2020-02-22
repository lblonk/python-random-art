
# A special dict that keeps (only) the recent expression trees in memory
from collections import OrderedDict
class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("size_limit", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


from diskcache import Cache
import jsonpickle

class ArtDiskCache(Cache):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def store_art(self,id,art):
        self[id] = jsonpickle.encode(art)

    def get_art(self,id):
        return jsonpickle.decode(self[id])