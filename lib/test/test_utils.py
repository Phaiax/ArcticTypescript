# coding=utf8

import sublime, sys, os

from ArcticTypescript.lib.ArcticTestCase import ArcticTestCase
from ArcticTypescript.lib.utils import get_deep, get_first
from sublime_unittest import TestCase
from unittest.mock import MagicMock as MM


class test_project_opening(ArcticTestCase):


    def test_get_first(self):
        l = [{"e": 3}, {"e": 4}, {"e": 5}]
        r = get_first(l, lambda i: i['e'] == 4)
        self.assertEqual(r, l[1])


    def test_get_from_objectstructure(self):
        l = {"a": {
                "aa": 5,
                 "ab": [11, 22],
                 "ac": {
                    "aca": "v"
                    }
            }}

        self.assertEqual(get_deep(l, "a"), l['a'])
        self.assertEqual(get_deep(l, "a:aa"), 5)
        self.assertEqual(get_deep(l, "a:ab"), l['a']['ab'])
        self.assertEqual(get_deep(l, "a:ab:1"), 22)
        self.assertRaises(KeyError, lambda: get_deep(l, "a:ab:2"))
        self.assertEqual(get_deep(l, "a:ac:aca"), l['a']['ac']['aca'])
        self.assertRaises(KeyError, lambda: get_deep(l, "a:ab:asd"))


