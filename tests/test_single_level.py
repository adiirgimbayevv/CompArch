import pytest
from vmsim.memory.frame_allocator import FrameAllocator
from vmsim.paging.single_level import SingleLevelPageTable, PageFaultError

def test_frame_allocator_basic():
    """Тест: Базовое выделение и освобождение фреймов."""
    allocator = FrameAllocator(total_frames=10)
    
    assert allocator.get_stats()["free_frames"] == 10
    
    frame = allocator.allocate_frame()
    assert frame is not None
    assert allocator.get_stats()["allocated_frames"] == 1
    assert allocator.get_stats()["free_frames"] == 9
    
    allocator.free_frame(frame)
    assert allocator.get_stats()["free_frames"] == 10
    assert allocator.get_stats()["allocated_frames"] == 0

def test_frame_allocator_oom():
    """Тест: Поведение аллокатора, когда заканчивается свободная память."""
    allocator = FrameAllocator(total_frames=2)
    
    frame1 = allocator.allocate_frame()
    frame2 = allocator.allocate_frame()
    frame3 = allocator.allocate_frame()  # Память кончилась
    
    assert frame1 is not None
    assert frame2 is not None
    assert frame3 is None

def test_page_table_translation_hit():
    """Тест: Успешная трансляция адреса (Page Hit)."""
    allocator = FrameAllocator(total_frames=256)
    page_table = SingleLevelPageTable()
    
    vpn = 42
    frame = allocator.allocate_frame()
    
    # Связываем виртуальную страницу с физическим фреймом
    page_table.map_page(vpn, frame) # type: ignore
    
    # Выполняем трансляцию
    translated_frame, trace = page_table.translate(vpn)
    
    assert translated_frame == frame
    assert trace["hit"] is True
    assert trace["vpn"] == vpn
    assert trace["frame"] == frame
    
    # Проверяем, что обновился бит referenced
    assert page_table.table[vpn].referenced is True

def test_page_table_translation_fault():
    """Тест: Промах страницы (Page Fault) выбрасывает нужное исключение."""
    page_table = SingleLevelPageTable()
    vpn = 100
    
    # Страница еще не загружена в память
    with pytest.raises(PageFaultError) as excinfo:
        page_table.translate(vpn)
        
    # Убеждаемся, что исключение содержит правильный VPN
    assert excinfo.value.vpn == vpn
