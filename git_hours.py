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
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

def generate_heatmap_data(commit_data):
    """
    Generate data for heatmap visualization.

    Args:
        commit_data (list of dict): List of commit data dictionaries.

    Returns:
        pandas.DataFrame: DataFrame suitable for heatmap generation.
    """
    data = []
    for commit in commit_data:
        timestamp = commit['timestamp']
        day_of_week = timestamp.weekday()  # Monday is 0 and Sunday is 6
        hour = timestamp.hour
        data.append({'day_of_week': day_of_week, 'hour': hour})

    df = pd.DataFrame(data)
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
    return heatmap_data

def plot_heatmap(heatmap_data, contributor=None):
    """
    Plot heatmap of commit activity.

    Args:
        heatmap_data (pandas.DataFrame): DataFrame containing heatmap data.
        contributor (str, optional): Name of the contributor. Defaults to None.
    """
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap='YlOrRd')
    plt.title(f'Commit Activity Heatmap {"for " + contributor if contributor else ""}')
    plt.xlabel('Hour of Day')
    plt.ylabel('Day of Week')
    plt.yticks(ticks=[0,1,2,3,4,5,6], labels=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], rotation=0)
    plt.show()

def identify_productivity_patterns(contributor_commits):
    """
    Identify productivity patterns for each contributor.

    Args:
        contributor_commits (dict): Dictionary with contributor as key and list of commits as value.

    Returns:
        dict: Dictionary with contributor as key and productivity patterns as value.
    """
    patterns = {}
    for contributor, commits in contributor_commits.items():
        data = []
        for commit in commits:
            timestamp = commit['timestamp']
            day_of_week = timestamp.weekday()
            hour = timestamp.hour
            data.append({'day_of_week': day_of_week, 'hour': hour})
        df = pd.DataFrame(data)
        patterns[contributor] = df
    return patterns

def plot_contributor_heatmaps(patterns):
    """
    Plot heatmaps for each contributor.

    Args:
        patterns (dict): Dictionary with contributor as key and DataFrame of commit times as value.
    """
    for contributor, df in patterns.items():
        heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        plot_heatmap(heatmap_data, contributor=contributor)

def generate_trend_analysis(commit_data):
    """
    Generate trend analysis data over time.

    Args:
        commit_data (list of dict): List of commit data dictionaries.

    Returns:
        pandas.DataFrame: DataFrame containing daily commit counts.
    """
    df = pd.DataFrame(commit_data)
    df['date'] = df['timestamp'].dt.date
    trend_data = df.groupby('date').size().reset_index(name='commit_count')
    return trend_data

def plot_trend_analysis(trend_data):
    """
    Plot trend analysis over time.

    Args:
        trend_data (pandas.DataFrame): DataFrame containing daily commit counts.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(trend_data['date'], trend_data['commit_count'], marker='o')
    plt.title('Commit Activity Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Commits')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def generate_report(active_work_time, trend_data):
    """
    Generate a summary report of git-hours and productivity patterns.

    Args:
        active_work_time (dict): Dictionary with contributor as key and total active work time in hours.
        trend_data (pandas.DataFrame): DataFrame containing daily commit counts.
    """
    print("\n=== Git Hours Report ===")
    display_results(active_work_time)
    print("\nOverall Commit Trend:")
    print(trend_data.describe())
    # More detailed report generation can be added here.

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
    Main function to compute git-hours and perform advanced analysis.

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

    print("Identifying productivity patterns...")
    patterns = identify_productivity_patterns(contributor_commits)
    plot_contributor_heatmaps(patterns)

    print("Generating trend analysis...")
    trend_data = generate_trend_analysis(commit_data)
    plot_trend_analysis(trend_data)

    print("Generating report...")
    generate_report(active_work_time, trend_data)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Compute git-hours per contributor and perform advanced analysis.')
    parser.add_argument('repo_path', help='Path to the Git repository.')
    args = parser.parse_args()
    main(args.repo_path)
