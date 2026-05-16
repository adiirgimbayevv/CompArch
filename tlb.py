from core_types import TLBEntry
from policies import LRUPolicy, FIFOPolicy

class TLB:
    def __init__(self, size: int, policy_type: str = "LRU"):
        self.size = size
        self.table = {} 
        
   
        if policy_type == "LRU":
            self.policy = LRUPolicy(size)
        elif policy_type == "FIFO":
            self.policy = FIFOPolicy(size)
        else:
            raise ValueError("Unknown policy")

        self.hits = 0
        self.misses = 0

    def lookup(self, vpn: int):
        """Ищет PFN по виртуальной странице."""
        if vpn in self.table and self.table[vpn].valid:
            self.hits += 1
            self.policy.access(vpn)  
            return self.table[vpn].pfn
        
        self.misses += 1
        return None  

    def insert(self, vpn: int, pfn: int):
        """Добавляет запись в TLB. Если места нет — вытесняет старую."""
        if vpn in self.table:
            self.table[vpn].pfn = pfn
            self.policy.access(vpn)
            return

        if len(self.table) >= self.size:
            victim_vpn = self.policy.evict()
            if victim_vpn in self.table:
                del self.table[victim_vpn]


        self.table[vpn] = TLBEntry(vpn, pfn)
        self.policy.access(vpn)

    def flush(self):
        """Сброс TLB (нужен при смене процесса)."""
        self.table.clear()
        self.__init__(self.size, "LRU" if isinstance(self.policy, LRUPolicy) else "FIFO")