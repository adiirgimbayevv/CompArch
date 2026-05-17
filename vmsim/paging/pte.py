from dataclasses import dataclass
from typing import Optional

@dataclass
class PTE:
    """
    Page Table Entry (PTE) - запись таблицы страниц.
    
    Атрибуты:
        valid (bool): Указывает, находится ли страница в данный момент в физической памяти.
        frame_number (Optional[int]): Номер физического фрейма, если страница загружена (valid == True).
        dirty (bool): Указывает, была ли страница изменена (модифицирована). Если да, ее нужно будет записать в Swap при вытеснении.
        referenced (bool): Указывает, обращались ли к странице недавно. Необходимо для алгоритмов вытеснения, таких как Clock или LRU.
    """
    valid: bool = False
    frame_number: Optional[int] = None
    dirty: bool = False
    referenced: bool = False
