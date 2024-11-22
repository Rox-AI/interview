import csv
import random
from itertools import chain
from datetime import datetime
from faker import Faker
from typing import List, Dict

fake = Faker()

# Constants
INDUSTRIES = [
    "Technology",
    "Finance",
    "Healthcare",
    "Retail",
    "Manufacturing",
    "Education",
    "Real Estate",
]

LOCATIONS = [
    ("San Francisco", "CA", "USA"),
    ("New York", "NY", "USA"),
    ("Chicago", "IL", "USA"),
    ("Boston", "MA", "USA"),
    ("Seattle", "WA", "USA"),
    ("Austin", "TX", "USA"),
    ("Los Angeles", "CA", "USA"),
    ("Miami", "FL", "USA"),
    ("London", "England", "UK"),
    ("Paris", "", "France"),
]

KNOWN_COMPANIES = [
    ("Googol", "googol.com", "San Francisco", "CA", "USA"),
    ("Netflicks", "netflicks.com", "Los Gatos", "CA", "USA"),
    ("Orange", "orange.com", "Cupertino", "CA", "USA"),
    ("Jumbohard", "jumbohard.com", "Seattle", "WA", "USA"),
    ("AirDNT", "airdnt.com", "San Francisco", "CA", "USA"),
]

JOB_TITLES = {
    "c-level": ["CEO", "CTO"],
    "vp": [
        "VP of Sales",
        "VP of Marketing",
        "VP of Product",
        "VP of Engineering",
    ],
    "director": [
        "Director of Sales",
        "Director of Marketing",
        "Director of Product",
        "Director of Engineering",
    ],
    "manager": [
        "Sales Manager",
        "Marketing Manager",
        "Product Manager",
        "Engineering Manager",
    ],
    "non-manager": [
        "Software Engineer",
        "Data Analyst",
        "Account Executive",
        "Sales Development Representative",
        "Sales Operations Manager",
        "Marketing Specialist",
        "Content Marketing Manager",
        "Digital Marketing Specialist",
        "Product Designer",
        "UX Designer",
        "UI Designer",
        "DevOps Engineer",
        "QA Engineer",
        "Data Scientist",
        "Business Analyst",
        "HR Manager",
        "Recruiter",
        "Operations Manager",
        "Customer Success Manager",
        "Account Manager",
        "Finance Manager",
        "Accountant",
    ],
}


def get_seniority(role: str) -> str:
    if role in JOB_TITLES["c-level"]:
        return "C-Level"
    elif role in JOB_TITLES["vp"]:
        return "VP"
    elif role in JOB_TITLES["director"]:
        return "Director"
    elif role in JOB_TITLES["manager"]:
        return "Manager"
    else:
        return "Non-Manager"


def generate_company_name() -> str:
    return fake.company().replace(" ", "").replace(",", "").replace(".", "")


def generate_domain(company_name: str) -> str:
    return f"{company_name.lower()}.com"


def generate_companies(num_companies: int) -> List[Dict]:
    companies = []
    company_id = 1

    # First add known companies
    for name, domain, city, state, country in KNOWN_COMPANIES:
        companies.append(
            {
                "id": company_id,
                "domain": domain,
                "name": name,
                "city": city,
                "state": state,
                "country": country,
                "industry": random.choice(INDUSTRIES),
                "employee_count": random.randint(1000, 10000),
                "revenue": random.randint(100000000, 1000000000),
            }
        )
        company_id += 1

    # Generate remaining companies
    for _ in range(num_companies - len(KNOWN_COMPANIES)):
        name = generate_company_name()
        location = random.choice(LOCATIONS)
        companies.append(
            {
                "id": company_id,
                "domain": generate_domain(name),
                "name": name,
                "city": location[0],
                "state": location[1],
                "country": location[2],
                "industry": random.choice(INDUSTRIES),
                "employee_count": random.randint(5, 100),
                "revenue": random.randint(100000, 10000000),
            }
        )
        company_id += 1

    return companies


def generate_people(companies: List[Dict], num_people_per_company: int) -> List[Dict]:
    people = []
    person_id = 1

    for company in companies:
        # Assign unique roles first
        num_unique_roles = 0
        for role in chain(JOB_TITLES["c-level"], JOB_TITLES["vp"]):
            people.append(
                {
                    "id": person_id,
                    "name": fake.name(),
                    "company_id": company["id"],
                    "company_domain": company["domain"],
                    "job_title": role,
                    "seniority": get_seniority(role),
                    "city": company["city"],
                    "state": company["state"],
                    "country": company["country"],
                    "num_followers": random.randint(1000, 10000),
                    "start_date": fake.date_between(
                        start_date=datetime(2022, 1, 1), end_date=datetime(2024, 11, 1)
                    ).strftime("%Y-%m-%d"),
                }
            )
            person_id += 1
            num_unique_roles += 1

        # Generate remaining employees
        remaining_count = num_people_per_company - num_unique_roles
        all_other_roles = (
            JOB_TITLES["director"] + JOB_TITLES["manager"] + JOB_TITLES["non-manager"]
        )

        for _ in range(remaining_count):
            # 80% chance to use company location, 20% chance for random location
            if random.random() < 0.8:
                city = company["city"]
                state = company["state"]
                country = company["country"]
            else:
                random_location = random.choice(LOCATIONS)
                city = random_location[0]
                state = random_location[1]
                country = random_location[2]

            role = random.choice(all_other_roles)
            people.append(
                {
                    "id": person_id,
                    "name": fake.name(),
                    "company_id": company["id"],
                    "company_domain": company["domain"],
                    "job_title": role,
                    "seniority": get_seniority(role),
                    "city": city,
                    "state": state,
                    "country": country,
                    "num_followers": random.randint(50, 5000),
                    "start_date": fake.date_between(
                        start_date=datetime(2022, 1, 1), end_date=datetime(2024, 11, 1)
                    ).strftime("%Y-%m-%d"),
                }
            )
            person_id += 1
    return people


def write_csv(filename: str, data: List[Dict]):
    if not data:
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def main():
    num_companies = 1000
    num_people_per_company = 100

    companies = generate_companies(num_companies)
    people = generate_people(companies, num_people_per_company)

    write_csv("companies.csv", companies)
    write_csv("people.csv", people)


if __name__ == "__main__":
    main()

