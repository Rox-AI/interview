import pandas as pd
from openai import OpenAI
from dataclasses import dataclass
from pprint import pprint
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "<insert key here>"

LLM_PROMPT = """
You are given a search query on people and company and you need to convert it into structured filters, an optional ordering, and an optional limit on number of results.

Here are the list of allowed columns to filter on:
* company_domain - e.g. google.com
* job_title - e.g. CEO
* seniority - e.g. C-Level
* city_person - e.g. San Francisco
* state_person - e.g. CA
* country_person - e.g. USA
* num_followers - e.g. 1000
* name_company - e.g. Google
* city_company - e.g. Los Gatos
* state_company - e.g. CA
* country_company - e.g. USA
* industry - e.g. Education
* employee_count - e.g. 5000
* revenue - e.g. 1000000
* start_date - e.g. 2023-10-01

If the search query mentions job title, you should find the closest match to one of the following job titles:
* {JOB_TITLES}

If the search query mentions seniority, you should find the closest match to one of the following seniorities:
* {SENIORITIES}

If the search query mentions industry, you should find the closest match to one of the following industries:
* {INDUSTRIES}



You should output a list of filters, an optional ordering, and an optional limit.
Filters should always be of this form:
FILTER <column> <operator> <value>

Example filters:
FILTER company_domain = google.com
FILTER num_followers > 1000

Ordering should be of this format:
ORDER <column> <asc OR desc>

Example ordering:
ORDER num_followers asc

There should only be one ordering.

Limit should be of this format:
LIMIT <number of results>

Example limit:
LIMIT 10


=============================
Example input query:

Give me up to 10 people that work in the Education industry and live in San Francisco. I want the people with the most followers.

Example output:
FILTER industry = Education
FILTER city_person = San Francisco
ORDER num_followers desc
LIMIT 10

==============================
Now it's your turn.

Input query:

{INPUT_QUERY}

Output:"""


@dataclass
class Clause:
    clause_type: str
    column: str = ""
    operator: str = ""  # only for filter
    value: str = ""


def get_combined_df(base_dir="data") -> pd.DataFrame:
    companies = pd.read_csv(f"{base_dir}/companies.csv")
    people = pd.read_csv(f"{base_dir}/people.csv")
    combined = pd.merge(
        left=people,
        right=companies,
        how="left",
        left_on=["company_id"],
        right_on=["id"],
        suffixes=("_person", "_company"),
    )
    return combined


def _parse_content(raw_llm_output: str) -> list[Clause]:
    clauses = []
    for line in raw_llm_output.split("\n"):
        split = line.split()

        if split[0] == "FILTER":
            clauses.append(
                Clause(
                    clause_type=split[0],
                    column=split[1],
                    operator=split[2],
                    value=" ".join(split[3:]),
                )
            )
        elif split[0] == "ORDER":
            clauses.append(
                Clause(
                    clause_type=split[0],
                    column=split[1],
                    operator=split[2],
                )
            )
        elif split[0] == "LIMIT":
            clauses.append(
                Clause(
                    clause_type=split[0],
                    value=split[1],
                )
            )
        else:
            print("Can't parse split: ", line)

    return clauses


def convert_query_to_clauses(
    combined_df: pd.DataFrame, input_query: str
) -> list[Clause]:
    client = OpenAI()

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": LLM_PROMPT.format(
                    JOB_TITLES="\n* ".join(combined_df.job_title.unique()),
                    SENIORITIES="\n* ".join(combined_df.seniority.unique()),
                    INDUSTRIES="\n* ".join(combined_df.industry.unique()[:-1]),
                    INPUT_QUERY=input_query,
                ),
            }
        ],
    )

    content = result.choices[0].message.content
    clauses = _parse_content(content)

    pprint(clauses)

    return clauses


def apply_clauses(combined_df: pd.DataFrame, clauses: list[Clause]) -> pd.DataFrame:
    result_df = combined_df
    for clause in clauses:
        if clause.clause_type == "FILTER":
            if clause.operator == "=":
                result_df = result_df[getattr(result_df, clause.column) == clause.value]
            elif clause.operator == ">":
                result_df = result_df[getattr(result_df, clause.column) > clause.value]
            elif clause.operator == "<":
                result_df = result_df[getattr(result_df, clause.column) < clause.value]
            elif clause.operator == ">=":
                result_df = result_df[getattr(result_df, clause.column) >= clause.value]
            elif clause.operator == "<=":
                result_df = result_df[getattr(result_df, clause.column) <= clause.value]
            else:
                print("Can't parse!!!")
        elif clause.clause_type == "ORDER":
            result_df.sort_values(
                by=[clause.column], ascending=(clause.operator == "asc")
            )
        else:
            result_df = result_df.head(int(clause.value))

    return result_df


def get_filtered_df(combined_df: pd.DataFrame, input_query: str) -> pd.DataFrame:
    clauses = convert_query_to_clauses(combined_df, input_query)
    result_df = apply_clauses(combined_df, clauses)
    return result_df


if __name__ == "__main__":
    input_query = "Who are the Chief Executive Officers of the top 5 healthcare companies by revenue?"
    # input_query = "I want 10 PMs from San Francisco who have started since August 2024"
    # input_query = "Give me all the people at the level of Vice President that work at Googol"

    combined_df = get_combined_df()
    filtered_df = get_filtered_df(combined_df, input_query)
    filtered_df.to_csv("output_df.csv", index=False)

    print("OUTPUT to {input_query}:\n", filtered_df.to_markdown())
