# main.py
import helsinki_people_checker as hpc
import argparse
from datetime import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Gathers user data from a given Helsinki website and Helsinki research group, and sends an email "
                    "to a desired recipient, informing them of users who are a part of the research group but not on "
                    "the website.")
    parser.add_argument("--email_recipient", metavar="ADDRESS", required=True,
                        help="The email address of the recipient.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--r_org_individual', metavar='NAME',
                       help="If you don't know the id of your research group, this command lets you use a person "
                            "whose first research group is the one you are looking for.")
    group.add_argument('--r_org_group', metavar='NAME',
                       help="If you don't know the id of your research group, this command lets you use the name of "
                            "the research group to find what you're looking for.")
    group.add_argument('--r_org_id', metavar='ID', type=int, default=62060775,
                       help="Uses the research group id, skipping the search step. Default is the "
                            "Centre for Social Data Science Org ID.")
    parser.add_argument("--website", metavar='URL',
                        default="https://www.helsinki.fi/en/networks/centre-social-data-science/people",
                        help="The name of the website whose hy-person-cards you want to check. Default is the "
                             "Centre for Social Data Science People's Page.")
    parser.add_argument("--email_sender", metavar="ADDRESS", default="me@example.com",
                        help="The email address of the sender. The default is me@example.com.")
    parser.add_argument("--sendmail_loc", metavar="FILE PATH", default="/usr/lib/sendmail",
                        help="The location of the sendmail app. The default is /usr/lib/sendmail.")
    args = parser.parse_args()
    print(args)

    # Getting Research Organization ID
    ## If you don't know the org id, you can find it through the name of an associated individual.
    if args.r_org_individual:  # By individuals name
        named_person_api = hpc.HelsinkiAPICall(fullname=args.r_org_individual)
        member = hpc.get_all_members(named_person_api.request_json())[0]
        research_org_id = hpc.get_member_info(member, search_term="researchOrganizations")["id"]
        print("Found matching research org by person.")
    elif args.r_org_group:  # By research orgs name
        named_person_api = hpc.HelsinkiAPICall(search=args.r_org_group)
        research_org_id = named_person_api.find_specific_id(search_term="researchOrganizations")
        print("Found matching research org by name.")
    else:  # By ID
        research_org_id = args.r_org_id

    # Discovering How a Webpage's People Compares to a Research Organization
    ## First, finding all people_ids from the social data science page
    website_people_ids = hpc.scrape_helsinki_people_ids(args.website)

    ## Then, getting all the members from the research organization
    research_org_api = hpc.HelsinkiAPICall(**{'researchOrganizations.id[]': research_org_id})
    org_members = hpc.get_all_members(research_org_api.request_json())

    ## Finally, seeing how those terms match
    matching_terms, different_terms = hpc.compare_members_to_list("id", org_members, website_people_ids)

    # Getting Person Info
    ## Now that we know the different people's ids, finding their information.
    members = []
    print(f"Total of {len(different_terms)} missing from the desired people's page.")
    id_person_api = hpc.HelsinkiAPICall()
    for person_id in different_terms:
        id_person_api.add_parameters(person_id=person_id)
        members.append(id_person_api.binary_int_search()["fullname"])

    if members:
        # Email Message
        recipient = args.email_recipient
        subject = f"{datetime.today().strftime("%Y-%m")} Update on Social Data Science Centre Members"
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
        hpc.plaintext_sendmail(recipient=recipient, subject=subject, message=message, sender=args.email_sender,
                               sendmail_loc=args.sendmail_loc)
