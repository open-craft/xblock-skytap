"""
Unit test mock mixins for interactions with Boomi endpoints.
"""

# Imports ###########################################################

import json
import unittest

import httpretty


# Globals ###########################################################

BOOMI_CONFIGURATION = {
    "base_url": "https://connect.boomi.example.com",
    "endpoint": "/ws/simple/createVm",
    "username": "foo",
    "token": "b8eaadd78-4ebd-4404-a261-690c8151e556",
}


# Classes ###########################################################

class CreateVmMockMixin(unittest.TestCase):
    """
    Mocks for 'createVm' Boomi endpoint responses.
    """

    def setUp(self):
        super(CreateVmMockMixin, self).setUp()

    @staticmethod
    def mock_createvm(mock_url, sharing_portal_url="https://skytap.example.com/sharing/portal/url"):
        """
        Mock a successful response from the createVm endpoint.
        """
        response = {
            "ErrorExists": False,
            "ErrorMessage": None,
            "SkytapURL": sharing_portal_url,
        }
        httpretty.register_uri(
            method=httpretty.POST,
            uri=mock_url,
            body=json.dumps(response),
            content_type="application/json",
        )

    @staticmethod
    def mock_createvm_error(mock_url, error="This is an error message returned from Boomi."):
        """
        Mock an error response from the createVm endpoint.
        """
        response = {
            "ErrorExists": True,
            "ErrorMessage": error,
            "SkytapURL": None,
        }
        httpretty.register_uri(
            method=httpretty.POST,
            uri=mock_url,
            body=json.dumps(response),
            content_type="application/json",
        )

    @staticmethod
    def mock_createvm_malformed(mock_url):
        """
        Mock an invalid response from the createVm endpoint.
        """
        httpretty.register_uri(
            method=httpretty.POST,
            uri=mock_url,
            body='Certainly this response is not valid. It\'s not even valid JSON.',
            content_type="application/json",
        )
