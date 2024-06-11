from helsinki_api_call import HelsinkiAPICall as hapi

if __name__ == '__main__':
    # First, finding all people_ids from the social data science page
    desired_search_page = "https://www.helsinki.fi/en/networks/centre-social-data-science/people"
    people_ids = hapi.scrape_helsinki_people_ids(desired_search_page)

    # Next - assuming you don't immediately know the research id - finding it through the name of an individual.
    person_api = hapi(fullname="Maria Valaste")
    member = hapi.get_all_members(person_api.request_json())[0]
    hapi.get_member_info(member, search_term="id")
    #print(member["id"])




