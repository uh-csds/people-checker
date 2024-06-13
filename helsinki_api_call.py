#helsinki_api_call.py
# File dependencies
from dependicies.api_call import APICall
from dependicies.api_decorators import check_correct_argument

# External dependencies
import requests
from bs4 import BeautifulSoup
import re
from subprocess import Popen, PIPE
from email.mime.text import MIMEText

_API_PATH = 'https://www.helsinki.fi/en/api/people/contacts'


def plaintext_sendmail(recipient, subject, message, sender="me@example.com", sendmail_loc="/usr/lib/sendmail"):
    """Sends a plaintext email through sendmail to a recipient.
    :param recipient: The email address you're sending to.
    :param subject: The subject line of the email.
    :param message: The body of the email you are sending.
    :param sender: The sender's email - may not be necessary depending on system.
    :param sendmail_loc: The location of sendmail.exe on the users or systems server."""
    msg = MIMEText(message)
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    p = Popen([sendmail_loc, "-t", "-oi"], stdin=PIPE, universal_newlines=True)
    p.communicate(msg.as_string())


def extract_page_number(page_info):
    """Given a string, find the value after \"page=\" with regex.
    :param page_info: The string that contains the page number."""
    match = re.search(r'page=(\d+)', page_info)
    return int(match.group(1)) if match else None


class HelsinkiAPICall(APICall):
    def __init__(self, ac_api_path=_API_PATH, **kwargs):
        super().__init__(ac_api_path, **kwargs)
        try:
            self.person_id = self._params.get("person_id")
            del self._params["person_id"]
            self._params["sort"] = "id"
        except KeyError:
            self.person_id = int

        self.page_numbers = {}
        self.current_member = {}

    @staticmethod
    def get_member_info(member, search_term="", all_instances=False):
        """Given a member dict, find information about that member. Can return either a dictionary
        (for an organization) or a value (for id).
        :param member: The member dictionary.
        :param all_instances: If True, returns all names and id instances. Set at start to False.
        :param search_term: What term you wish to search for.
        """
        def recursive_dict_in_list(nested_list):
            dict_elements = []
            for element in nested_list:
                if isinstance(element, dict):
                    if all_instances:
                        dict_elements.append({"id": element.get("id"), "name": element.get("name").get("en")})
                    else:
                        return {"id": element.get("id"), "name": element.get("name").get("en")}
                elif isinstance(element, list):
                    return recursive_dict_in_list(element)
            return dict_elements

        desired_search = member.get(search_term)
        # If the desired search is not a dict or list, that means the function was a success.
        if not isinstance(desired_search, (dict, list)):
            return desired_search
        else:
            return recursive_dict_in_list(desired_search)


    @staticmethod
    def scrape_helsinki_people_ids(url):
        """Given a Helsinki webpage, scrape all person ids from the html.
        :param url: The desired url link."""
        headers = {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        # Fetch the HTML content of the webpage
        response = requests.get(url, headers=headers)

        # Set up person ids
        person_ids = []

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all div elements with the class "hy-person-container"
            person_containers = soup.find_all('div', class_='hy-person-container')

            # Extract and store the data-person-id attribute
            for container in person_containers:
                person_id = container.get('data-person-id')
                if person_id:
                    person_ids.append(person_id)
            return person_ids
        else:
            print("Failed to retrieve webpage.")

    @staticmethod
    def compare_members_to_list(search_term, members_list, comparison_list):
        """Given a search term, a members list, and a comparison list that contains a members element (i.e. id),
        find all instances that match and don't match.
        :param search_term: The search term to compare - i.e. id.
        :param members_list: A list of member dictionaries.
        :param comparison_list: A list of ids to compare the members to."""
        matching_terms, different_terms = ([], [])
        for member in members_list:
            if str(member[search_term]) in comparison_list:
                matching_terms.append(member[search_term])
            else:
                different_terms.append(member[search_term])
        return matching_terms, different_terms

    @staticmethod
    def get_all_members(data):
        """Given a json file that contains hydra members, find and return a list of all members.
        :param data: The json file with hydra members."""
        members = []
        hydra_member = data.get('hydra:member', {})
        for member in hydra_member:
            members.append(member)
        return members

    @check_correct_argument("sort", "_params", partial=True)
    def gather_page_range(self):
        """Given a sort search term, find the start and end pages."""
        data = self.request_json(sort=self.get_param("sort"))
        if data:
            # Searches for all values in hydra:view in the json, which contains the first and last pages.
            hydra_view = data.get('hydra:view', {})
            hydra_member = data.get('hydra:member', {})

            # Extract hydra:first and hydra:last's page numbers
            first_page, last_page = map(extract_page_number,
                                        (hydra_view.get('hydra:first'), hydra_view.get('hydra:last')))

            self.page_numbers = {"first_page": first_page, "last_page": last_page}
            return first_page, last_page

    @check_correct_argument("sort", "_params", partial=True)
    def binary_int_search(self, search_id=int()):  # Only start if sort in parameters.
        """Given a sort search parameter (i.e. id - right now, this appears to be only term requiring a sorted
        search) either look through an already existing

        :param search_id: The id you wish to search for (i.e. id = 9010001)
        :param filepath: If a filepath is set, the function will first search through the file to see if the search term exists."""

        # This is done to reduce the number of API calls, if a binary search needs to be done multiple times
        if self.page_numbers:
            first_page, last_page = (self.page_numbers["first_page"], self.page_numbers["last_page"])
        else:
            first_page, last_page = self.gather_page_range()
        info = self.get_param("sort")
        count = 0

        # Checking to see if user already inputted a person id or not.
        if not search_id and self.person_id:
            search_id = self.person_id

        def binary_search(arg, low, high):
            # Continuing the count
            nonlocal count
            count += 1
            # print(f"Run number {count}")
            # print(f"Low value: {low}")
            # print(f"High value: {high}")
            # print(f"Search id: {search_id}")
            # Setting mid value, getting data & beginning and end id
            mid = (low + high) // 2
            data = self.request_json(sort=arg, page=mid)
            hydra_member = data.get('hydra:member', {})
            start_id, end_id = (int(hydra_member[0].get(arg)), int(hydra_member[-1].get(arg)))

            # If the search is continuing...
            if high >= low:
                # Check if search_id is between the start and end ids. If so, return the member's data.
                if start_id < search_id < end_id:
                    for member in hydra_member:
                        if int(member.get(arg)) == search_id:
                            print(f"Took {count} total calls to finish binary search for {search_id}.")
                            return member
                # Else, check if the search_id is either below or above the id range in the gathered data.
                elif search_id < start_id:
                    return binary_search(arg, low, mid - 1)
                else:
                    return binary_search(arg, mid + 1, high)
            # if it fails, return an IndexError.
            else:
                raise IndexError(f"The search id given does not appear to be in the API! Given term: {search_id}.")

        # Run the binary search algorithm
        return binary_search(info, first_page, last_page)
