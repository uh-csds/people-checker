
# Python Interface - Helsinki University People Finder

An API Class (HelsinkiAPICall) that allows for easier interaction with the [Helsinki University People Finder](https://www.helsinki.fi/en/api/people/contacts) system in Python.

## Example Functions

### Matching a Helsinki Webpage's Members to a Research Groups
The [Centre for Social Data Science (CSDS)](https://www.helsinki.fi/en/networks/centre-social-data-science/people) webpage has a list of members that requires manual updates. However, these change consistently, and the page may then miss new members of CSDS.

To fix this, I'll run code that will find who out who is considered to be a part of CSDS, compare it to the webpage, and then tell myself their names.

#### Getting Research Organization Members
To get the research organization members, we'll need to first create a base `HelsinkiAPICall` class. The class accepts a number of keyword arguments. An example is given below for a research organization call:
```
from helsinki_api_call import HelsinkiAPICall

research_org_api = HelsinkiAPICall(**{'researchOrganizations.id[]': 62060775})
```
Due to how the calls are set up, some API parameters require unpacking a dictionary or setting their values beforehand, as they cannot be entered as pure keywords. If you're interested in the possible People Finder API calls, they will be placed below in the appendix.

Above, I used an already known research organization key for CSDS. However, if you don't know the key, you can use the following code:
```
# Setting up new API call based on persons name
named_person_api = HelsinkiAPICall(fullname="Maria Valaste")

# Getting the first member, as there is only one Maria Valaste in the system.
# If you're interested in making sure that you're getting the correct person, you can use 'HelsinkiAPICall.get_member_info'
member = hapi.get_all_members(named_person_api.request_json())[0]

# Requesting the first research group.
# (if all_instances is true, will return all possible research groups. In this case, the group at the lowest administrative level is the one I want.)
research_org = hapi.get_member_info(member, search_term="researchOrganizations", all_instances=False)

# Research_org id
research_org["id"]
```
Member represents the dictionary given by the json. If you're interested in some more uses of get_member_info, they will also be stored in the appendix.

With this information in place, you can now get all of the research organization's members.

```
org_members = HelsinkiAPICall.get_all_members(research_org_api.request_json())
```

#### Scrapping a Helsinki Webpage
Sadly, the University's HTML only gives the person_ids, not the name. These can be converted later, however, into full names. For now, we can use `HelsinkiAPICall.scrape_helsinki_people_ids(url)` to get back a list of all Helsinki people that are on the webpage.

```
# The webpage we want to scrap from
desired_search_page = "https://www.helsinki.fi/en/networks/centre-social-data-science/people"

# Getting the list of ids
website_people_ids = HelsinkiAPICall.scrape_helsinki_people_ids(desired_search_page)
```
#### Matching the Terms
Now that we have `org_members` and `website_people_ids`, we can match them to see which ids are the same and which are different. The `members_list` keyword uses a list of member dictionaries, while `comparison_list` uses a list of the `search_term` you want to compare.
```
matching_terms, different_terms = HelsinkiPeopleAPI.compare_members_to_list(search_term="id", members_list=org_members, comparison_list=website_people_ids)
```
#### Discovering Their Names
`different_terms` will now give us a list of non-matching ids (such as `[900710, 900720]`) but those alone don't tell us much. We can use the `HelsinkiAPICall.binary_int_search()` to find what we're looking for.

```
for different_id in different_terms:
    id_person_api = HelsinkiAPICall(person_id = different_id)
    print(HelsinkiAPICall.binary_int_search())
```

The Helsinki People Finder does not actually allow you to search for ids on its own - this is why a binary search is done with the sort function. The code above is therefore the same as:

```
for different_id in different_terms:
    id_person_api = HelsinkiAPICall(sort = id)
    print(HelsinkiAPICall.binary_int_search(different_id))
```
Both work, depending on your preference.

### Base API Interactions
There are some other possibilities that the class can handle. For example:
#### Creating a Child Class
If there is ever a reason to create a new child class using the existing parameters of your base class, you can use `.create_child_api()`

```
base_api = HelsinkiAPICall(sort = id)

# Creating a child_api that uses sort = id and adds on its own keyword.
child_api = base_api.create_child_api(page = 252)
```

#### Getting Page Range
If you're interested in just getting the page range for a specific sort function, you can do the following:

```
base_api = HelsinkiAPICall(sort = researchOrganizations)
first_page, last_page = base_api.gather_page_range()
```

#### Other Possible Commands
```
base_api.remove_parameters(sort) # Removes parameter(s).

base_api.add_parameters(sort=id, page=124) # Adds a new parameter(s) to the keywords.

base_api.get_param(page) # Gets the value for a specific parameter
 (i.e. 124 here)

base_api.request_json() # Gets the json result from the API call.
```



## Appendix

For calling the Helsinki People Finder API, you can use the following commands:

```
sort: Sorts by a given parameter (i.e. id, name)

fullname: Finds a desired full name - and specifically only that name.

name: Finds a desired name. Unlike fullname, does a search among similar names as well.

firstnames: Finds a desired first name(s).

lastname/email/mobileNumber/phoneNumber: Finds a desired last name/email/mobile number/work number

organizations.id[]: Finds a desired department/faculty by organization id (includes only main organizations, like "Department of Philosophy, History and Art Studies").

researchOrganizations.id[]: Finds a desired research group by organzation id (includes everything in organzations.id[] - with the same groups having the same ids - but can include things like Helsinki Institute of Sustainability Science).

title.id[]: Finds a desired title by id, such as "Senior University Lecturer" or "Professor".

fieldsOfScience.value.id[]: Finds a desired field by id, such as "Statistics and probability".

search: Allows you to search for any value that is similar to the one you're looking for.

-----

primary_organizations.id[], primary_research_organizations.id[], servicingOrganizations.id[]: Exists, but am uncertain of use, as there is no "primary_organizations" or "servicingOrganziations" category under a member person.

steeringGroups.id[], hrOrganizations.id[]: Exist under a person, but have no values, even for people who I know are in these, so am uncertain if they are used.

description, publicWorkDescription, currentStatus: Do have values under a person, but searching directly doesn't appear to give anything.

limit: No clear use as of now.
```

Additionally, when dealing with a member dictionary, you can use `.get_member_info(serach_term="")` with the following terms:

```
researchOrganizations: i.e., if a person is a member of the Centre for Social Data Science or part of the Faculty of Social Sciences. If all_instances is False, returns the lowest denomination (since Centre is a child of Faculty,  Centre returns instead of Faculty.)
title: (i.e., Professor)
fieldsOfScience: (i.e. Statistics and probability)
address: (i.e. work address)
steeringGroups, hrOrganizations: Appears unused.

Other terms that will return a value are:
firstnames, lastnames, fullname, email, mobilenumber, fullnumber, id, picture (link), description, publicWorkDescription, currentStatus

Others that I am not certain on, but may give a result, depending on the person:
twiterLink, linkedinLink, facebookLink, instagramLink, youtubeLink, personalLinks
```
