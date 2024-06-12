from helsinki_api_call import HelsinkiAPICall as hapi

if __name__ == '__main__':
    # Getting Research Organization ID
    ## If you don't know the org id, you can find it through the name of an associated individual.
    named_individual = "Maria Valaste"
    named_person_api = hapi(fullname=named_individual)
    member = hapi.get_all_members(named_person_api.request_json())[0]
    research_org = hapi.get_member_info(member, search_term="researchOrganizations")

    # Discovering How a Webpage's People Compares to a Research Organization
    ## First, finding all people_ids from the social data science page
    desired_search_page = "https://www.helsinki.fi/en/networks/centre-social-data-science/people"
    website_people_ids = hapi.scrape_helsinki_people_ids(desired_search_page)

    ## Then, getting all the members from the research organization
    research_org_api = hapi(**{'researchOrganizations.id[]': research_org["id"]})
    org_members = hapi.get_all_members(research_org_api.request_json())

    ## Finally, seeing how those terms match
    matching_terms, different_terms = hapi.compare_members_to_list("id", org_members, website_people_ids)

    # Getting Person Info
    ## Now that we know the different people's ids, finding their information.
    members = []
    for person_id in different_terms:
        id_person_api = hapi(person_id = person_id)
        members.append(id_person_api.binary_int_search())

    for member in members:
        print(member)




