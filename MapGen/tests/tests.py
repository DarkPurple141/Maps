#!/usr/bin/env python3

from unittest import TestCase

import MapGen
from MapGen import geom as g
from MapGen import name_gen as n

class ModuleTests(TestCase):
    def test_one(self):
        g.main()
    def test_two(self):
        print(n.generate_name())
