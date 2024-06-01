#HelsinkiAPICall.py
import requests
from classes.api_call import APICall
from functions.api_decorators import check_correct_argument

_API_PATH = 'https://www.helsinki.fi/en/api/people/contacts'
_SEARCH_TYPES = {"id": int, "firstnames": str, "lastname": str, "fullname": str}


class HelsinkiAPICall(APICall):
    def __init__(self, pc_api_path=_API_PATH, **kwargs):
        super().__init__(pc_api_path, **kwargs)
        self.persons_by_id = dict

    @check_correct_argument("sort", "_params", partial=True)
    def gather_sort_range(self):
        """Given a sort search term, find the start and end pages."""
        info = self.get_param("sort")
        old_data = self.request_json()
        return info, old_data

    @check_correct_argument("sort", "_params", partial=True)
    def sorted_search(self, search_term="", filepath=""):  # Only start if sort in parameters.
        """Given a sort search parameter (i.e. id - right now, this appears to be only term requiring a sorted
        search) either look through an already existing

        :param search_term: The term you wish to search for (i.e. id = 9010001)
        :param filepath: If a filepath is set, the function will first search through the file to see if the search term exists."""
        if filepath:
            pass

        data = self.request_json()
        if data:
            pass
        return self.persons_by_id
