#!/usr/bin/env python3
# Emergent git auto timesheet
# Created by: Ashwin Kochiyil Philips, Emergent Solutions
# Date: 2024-10-25

"""
This script provides functionality to generate an automated timesheet based on Git commit history.
It analyzes commit patterns to estimate work hours and productivity for contributors in a Git repository.
"""

import git
import datetime
from collections import defaultdict

def get_repo(repo_path):
    """
    Initialize and return a Git repository object.

    Args:
        repo_path (str): Path to the Git repository.

    Returns:
        git.Repo: GitPython repository object.
    """
    try:
        repo = git.Repo(repo_path)
        return repo
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: {repo_path} is not a valid Git repository.")
        exit(1)

def get_commits(repo):
    """
    Retrieve all commits from the repository.

    Args:
        repo (git.Repo): GitPython repository object.

    Returns:
        list of git.Commit: List of commit objects.
    """
    return list(repo.iter_commits())

def parse_commit(commit):
    """
    Parse commit information.

    Args:
        commit (git.Commit): Commit object.

    Returns:
        dict: Dictionary containing commit data.
    """
    return {
        'author': commit.author.name,
        'email': commit.author.email,
        'timestamp': datetime.datetime.fromtimestamp(commit.committed_date),
        'message': commit.message,
        'hexsha': commit.hexsha
    }

def extract_commit_info(commits):
    """
    Extract information from a list of commits.

    Args:
        commits (list of git.Commit): List of commit objects.

    Returns:
        list of dict: List of commit data dictionaries.
    """
    commit_data = []
    for commit in commits:
        data = parse_commit(commit)
        commit_data.append(data)
    return commit_data

def filter_commits(commit_data):
    """
    Filter out commits that do not contribute to meaningful time analysis.

    Args:
        commit_data (list of dict): List of commit data dictionaries.

    Returns:
        list of dict: Filtered list of commit data dictionaries.
    """
    filtered_commits = []
    for data in commit_data:
        if not data['message'].startswith('Merge'):
            filtered_commits.append(data)
    return filtered_commits

def group_commits_by_contributor(commit_data):
    """
    Group commits by contributor.

    Args:
        commit_data (list of dict): List of commit data dictionaries.

    Returns:
        dict: Dictionary with contributor as key and list of commits as value.
    """
    contributor_commits = defaultdict(list)
    for data in commit_data:
        contributor = data['author']
        contributor_commits[contributor].append(data)
    return contributor_commits

def sort_commits_by_timestamp(contributor_commits):
    """
    Sort commits by timestamp for each contributor.

    Args:
        contributor_commits (dict): Dictionary with contributor as key and list of commits as value.

    Returns:
        dict: Dictionary with contributor as key and sorted list of commits.
    """
    for contributor in contributor_commits:
        contributor_commits[contributor].sort(key=lambda x: x['timestamp'])
    return contributor_commits

def calculate_active_work_time(contributor_commits, time_threshold_hours=4):
    """
    Calculate active work time per contributor.

    Args:
        contributor_commits (dict): Dictionary with contributor as key and sorted list of commits.
        time_threshold_hours (int, optional): Threshold in hours to define active work sessions.

    Returns:
        dict: Dictionary with contributor as key and total active work time in hours.
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

def display_results(active_work_time):
    """
    Display the total active work hours per contributor.

    Args:
        active_work_time (dict): Dictionary with contributor as key and total active work time in hours.
    """
    print("\nTotal Active Work Hours per Contributor:")
    print("---------------------------------------")
    for contributor, hours in active_work_time.items():
        print(f"{contributor}: {hours:.2f} hours")

def main(repo_path):
    """
    Main function to compute git-hours.

    Args:
        repo_path (str): Path to the Git repository.
    """
    print("Initializing repository...")
    repo = get_repo(repo_path)

    print("Retrieving commits...")
    commits = get_commits(repo)

    print("Extracting commit information...")
    commit_data = extract_commit_info(commits)

    print("Filtering commits...")
    commit_data = filter_commits(commit_data)

    print("Grouping commits by contributor...")
    contributor_commits = group_commits_by_contributor(commit_data)

    print("Sorting commits by timestamp...")
    contributor_commits = sort_commits_by_timestamp(contributor_commits)

    print("Calculating active work time...")
    active_work_time = calculate_active_work_time(contributor_commits)

    display_results(active_work_time)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Compute git-hours per contributor.')
    parser.add_argument('repo_path', help='Path to the Git repository.')
    args = parser.parse_args()
    main(args.repo_path)

