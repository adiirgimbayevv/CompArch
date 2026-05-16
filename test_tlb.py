
from tlb import TLB

tlb = TLB(size=3, policy_type="LRU")

print("--- Шаг 1: Заполняем TLB ---")
tlb.insert(vpn=1, pfn=100)
tlb.insert(vpn=2, pfn=200)
tlb.insert(vpn=3, pfn=300)

print("Поиск VPN 2 :", tlb.lookup(2))  

print("\n--- Шаг 2: Добавляем 4-й элемент ---")
tlb.insert(vpn=4, pfn=400)

print("Поиск VPN 1 :", tlb.lookup(1))
print("Поиск VPN 4 :", tlb.lookup(4))

print("\n--- Статистика ---")
print(f"Hits: {tlb.hits}, Misses: {tlb.misses}")