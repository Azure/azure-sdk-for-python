# test_blob.py
# Copyright (C) 2008, 2009 Michael Trier (mtrier@gmail.com) and contributors
#
# This module is part of GitPython and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php

from git.test.lib import TestBase
from git import Blob


class TestBlob(TestBase):

    def test_mime_type_should_return_mime_type_for_known_types(self):
        blob = Blob(self.rorepo, **{'binsha': Blob.NULL_BIN_SHA, 'path': 'foo.png'})
        self.assertEqual("image/png", blob.mime_type)

    def test_mime_type_should_return_text_plain_for_unknown_types(self):
        blob = Blob(self.rorepo, **{'binsha': Blob.NULL_BIN_SHA, 'path': 'something'})
        self.assertEqual("text/plain", blob.mime_type)

    def test_nodict(self):
        self.assertRaises(AttributeError, setattr, self.rorepo.tree()['AUTHORS'], 'someattr', 2)
