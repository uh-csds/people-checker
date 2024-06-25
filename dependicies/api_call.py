# api_call.py
import requests
import urllib.parse


class APICall:
    """Establishes a basic API. Can be used as a base."""

    def __init__(self, ac_api_path, ac_headers=None, **kwargs):
        """Establishes base api path and parameters for the api call.
        :param ac_api_path: Base API path. ac stands for APICall to differentiate from possible keywords.
        :param ac_headers: Potential headers to use for the call. Expects a dict format.
        :param kwargs: Parameters to add to the API."""
        self._headers = ac_headers
        self._api_path = ac_api_path
        self._params = kwargs

    def create_child_api(self, **kwargs):
        """Creates a new API using self as a base.
        :param kwargs: parameters to add to the API call."""
        new_api = APICall(self._api_path, **self._params)
        new_api.add_parameters(**kwargs)
        return new_api

    def request_json(self, **kwargs):
        """Requests the json information from the api. If there are kwargs, they will be used instead of this
        specific json call.
        :param kwargs: Can be used if user wants to not change their API class, but does want to do a specific request
        call that their API will not currently allow."""
        try:
            if kwargs:
                data = requests.get(self._api_path, headers=self._headers, params=kwargs).json()
            else:
                data = requests.get(self._api_path, headers=self._headers, params=self._params).json()
        except Exception as e:
            print(f"Error when requesting from the API! Reason: {str(e)}.")
        else:
            return data

    def _update_dict(self, target_dict, **kwargs):
        """Helper function to update a dictionary with given keyword arguments."""
        if not target_dict:
            target_dict = kwargs
        else:
            target_dict.update(kwargs)

    def _get_value(self, source_dict, key, default=""):
        """Helper function to get a value from a dictionary with error handling."""
        try:
            return source_dict.get(key, default)
        except Exception as e:
            print(f"Error when getting value! Reason: {str(e)}.")
            return default

    def _remove_keys(self, target_dict, *keys):
        """Helper function to remove keys from a dictionary with error handling."""
        for key in keys:
            try:
                del target_dict[key]
            except KeyError:
                print(f"Key '{key}' not found in the dictionary.")
            except Exception as e:
                print(f"Failed to remove key '{key}'. The error was: {str(e)}")

    def add_parameters(self, **kwargs):
        """Will add desired parameters to the API. If a parameter is already in the dictionary,
        it's value will be replaced. Only accepts keyword arguments.
        :param kwargs: All parameters to either set or replace."""
        self._update_dict(self._params, **kwargs)

    def add_headers(self, **kwargs):
        """Will add desired headers to the API. If a header is already in the dictionary,
        it's value will be replaced. Only accepts keyword arguments.
        :param kwargs: All headers to either set or replace."""
        self._update_dict(self._headers, **kwargs)

    def remove_parameters(self, *args):
        """Will remove the desired parameters from the API. Will only accept the parameter keys.
        :param args: All argument keys to remove."""
        self._remove_keys(self._params, *args)

    def remove_headers(self, *args):
        """Will remove the desired headers from the API. Will only accept the header keys.
        :param args: All argument keys to remove."""
        self._remove_keys(self._headers, *args)

    def get_param(self, key):
        """Gets a specific parameter from the params.
        :param key: The key of the desired parameter."""
        return self._get_value(self._params, key)

    def get_params(self):
        """Provides a list of the parameters."""
        return self._params

    def get_header(self, key):
        """Gets a specific header from the params.
        :param key: The key of the desired header."""
        return self._get_value(self._headers, key)

    def get_headers(self):
        """Provides a list of the parameters."""
        return self._headers

    def get_url(self):
        """Gets the base url."""
        return self._api_path

    def set_url(self, url):
        """Sets the base url.
        :param url: The url to set the api path to."""
        self._api_path = url
