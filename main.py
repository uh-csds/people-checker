from helsinki_api_call import HelsinkiAPICall as hapi, plaintext_sendmail
from datetime import datetime

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
    print(f"Total of {len(different_terms)} missing from the CSDS people's page.")
    for person_id in different_terms:
        id_person_api = hapi(person_id=person_id)
        members.append(id_person_api.binary_int_search()["fullname"])

    if members:
        # Email Message
        recipient = "helsinkisocialdatascience@gmail.com"  # CHANGE
        subject = f"{datetime.today().strftime("%Y-%m")} Update on Social Data Science Centre Members"  # Will datetime work?
        message = f"""
        Hello!
        
        This is an automatic update on the current members of CSDS. The program looks at who is officially a member of CSDS in the University system, then looks at the members of 
        https://www.helsinki.fi/en/networks/centre-social-data-science/people and sees who is missing.
        
        The following people are considered to be members of CSDS, but are not currently on its people page:
        {", ".join(str(x) for x in members)}
        
        Best wishes,
        Computer""".strip('\t')

        print(message)
        # Sends email (sender, sendmail_loc not necessary if given strings are applicable, but kept in for clarity)
        plaintext_sendmail(recipient=recipient, subject=subject, message=message, sender="me@example.com", sendmail_loc="/usr/lib/sendmail")
