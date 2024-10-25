#!/usr/bin/env python3
# Emergent git auto timesheet v3
# Created by: Ashwin Kochiyil Philips, Emergent Solutions
# Date: 2024-10-25

"""
This script provides functionality to generate an automated timesheet based on Git commit history.
It analyzes commit patterns to estimate work hours and productivity for contributors in a Git repository.
"""


import git
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# F0: Atomic Operations
def get_repo(repo_path):
    """
    F0: Initialize and return a Git repository object.
    """
    try:
        repo = git.Repo(repo_path)
        return repo
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: {repo_path} is not a valid Git repository.")
        exit(1)

def get_commits(repo, branches=None):
    """
    F0: Retrieve all commits from the repository.
    Optionally filter by branches.
    """
    commits = []
    if branches:
        for branch in branches:
            commits.extend(repo.iter_commits(branch))
    else:
        commits = list(repo.iter_commits('--all'))
    return commits

def parse_commit(commit):
    """
    F0: Parse commit information.
    """
    return {
        'author': commit.author.name,
        'email': commit.author.email,
        'timestamp': datetime.datetime.fromtimestamp(commit.committed_date),
        'message': commit.message.strip(),
        'hexsha': commit.hexsha,
        'branch': get_commit_branch(commit),
    }

def get_commit_branch(commit):
    """
    F0: Get the branch name for a commit.
    """
    # This is a complex operation; for simplicity, we'll set it to None
    # as determining the branch from a commit is non-trivial in Git.
    return None

# F1: Simple Functions
def extract_commit_info(commits):
    """
    F1: Extract information from a list of commits.
    """
    commit_data = []
    for commit in commits:
        data = parse_commit(commit)
        commit_data.append(data)
    return commit_data

def filter_commits(commit_data):
    """
    F1: Filter out commits that do not contribute to meaningful time analysis.
    """
    filtered_commits = []
    for data in commit_data:
        if not data['message'].startswith('Merge'):
            filtered_commits.append(data)
    return filtered_commits

# F2: Aggregated Functions
def group_commits_by_contributor(commit_data):
    """
    F2: Group commits by contributor.
    """
    contributor_commits = defaultdict(list)
    for data in commit_data:
        contributor = data['author']
        contributor_commits[contributor].append(data)
    return contributor_commits

def group_commits_by_branch(commit_data):
    """
    F2: Group commits by branch.
    """
    branch_commits = defaultdict(list)
    for data in commit_data:
        branch = data['branch'] if data['branch'] else 'Unknown'
        branch_commits[branch].append(data)
    return branch_commits

def sort_commits_by_timestamp(contributor_commits):
    """
    F2: Sort commits by timestamp for each contributor.
    """
    for contributor in contributor_commits:
        contributor_commits[contributor].sort(key=lambda x: x['timestamp'])
    return contributor_commits

# F3: Higher-Level Analysis
def calculate_active_work_time(contributor_commits, time_threshold_hours=4):
    """
    F3: Calculate active work time per contributor.
    """
    active_work_time = {}
    threshold = datetime.timedelta(hours=time_threshold_hours)
    for contributor, commits in contributor_commits.items():
        total_time = datetime.timedelta()
        previous_time = None
        for data in commits:
            current_time = data['timestamp']
            if previous_time is not None:
                delta = current_time - previous_time
                if delta <= threshold:
                    total_time += delta
            previous_time = current_time
        active_work_time[contributor] = total_time.total_seconds() / 3600.0  # Convert to hours
    return active_work_time

def split_time_periods(commit_data):
    """
    F3: Split commit data into different time periods.
    """
    periods = {'week': {}, 'month': {}, 'year': {}}
    for data in commit_data:
        timestamp = data['timestamp']
        week = timestamp.isocalendar()[1]
        month = timestamp.month
        year = timestamp.year

        key_week = f"{year}-W{week}"
        key_month = f"{year}-M{month}"
        key_year = f"{year}"

        periods['week'].setdefault(key_week, []).append(data)
        periods['month'].setdefault(key_month, []).append(data)
        periods['year'].setdefault(key_year, []).append(data)
    return periods

