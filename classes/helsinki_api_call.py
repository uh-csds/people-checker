#HelsinkiAPICall.py
import requests
from classes.api_call import APICall
from functions.api_decorators import check_correct_argument
import re

_API_PATH = 'https://www.helsinki.fi/en/api/people/contacts'
_SEARCH_TYPES = {"id": int, "firstnames": str, "lastname": str, "fullname": str}


def extract_page_number(page_info):
    """Given a string, find the value after \"page=\" with regex.
    :param page_info: The string that contains the page number."""
    match = re.search(r'page=(\d+)', page_info)
    return match.group(1) if match else None


class HelsinkiAPICall(APICall):
    def __init__(self, ac_api_path=_API_PATH, **kwargs):
        super().__init__(ac_api_path, **kwargs)
        self.persons_by_id = dict

    @check_correct_argument("sort", "_params", partial=True)
    def gather_page_range(self):
        """Given a sort search term, find the start and end pages."""
        data = self.request_json(sort=info)
        if data:
            # Searches for all values in hydra:view in the json, which contains the first and last pages.
            hydra_view = data.get('hydra:view', {})
            hydra_member = data.get('hydra:member', {})

            # Extract hydra:first and hydra:last's page numbers
            first_page, last_page = map(extract_page_number,
                                        (hydra_view.get('hydra:first'), hydra_view.get('hydra:last')))

            return first_page, last_page

    def get_page_member_nums(self):
        pass

    @check_correct_argument("sort", "_params", partial=True)
    def binary_arg_search(self, search_term="", filepath=""):  # Only start if sort in parameters.
        """Given a sort search parameter (i.e. id - right now, this appears to be only term requiring a sorted
        search) either look through an already existing

        :param search_term: The id you wish to search for (i.e. id = 9010001)
        :param filepath: If a filepath is set, the function will first search through the file to see if the search term exists."""
        first_page, last_page = self.gather_page_range()
        info = self.get_param("sort")

        #data = self.request_json()
        def binary_search(arg, left, right):
            mid = (left + right) // 2
            data = self.request_json(sort=arg, page=mid)

        #return self.persons_by_id

    # @check_correct_argument("sort", "_params", partial=True)
    # def binary_id_search(self, search_id="", filepath=""):  # Only start if sort in parameters.
    #     """Given a sort search parameter (i.e. id - right now, this appears to be only term requiring a sorted
    #     search) either look through an already existing
    #
    #     :param search_id: The id you wish to search for (i.e. id = 9010001)
    #     :param filepath: If a filepath is set, the function will first search through the file to see if the search term exists."""
    #     sort_info = self.gather_sort_range()
    #     if sort_info["start_id"] <= search_id <= sort_info["end_id"]:
    #         print("Found with 1 try")
    #     else:
    #         # The reason this is sliced in such a peculiar way is because the Helsinki API jumps from 91x to 93x to 94x.
    #         # Searching through the last digits will give a more accurate search.
    #         (search_id[-5:]-sort_info["end_id"][-5:])/sort_info["id_dif"]
    #
    #     if filepath:
    #         pass
    #
    #     data = self.request_json()
    #     if data:
    #         pass
    #     return self.persons_by_id
