"""Tests for the segmentation module. Use this as a template for
your own module's tests (Person 2-6)."""
import pytest

from vmsim.segmentation import (
    Segment,
    SegmentTable,
    SegmentationFault,
    make_default_segment_table,
)


class TestSegment:
    def test_basic_construction(self):
        s = Segment(name="code", base=0x1000, limit=0x1000)
        assert s.name == "code"
        assert s.base == 0x1000
        assert s.limit == 0x1000

    def test_negative_base_rejected(self):
        with pytest.raises(ValueError):
            Segment(name="bad", base=-1, limit=0x1000)

    def test_zero_limit_rejected(self):
        with pytest.raises(ValueError):
            Segment(name="bad", base=0, limit=0)


class TestSegmentTable:
    def test_add_and_lookup(self):
        table = SegmentTable()
        seg = Segment(name="code", base=0x1000, limit=0x1000)
        table.add_segment(selector=1, segment=seg)
        assert table.get_segment(1) is seg
        assert table.get_segment(999) is None

    def test_duplicate_selector_rejected(self):
        table = SegmentTable()
        s1 = Segment(name="a", base=0, limit=0x100)
        s2 = Segment(name="b", base=0x1000, limit=0x100)
        table.add_segment(1, s1)
        with pytest.raises(ValueError):
            table.add_segment(1, s2)

    def test_translate_within_bounds(self):
        table = SegmentTable()
        table.add_segment(1, Segment(name="code", base=0x1000, limit=0x100))
        logical = SegmentTable.pack_logical(selector=1, offset=0x50)
        trace = []
        linear = table.translate(logical, trace)
        assert linear == 0x1000 + 0x50
        assert len(trace) == 1
        assert trace[0].stage == "segmentation"
        assert trace[0].hit is True

    def test_translate_at_boundary(self):
        table = SegmentTable()
        table.add_segment(1, Segment(name="code", base=0x1000, limit=0x100))
        # offset == limit is out of bounds (limit is exclusive)
        logical = SegmentTable.pack_logical(selector=1, offset=0x100)
        with pytest.raises(SegmentationFault):
            table.translate(logical, [])

    def test_translate_out_of_bounds(self):
        table = SegmentTable()
        table.add_segment(1, Segment(name="code", base=0x1000, limit=0x100))
        logical = SegmentTable.pack_logical(selector=1, offset=0x1000)
        trace = []
        with pytest.raises(SegmentationFault):
            table.translate(logical, trace)
        # We must still have logged a step
        assert len(trace) == 1
        assert trace[0].hit is False

    def test_translate_unknown_selector(self):
        table = SegmentTable()
        logical = SegmentTable.pack_logical(selector=42, offset=0)
        trace = []
        with pytest.raises(SegmentationFault):
            table.translate(logical, trace)
        assert len(trace) == 1
        assert trace[0].hit is False

    def test_default_table_works(self):
        table = make_default_segment_table()
        # Each default segment translates its base offset correctly.
        for selector in [0x0001, 0x0002, 0x0003, 0x0004]:
            seg = table.get_segment(selector)
            assert seg is not None
            logical = SegmentTable.pack_logical(selector, 0)
            trace = []
            linear = table.translate(logical, trace)
            assert linear == seg.base
