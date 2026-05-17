from typing import Optional, Set

class FrameAllocator:
    """
    Аллокатор физической памяти.
    Управляет пулом доступных физических фреймов (памяти).
    """
    def __init__(self, total_frames: int):
        self.total_frames = total_frames
        # Изначально все фреймы свободны
        self.free_frames: Set[int] = set(range(total_frames))
        self.allocated_frames: Set[int] = set()

    def allocate_frame(self) -> Optional[int]:
        """
        Выделяет один свободный физический фрейм.
        
        Возвращает:
            int: Номер выделенного фрейма.
            None: Если свободных фреймов больше нет (требуется вытеснение страниц).
        """
        if not self.free_frames:
            return None
            
        frame_number = self.free_frames.pop()
        self.allocated_frames.add(frame_number)
        return frame_number

    def free_frame(self, frame_number: int) -> None:
        """
        Освобождает ранее выделенный фрейм (например, при вытеснении страницы в Swap).
        """
        if frame_number in self.allocated_frames:
            self.allocated_frames.remove(frame_number)
            self.free_frames.add(frame_number)
        else:
            raise ValueError(f"Фрейм {frame_number} не был выделен или уже свободен.")
            
    def get_stats(self) -> dict:
        """
        Возвращает статистику использования физической памяти.
        """
        return {
            "total_frames": self.total_frames,
            "free_frames": len(self.free_frames),
            "allocated_frames": len(self.allocated_frames)
        }
