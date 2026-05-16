from collections import deque, OrderedDict

class FIFOPolicy:
    """Первым пришел — первым ушел."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()

    def access(self, key):
        if key not in self.queue:
            self.queue.append(key)

    def evict(self):
        if self.queue:
            return self.queue.popleft()
        return None


class LRUPolicy:
    """Вытеснение давно неиспользуемых (Least Recently Used)."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        # OrderedDict идеально подходит для LRU
        self.cache = OrderedDict()

    def access(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            self.cache[key] = True

    def evict(self):
        if self.cache:
            key, _ = self.cache.popitem(last=False)
            return key
        return None