"""Tests for webwrench.options."""

from webwrench.options import Options, options


class TestOptions:
    def test_defaults(self):
        o = Options()
        assert o.assets == "local"
        assert o.debug is False
        assert o.keep_alive_interval == 15

    def test_set_values(self):
        o = Options()
        o.assets = "cdn"
        o.debug = True
        o.keep_alive_interval = 30
        assert o.assets == "cdn"
        assert o.debug is True
        assert o.keep_alive_interval == 30

    def test_reset(self):
        o = Options()
        o.assets = "cdn"
        o.debug = True
        o.keep_alive_interval = 99
        o.reset()
        assert o.assets == "local"
        assert o.debug is False
        assert o.keep_alive_interval == 15

    def test_singleton_is_options_instance(self):
        assert isinstance(options, Options)
