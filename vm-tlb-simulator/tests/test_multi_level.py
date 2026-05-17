"""Tests for the multi-level page table."""
import pytest

from vmsim.core import PTE, PhysicalMemory, PAGE_SHIFT
from vmsim.paging.multi_level import MultiLevelPageTable
from vmsim.paging.single_level import PageFault


@pytest.fixture
def memory():
    return PhysicalMemory(num_frames=16)


@pytest.fixture
def page_table(memory):
    return MultiLevelPageTable(memory)


class TestMap:
    def test_map_then_lookup_returns_same_pte(self, page_table):
        pte = PTE(valid=True, frame_number=5)
        page_table.map(0x12345, pte)
        assert page_table.lookup(0x12345) is pte

    def test_map_multiple_vpns(self, page_table):
        pte_a = PTE(valid=True, frame_number=1)
        pte_b = PTE(valid=True, frame_number=2)
        page_table.map(0x100, pte_a)
        page_table.map(0x200, pte_b)
        assert page_table.lookup(0x100) is pte_a
        assert page_table.lookup(0x200) is pte_b

    def test_map_overwrites_existing(self, page_table):
        page_table.map(0x12345, PTE(valid=True, frame_number=1))
        page_table.map(0x12345, PTE(valid=True, frame_number=2))
        assert page_table.lookup(0x12345).frame_number == 2


class TestLookup:
    def test_lookup_unmapped_returns_none(self, page_table):
        assert page_table.lookup(0x12345) is None

    def test_lookup_other_vpn_still_none_after_mapping(self, page_table):
        page_table.map(0x12345, PTE(valid=True, frame_number=5))
        assert page_table.lookup(0x99999) is None


class TestTranslate:
    def test_translate_mapped_page(self, page_table):
        page_table.map(0x12345, PTE(valid=True, frame_number=7))
        address = (0x12345 << PAGE_SHIFT) | 0xabc
        physical = page_table.translate(address, [])
        assert physical == (7 << PAGE_SHIFT) | 0xabc

    def test_translate_unmapped_raises_page_fault(self, page_table):
        address = (0x99999 << PAGE_SHIFT) | 0x100
        with pytest.raises(PageFault):
            page_table.translate(address, [])

    def test_translate_invalid_pte_raises_page_fault(self, page_table):
        page_table.map(0x12345, PTE(valid=False, frame_number=0))
        with pytest.raises(PageFault):
            page_table.translate(0x12345 << PAGE_SHIFT, [])

    def test_translate_appends_trace_steps(self, page_table):
        page_table.map(0x12345, PTE(valid=True, frame_number=7))
        trace = []
        page_table.translate(0x12345 << PAGE_SHIFT, trace)
        assert len(trace) == 5
        assert trace[-1].stage == "physical_access"
        assert trace[-1].hit is True

    def test_translate_sets_accessed_bit(self, page_table):
        pte = PTE(valid=True, frame_number=5, accessed=False)
        page_table.map(0x12345, pte)
        page_table.translate(0x12345 << PAGE_SHIFT, [])
        assert pte.accessed is True


class TestMemoryOverhead:
    def test_overhead_grows_with_mappings_in_different_regions(self, page_table):
        initial = page_table.memory_overhead_bytes()
        page_table.map(0x100, PTE(valid=True, frame_number=1))
        after_one = page_table.memory_overhead_bytes()
        assert after_one > initial
        page_table.map(0x80000000, PTE(valid=True, frame_number=2))
        after_two = page_table.memory_overhead_bytes()
        assert after_two > after_one