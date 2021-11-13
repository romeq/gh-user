#!/bin/python3
# Request specified account's profile data from GitHub API and show them to user
#

import html
import requests
import sys

BASE_URL = "https://api.github.com"


class ApiEng:
    def __init__(self, username):
        self.username = username

    def get_basic(self):
        print("Requesting profile...")
        req = requests.get(f"{BASE_URL}/users/{html.escape(self.username)}")
        return req.json(), "message" in req.json()

    
    def get_repos(self):
        print("Requesting repositories")
        req = requests.get(
            f"{BASE_URL}/users/{html.escape(self.username)}/repos")
        return req.json(), "message" in req.json()


    def get_organizations(self):
        print("Requesting organizations...")
        req = requests.get(
            f"{BASE_URL}/users/{html.escape(self.username)}/orgs")
        return req.json(), "message" in req.json()


class DataHandler:
    def __init__(self, username, basic_data, repos, organizations):
        self.username = username
        self.basic = basic_data
        self.repos = repos
        self.git_organizations = organizations

    def handle_basic(self):
        self._print_field("\nUsername", self.basic['login'])
        self._print_field("Full name", self.basic['name'])
        self._print_field("Biography", self.basic['bio'])
        self._print_field("twitter", self.basic['twitter_username'])
        self._print_field("company", self.basic['company'])
        self._print_field("Public repos", self.basic['public_repos'])
        self._print_field("Public gists", self.basic['public_gists'])
        self._print_field("User created",
                          self._parse_time(self.basic['created_at']))

    def handle_repos(self):
        if len(self.repos) == 0:
            print("This user does not have any repositories!")
        else:
            print(f"\n{self.username}'s repositories")
            for repo_data in self.repos:
                self._print_field("\tRepository name", repo_data['name'])
                self._print_field("\tShort description", repo_data['description'])
                self._print_field("\tProject Language", repo_data['language'])
                print("")


    def handle_orgs(self):
        if len(self.git_organizations) == 0:
            print("This user is not in any organization!")
        else:
            print(f"\n{self.username}'s organizations")
            for org_data in self.git_organizations:
                self._print_field("\tOrganization name", org_data['login'])
                self._print_field("\tShort description",
                                  org_data['description'])
                self._print_field("\tProfile picture", org_data['avatar_url'])
                print("")

    @staticmethod  # helper for data handlers. makes more sense to be in this class than public
    def _print_field(field_name, field_data):
        if field_data is None:
            return  # prevents "null" fields from github api
        summary = f"{field_name}: \t {field_data}"
        print(summary)

    @staticmethod
    def _parse_time(data):
        # return parsed time
        return "".join(" ".join(data.split('T')).split('Z'))


def print_stderr(message):
    sys.stderr.write(f"{message}\n")


def print_help():
    print("Syntax: ./github_userinfo <username>")


def check_err(api_error, json_data):
    if api_error:
        print_stderr(f"Oopsie, GitHub API returned error: {json_data['message']}")
        sys.exit(1)


def get_user() -> str:
    if len(sys.argv) != 2:
        print_help()
        sys.exit(2)
    return sys.argv[1]


def run():
    username = get_user()
    gheng = ApiEng(username)

    # get data and check for api errors (rate limit etc.)
    (user_data, api_error) = gheng.get_basic()
    check_err(api_error, user_data)

    (org_data, api_error) = gheng.get_organizations()
    check_err(api_error, org_data)

    (repo_data, api_error) = gheng.get_repos()
    check_err(api_error, repo_data)

    # no errors, we can start handling the data
    data_handler = DataHandler(username, user_data, repo_data, org_data)
    data_handler.handle_basic()
    data_handler.handle_repos()
    data_handler.handle_orgs()

    return 0

if __name__ == "__main__":
    run()