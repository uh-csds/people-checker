# api_call.py
import requests


class APICall:
    """Establishes a basic API. Can be used as a base."""

    def __init__(self, ac_api_path, **kwargs):
        """Establishes base api path and parameters for the api call.
        :param ac_api_path: Base API path. ac stands for APICall to differentiate from possible keywords.
        :param kwargs: Parameters to add to the API."""
        self._api_path = ac_api_path
        self._params = kwargs

    def add_parameters(self, **kwargs):
        """Will add desired parameters to the API. If a parameter is already in the dictionary,
        it's value will be replaced. Only accepts keyword arguments.
        :param kwargs: All parameters to either set or replace."""
        if not self._params:  # If no params was set
            self._params = kwargs
        else:  # Otherwise, if params exists
            for key, value in kwargs.items():
                self._params[key] = value

    def remove_parameters(self, *args):
        """Will remove the desired parameters from the API. Will only accept the parameter keys.
        :param args: All argument keys to remove."""
        for key in args:
            try:
                del self._params[key]
            except Exception as e:
                print("remove_parameters failed on key ", key, "! The error was: ", str(e))

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
                data = requests.get(self._api_path, params=kwargs).json()
            else:
                data = requests.get(self._api_path, params=self._params).json()
        except Exception as e:
            print(f"Error when requesting from the API! Reason: {str(e)}.")
        else:
            return data

    def get_param(self, key):
        """Gets a specific parameter from the params.
        :param key: The key of the desired parameter."""
        try:
            return self._params.get(key, "")
        except Exception as e:
            print(f"Error when getting parameter! Reason: {str(e)}.")

    def get_params(self):
        """Provides a list of the parameters."""
        return self._params

    def get_url(self):
        """Gets the base url."""
        return self._api_path

    def set_url(self, url):
        """Sets the base url.
        :param url: The url to set the api path to."""
        self._api_path = url
