"""Tests for core types (address, PTE, frame)."""
import pytest

from vmsim.core import (
    VirtualAddress,
    PhysicalAddress,
    PTE,
    PhysicalMemory,
    OutOfMemoryError,
    PAGE_SHIFT,
    PAGE_SIZE,
    PAGE_MASK,
    LEVELS,
    BITS_PER_LEVEL,
    ENTRIES_PER_TABLE,
    VIRTUAL_ADDRESS_BITS,
)


class TestVirtualAddress:
    def test_offset_extraction(self):
        va = VirtualAddress(0x1234_5678_ABC)
        assert va.offset == 0xABC

    def test_page_number_extraction(self):
        va = VirtualAddress(0x1234_5678_ABC)
        assert va.page_number == 0x1234_5678

    def test_zero(self):
        va = VirtualAddress(0)
        assert va.offset == 0
        assert va.page_number == 0
        assert va.multi_level_indices() == [0, 0, 0, 0]

    def test_max_value_allowed(self):
        # 48 bits, all ones
        va = VirtualAddress((1 << VIRTUAL_ADDRESS_BITS) - 1)
        assert va.offset == PAGE_MASK
        assert all(i == ENTRIES_PER_TABLE - 1 for i in va.multi_level_indices())

    def test_negative_rejected(self):
        with pytest.raises(ValueError):
            VirtualAddress(-1)

    def test_too_large_rejected(self):
        with pytest.raises(ValueError):
            VirtualAddress(1 << VIRTUAL_ADDRESS_BITS)

    def test_multi_level_indices_length(self):
        va = VirtualAddress(0x1234_5678_ABC)
        idx = va.multi_level_indices()
        assert len(idx) == LEVELS

    def test_multi_level_round_trip(self):
        """Reconstructing from indices + offset should give back the value."""
        original = 0x0000_1234_5678_9ABC & ((1 << VIRTUAL_ADDRESS_BITS) - 1)
        va = VirtualAddress(original)
        indices = va.multi_level_indices()
        rebuilt = 0
        for i, idx in enumerate(indices):
            level_from_top = i
            level_from_bottom = LEVELS - 1 - level_from_top
            shift = PAGE_SHIFT + level_from_bottom * BITS_PER_LEVEL
            rebuilt |= idx << shift
        rebuilt |= va.offset
        assert rebuilt == original


class TestPhysicalAddress:
    def test_from_frame(self):
        pa = PhysicalAddress.from_frame(frame_number=5, offset=0x100)
        assert pa.frame_number == 5
        assert pa.offset == 0x100
        assert pa.value == (5 << PAGE_SHIFT) | 0x100

    def test_offset_out_of_range(self):
        with pytest.raises(ValueError):
            PhysicalAddress.from_frame(0, PAGE_SIZE)


class TestPTE:
    def test_default_invalid(self):
        pte = PTE()
        assert pte.valid is False

    def test_construction(self):
        pte = PTE(valid=True, frame_number=42, dirty=True)
        assert pte.valid
        assert pte.frame_number == 42
        assert pte.dirty

    def test_referenced_and_accessed_are_synced(self):
        pte = PTE(valid=True, frame_number=7, referenced=True)
        assert pte.referenced is True
        assert pte.accessed is True

        pte.accessed = False
        assert pte.referenced is False


class TestPhysicalMemory:
    def test_allocate_until_full(self):
        mem = PhysicalMemory(num_frames=3)
        f1 = mem.allocate_frame(vpn=10)
        f2 = mem.allocate_frame(vpn=20)
        f3 = mem.allocate_frame(vpn=30)
        assert {f1, f2, f3} == {0, 1, 2}
        with pytest.raises(OutOfMemoryError):
            mem.allocate_frame(vpn=40)

    def test_free_frame(self):
        mem = PhysicalMemory(num_frames=2)
        f = mem.allocate_frame(vpn=1)
        assert mem.num_allocated == 1
        mem.free_frame(f)
        assert mem.num_allocated == 0
        # Can re-allocate now
        f2 = mem.allocate_frame(vpn=2)
        assert f2 == f

    def test_owner_tracking(self):
        mem = PhysicalMemory(num_frames=2)
        f = mem.allocate_frame(vpn=99)
        assert mem.owner_of(f) == 99
