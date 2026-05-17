from typing import Tuple, Dict, Any
from vmsim.paging.pte import PTE

class PageFaultError(Exception):
    """
    Исключение, выбрасываемое при Page Fault (страница отсутствует в физической памяти).
    Спроектировано так, чтобы его мог перехватывать модуль обработки Page Fault'ов (и загружать данные из Swap).
    """
    def __init__(self, vpn: int, message: str = "Page fault occurred"):
        self.vpn = vpn
        self.message = f"{message}. VPN: {vpn}"
        super().__init__(self.message)

class SingleLevelPageTable:
    """
    Одноуровневая таблица страниц.
    Реализует трансляцию виртуальных номеров страниц (VPN) в физические фреймы.
    """
    def __init__(self):
        # Словарь для хранения маппинга: Virtual Page Number (VPN) -> Page Table Entry (PTE)
        self.table: Dict[int, PTE] = {}

    def map_page(self, vpn: int, frame_number: int) -> None:
        """
        Инициализирует или обновляет запись в таблице страниц.
        Связывает виртуальную страницу с физическим фреймом при ее загрузке в память.
        """
        if vpn not in self.table:
            self.table[vpn] = PTE()
            
        pte = self.table[vpn]
        pte.valid = True
        pte.frame_number = frame_number
        pte.referenced = False
        pte.dirty = False

    def translate(self, vpn: int) -> Tuple[int, Dict[str, Any]]:
        """
        Транслирует виртуальную страницу в физический фрейм.
        
        Args:
            vpn (int): Virtual Page Number (номер виртуальной страницы).
            
        Возвращает:
            Tuple[int, Dict]: Кортеж, содержащий номер физического фрейма и "трейс" шага трансляции
                              (для интеграции с визуализацией).
                              
        Исключения:
            PageFaultError: Если PTE невалидна (страницы нет в памяти).
        """
        pte = self.table.get(vpn)
        
        if pte is None or not pte.valid:
            # Подготовка трейса на случай промаха (Miss)
            trace = {
                "level": "single_page_table",
                "vpn": vpn,
                "frame": None,
                "hit": False
            }
            # Генерируем PageFault, чтобы другой участник его перехватил
            raise PageFaultError(vpn)
            
        # Обновляем бит обращения (для алгоритмов Clock, LRU и т.д.)
        pte.referenced = True
        
        # Подготовка трейса при попадании (Hit)
        trace = {
            "level": "single_page_table",
            "vpn": vpn,
            "frame": pte.frame_number,
            "hit": True
        }
        
        # Возвращаем номер фрейма (игнорируем type warning, так как при valid=True фрейм точно int)
        return pte.frame_number, trace  # type: ignore
