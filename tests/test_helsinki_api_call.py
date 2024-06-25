import unittest
from unittest.mock import patch
import helsinki_people_checker as hpc


class TestHelsinkiAPIFunctions(unittest.TestCase):

    def test_extract_page_number(self):
        self.assertEqual(hpc.extract_page_number("page=3"), 3)
        self.assertIsNone(hpc.extract_page_number("no page info"))

    def test_get_member_info(self):
        member = {
            "researchOrganizations": [{"id": 1, "name": {"en": "Centre for Social Data Science"}}],
            "firstnames": "Jim",
            "lastnames": "Beam"
        }
        self.assertEqual(hpc.get_member_info(member, "firstnames"), "Jim")
        self.assertEqual(hpc.get_member_info(member, "researchOrganizations"),
                         {"id": 1, "name": "Centre for Social Data Science"})

    @patch('requests.get')
    def test_scrape_helsinki_people_ids(self, mock_get):
        html_content = '''
        <div class="hy-person-container" data-person-id="123"></div>
        <div class="hy-person-container" data-person-id="456"></div>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = html_content

        result = hpc.scrape_helsinki_people_ids('fake_url')
        self.assertEqual(result, ["123", "456"])

    @patch('requests.get')
    def test_scrape_helsinki_people_ids_failure(self, mock_get):
        mock_get.return_value.status_code = 404

        result = hpc.scrape_helsinki_people_ids('fake_url')
        self.assertIsNone(result)

    def test_compare_members_to_list(self):
        members_list = [{"id": "123"}, {"id": "456"}, {"id": "789"}]
        comparison_list = ["123", "789"]
        matching, different = hpc.compare_members_to_list("id", members_list, comparison_list)
        self.assertEqual(matching, ["123", "789"])
        self.assertEqual(different, ["456"])

    def test_get_all_members(self):
        data = {
            'hydra:member': [{"id": "123"}, {"id": "456"}]
        }
        result = hpc.get_all_members(data)
        self.assertEqual(result, [{"id": "123"}, {"id": "456"}])

    @patch('helsinki_people_checker.HelsinkiAPICall.request_json')
    def test_gather_page_range(self, mock_request_json):
        mock_request_json.return_value = {
            'hydra:view': {'hydra:first': 'page=1', 'hydra:last': 'page=10'}
        }
        api_call = hpc.HelsinkiAPICall(person_id=1033)
        first_page, last_page = api_call.gather_page_range()
        print(first_page)
        self.assertEqual(first_page, 1)
        self.assertEqual(last_page, 10)

    @patch('helsinki_people_checker.HelsinkiAPICall.request_json')
    def test_gather_page_range_failure(self, mock_request_json):
        with self.assertRaises(KeyError):
            mock_request_json.return_value = {
                'hydra:view': {'hydra:first': 'page=1', 'hydra:last': 'page=10'},
                'hydra:member': []
            }
            api_call = hpc.HelsinkiAPICall()
            first_page, last_page = api_call.gather_page_range()


class TestHelsinkiAPIConnectivity(unittest.TestCase):
    """Tests that don't use the mock connection."""

    def test_is_hydra_used(self):
        sort_api = hpc.HelsinkiAPICall(sort="id")
        sort_first_page = sort_api.request_json()
        print(sort_first_page)
        hydra_first_page = hpc.extract_page_number(sort_first_page.get('hydra:view', {}).get('hydra:first'))
        self.assertEqual(1, hydra_first_page)

    def test_binary_search(self):
        id_person_api = hpc.HelsinkiAPICall(person_id=9077557)  # Marias ID
        person_name = id_person_api.binary_int_search()["fullname"]
        self.assertEqual(person_name, "Maria Valaste")


if __name__ == '__main__':
    unittest.main()
