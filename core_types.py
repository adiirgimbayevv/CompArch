class TLBEntry:
    def __init__(self, vpn: int, pfn: int, valid: bool = True):
        self.vpn = vpn       
        self.pfn = pfn        
        self.valid = valid    