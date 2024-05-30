#HelsinkiAPICall.py
import requests
from api_call import APICall
from functions.api_decorators import check_correct_argument

_API_PATH = 'https://www.helsinki.fi/en/api/people/contacts'

class HelsinkiAPICall(APICall):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.persons_by_id = dict

    @check_correct_argument("sort?", "_params", partial=True)
    def sorted_search(self, search_term="", filepath=""):
        """Given a sort? search term (i.e. id, firstname, mobileNumber...) either look through an already existing

        :param filepath: If a filepath is set, the function will first search through the file to see if the search term exists."""
        if filepath:
            pass

        try:
            data = requests.get(_API_PATH, params = self._params).json()
        except Exception as e:
            print(f"Error when requesting from the API! Reason: {str(e)}.")
        else:
            return data
        return self.persons_by_id
