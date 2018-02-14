# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import mock
from azure_devtools.scenario_tests.utilities import (create_random_name, get_sha1_hash,
                                                     is_text_payload, is_json_payload)


class TestUtilityFunctions(unittest.TestCase):
    def test_create_random_name_default_value(self):
        default_generated_name = create_random_name()
        self.assertTrue(default_generated_name.startswith('aztest'))
        self.assertEqual(24, len(default_generated_name))
        self.assertTrue(isinstance(default_generated_name, str))

    def test_create_random_name_randomness(self):
        self.assertEqual(100, len(set([create_random_name() for _ in range(100)])))

    def test_create_random_name_customization(self):
        customized_name = create_random_name(prefix='pauline', length=61)
        self.assertTrue(customized_name.startswith('pauline'))
        self.assertEqual(61, len(customized_name))
        self.assertTrue(isinstance(customized_name, str))

    def test_create_random_name_exception_long_prefix(self):
        prefix = 'prefix-too-long'

        with self.assertRaises(ValueError) as cm:
            create_random_name(prefix, length=len(prefix)-1)
        self.assertEqual(str(cm.exception), 'The length of the prefix must not be longer than random name length')

        self.assertTrue(create_random_name(prefix, length=len(prefix)+4).startswith(prefix))

    def test_create_random_name_exception_not_enough_space_for_randomness(self):
        prefix = 'prefix-too-long'

        for i in range(4):
            with self.assertRaises(ValueError) as cm:
                create_random_name(prefix, length=len(prefix) + i)
            self.assertEqual(str(cm.exception), 'The randomized part of the name is shorter than 4, which may not be '
                                                'able to offer enough randomness')

    def test_get_sha1_hash(self):
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            content = b"""
All the world's a stage,
And all the men and women merely players;
They have their exits and their entrances,
And one man in his time plays many parts,
His acts being seven ages. At first, the infant,
Mewling and puking in the nurse's arms.
Then the whining schoolboy, with his satchel
And shining morning face, creeping like snail
Unwillingly to school. And then the lover,
Sighing like furnace, with a woeful ballad
Made to his mistress' eyebrow. Then a soldier,
Full of strange oaths and bearded like the pard,
Jealous in honor, sudden and quick in quarrel,
Seeking the bubble reputation
Even in the cannon's mouth. And then the justice,
In fair round belly with good capon lined,
With eyes severe and beard of formal cut,
Full of wise saws and modern instances;
And so he plays his part. The sixth age shifts
Into the lean and slippered pantaloon,
With spectacles on nose and pouch on side;
His youthful hose, well saved, a world too wide
For his shrunk shank, and his big manly voice,
Turning again toward childish treble, pipes
And whistles in his sound. Last scene of all,
That ends this strange eventful history,
Is second childishness and mere oblivion,
Sans teeth, sans eyes, sans taste, sans everything. 

William Shakespeare
            """
            f.write(content)
            f.seek(0)
            hash_value = get_sha1_hash(f.name)
            self.assertEqual('6487bbdbd848686338d729e6076da1a795d1ae747642bf906469c6ccd9e642f9', hash_value)

    def test_text_payload(self):
        http_entity = mock.MagicMock()
        headers = {}
        http_entity.headers = headers

        headers['content-type'] = 'foo/'
        self.assertFalse(is_text_payload(http_entity))

        headers['content-type'] = 'text/html; charset=utf-8'
        self.assertTrue(is_text_payload(http_entity))

        headers['content-type'] = 'APPLICATION/JSON; charset=utf-8'
        self.assertTrue(is_text_payload(http_entity))

        headers['content-type'] = 'APPLICATION/xml'
        self.assertTrue(is_text_payload(http_entity))

        http_entity.headers = None  # default to text mode if there is no header
        self.assertTrue(is_text_payload(http_entity))

    def test_json_payload(self):
        http_entity = mock.MagicMock()
        headers = {}
        http_entity.headers = headers

        headers['content-type'] = 'APPLICATION/JSON; charset=utf-8'
        self.assertTrue(is_json_payload(http_entity))

        headers['content-type'] = 'application/json; charset=utf-8'
        self.assertTrue(is_json_payload(http_entity))

        headers['content-type'] = 'application/xml; charset=utf-8'
        self.assertFalse(is_json_payload(http_entity))
