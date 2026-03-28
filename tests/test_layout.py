"""Tests for webwrench.layout -- layout primitives."""

from webwrench._context import Element, Page, get_default_page
from webwrench.layout import (
    ColumnSet,
    LayoutContainer,
    TabSet,
    accordion,
    card,
    columns,
    grid,
    modal,
    nav,
    sidebar,
    tabs,
)


class TestLayoutContainer:
    def test_context_manager_captures_children(self):
        page = Page()
        container = LayoutContainer("div", page=page)
        page.add(container)
        with container:
            page.add(Element("p", content="inside", element_id="p1"))
        # The <p> should be a child of the container, not a direct page element
        assert len(page.elements) == 1  # Only the container
        assert len(container.content) == 1
        assert container.content[0].tag == "p"

    def test_context_manager_multiple_children(self):
        page = Page()
        container = LayoutContainer("div", page=page)
        page.add(container)
        with container:
            page.add(Element("p", element_id="a"))
            page.add(Element("span", element_id="b"))
        assert len(container.content) == 2


class TestColumns:
    def test_equal_columns(self):
        col_set = columns(3)
        assert isinstance(col_set, ColumnSet)
        assert len(col_set) == 3

    def test_weighted_columns(self):
        col_set = columns([2, 1])
        assert len(col_set) == 2

    def test_columns_added_to_page(self):
        columns(2)
        assert len(get_default_page().elements) == 1

    def test_getitem(self):
        col_set = columns(2)
        col0 = col_set[0]
        col1 = col_set[1]
        assert isinstance(col0, LayoutContainer)
        assert isinstance(col1, LayoutContainer)

    def test_context_manager(self):
        col_set = columns(2)
        with col_set:
            pass  # Should not raise

    def test_custom_page(self):
        page = Page()
        columns(2, page=page)
        assert len(page.elements) == 1


class TestTabs:
    def test_creates_tabs(self):
        tab_set = tabs(["A", "B", "C"])
        assert isinstance(tab_set, TabSet)
        assert len(tab_set) == 3

    def test_getitem(self):
        tab_set = tabs(["X", "Y"])
        assert isinstance(tab_set[0], LayoutContainer)
        assert isinstance(tab_set[1], LayoutContainer)

    def test_added_to_page(self):
        tabs(["A", "B"])
        assert len(get_default_page().elements) == 1

    def test_labels(self):
        tab_set = tabs(["Foo", "Bar"])
        assert tab_set._labels == ["Foo", "Bar"]

    def test_context_manager(self):
        tab_set = tabs(["A"])
        with tab_set:
            pass  # Should not raise


class TestAccordion:
    def test_creates_details(self):
        a = accordion("Advanced")
        assert isinstance(a, LayoutContainer)
        assert a.tag == "details"

    def test_open(self):
        a = accordion("Open", open=True)
        assert a.attrs.get("open") == "open"

    def test_closed_by_default(self):
        a = accordion("Closed")
        assert "open" not in a.attrs

    def test_has_summary_child(self):
        a = accordion("Title")
        assert len(a.content) >= 1
        assert a.content[0].tag == "summary"
        assert a.content[0].content == "Title"


class TestSidebar:
    def test_creates_aside(self):
        s = sidebar()
        assert isinstance(s, LayoutContainer)
        assert s.tag == "aside"
        assert "ww-sidebar" in s.attrs["class"]


class TestCard:
    def test_creates_card(self):
        c = card()
        assert isinstance(c, LayoutContainer)
        assert "bw_card" in c.attrs["class"]

    def test_with_title(self):
        c = card(title="Revenue")
        assert len(c.content) >= 1
        assert c.content[0].content == "Revenue"

    def test_no_title(self):
        c = card()
        assert c.content == []


class TestGrid:
    def test_creates_grid(self):
        g = grid("1fr 2fr")
        assert isinstance(g, LayoutContainer)
        assert "display:grid" in g.attrs["style"]
        assert "1fr 2fr" in g.attrs["style"]

    def test_default_template(self):
        g = grid()
        assert "1fr 1fr" in g.attrs["style"]


class TestModal:
    def test_creates_modal(self):
        m = modal("Confirm")
        assert isinstance(m, LayoutContainer)
        assert m.attrs.get("role") == "dialog"
        assert m.attrs.get("aria-modal") == "true"

    def test_has_header(self):
        m = modal("Title")
        assert len(m.content) >= 1
        assert m.content[0].content == "Title"

    def test_close_method_exists(self):
        m = modal("Test")
        # close is a lambda placeholder
        assert hasattr(m, "close")
        m.close()  # Should not raise


class TestNav:
    def test_creates_nav(self):
        n = nav([{"text": "Home", "href": "/"}])
        assert n.tag == "nav"
        assert len(n.content) == 1
        assert n.content[0].tag == "a"
        assert n.content[0].attrs["href"] == "/"
        assert n.content[0].content == "Home"

    def test_multiple_items(self):
        items = [{"text": "A", "href": "/a"}, {"text": "B", "href": "/b"}]
        n = nav(items)
        assert len(n.content) == 2

    def test_missing_href(self):
        n = nav([{"text": "X"}])
        assert n.content[0].attrs["href"] == "#"

    def test_missing_text(self):
        n = nav([{"href": "/y"}])
        assert n.content[0].content == ""