def calculate_time_by_commit(contributor_commits, time_threshold_hours=4):
    """
    F3: Calculate time spent between commits for each contributor.
    """
    commit_times = []
    threshold = datetime.timedelta(hours=time_threshold_hours)
    for contributor, commits in contributor_commits.items():
        previous_time = None
        previous_commit = None
        for data in commits:
            current_time = data['timestamp']
            if previous_time is not None:
                delta = current_time - previous_time
                if delta <= threshold:
                    commit_times.append({
                        'contributor': contributor,
                        'time_spent': delta.total_seconds() / 3600.0,
                        'commit_message': previous_commit['message'],
                        'timestamp': previous_commit['timestamp'],
                    })
            previous_time = current_time
            previous_commit = data
    # Sort by time_spent descending
    commit_times.sort(key=lambda x: x['time_spent'], reverse=True)
    return commit_times

# F4: Complex Data Modeling
def generate_timesheet(active_work_time, periods, commit_times):
    """
    F4: Generate timesheet data.
    """
    timesheet_entries = []
    for contributor, hours in active_work_time.items():
        timesheet_entries.append({
            'Contributor': contributor,
            'Total Hours': round(hours, 2),
        })
    # Further processing for timesheet formats can be added here
    return timesheet_entries

def combine_repositories(repo_paths, branches=None):
    """
    F4: Combine commit data from multiple repositories.
    """
    combined_commits = []
    for repo_path in repo_paths:
        repo = get_repo(repo_path)
        commits = get_commits(repo, branches)
        commit_data = extract_commit_info(commits)
        filtered_data = filter_commits(commit_data)
        combined_commits.extend(filtered_data)
    return combined_commits

# F5+: Advanced Insights
def display_results(active_work_time, commit_times):
    """
    F5+: Display the total active work hours per contributor and time by commit.
    """
    total_hours = sum(active_work_time.values())
    print("\nTotal Active Work Hours: {:.2f} hours".format(total_hours))
    print("\nHours per Contributor:")
    print("----------------------")
    for contributor, hours in active_work_time.items():
        print(f"{contributor}: {hours:.2f} hours")

    print("\nTime by Commit (Most Time at Top):")
    print("---------------------------------")
    for entry in commit_times[:10]:  # Show top 10
        print(f"{entry['contributor']} spent {entry['time_spent']:.2f} hours on commit '{entry['commit_message']}' at {entry['timestamp']}")

def output_timesheet(timesheet_entries):
    """
    F5+: Output timesheet in standard agency format.
    """
    df = pd.DataFrame(timesheet_entries)
    df.to_csv('timesheet.csv', index=False)
    print("\nTimesheet saved to 'timesheet.csv'.")

def main(repo_paths, branches=None):
    """
    Main function to compute git-hours and perform advanced analysis.
    """
    print("Combining repositories...")
    commit_data = combine_repositories(repo_paths, branches)

    print("Grouping commits by contributor...")
    contributor_commits = group_commits_by_contributor(commit_data)

    print("Sorting commits by timestamp...")
    contributor_commits = sort_commits_by_timestamp(contributor_commits)

    print("Calculating active work time...")
    active_work_time = calculate_active_work_time(contributor_commits)

    print("Splitting time periods...")
    periods = split_time_periods(commit_data)

    print("Calculating time by commit...")
    commit_times = calculate_time_by_commit(contributor_commits)

    display_results(active_work_time, commit_times)

    print("Generating timesheet...")
    timesheet_entries = generate_timesheet(active_work_time, periods, commit_times)
    output_timesheet(timesheet_entries)

    # Additional functionalities like hours by branch can be added here.

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Compute git-hours per contributor and perform advanced analysis.')
    parser.add_argument('repo_paths', nargs='+', help='Paths to the Git repositories.')
    parser.add_argument('--branches', nargs='*', help='Specific branches to analyze.')
    args = parser.parse_args()
    main(args.repo_paths, args.branches)
