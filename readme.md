# SLMCF for Git-Hours Analysis

## F0: Atomic Operations

These are the basic, irreducible operations. In the context of git-hours, F0 operations include:

- **Time Calculation**: Basic date-time calculations, e.g., time differences between two commits.
- **Git Command Execution**: Running individual Git commands (e.g., git log, git diff) to extract commit metadata.
- **Data Parsing**: Parsing commit data, timestamps, and contributor details.

## F1: Simple Functions (Built on F0)

This layer aggregates F0 operations into simple utility functions that allow direct data manipulation:

- **Extract Commit Information**: Use git log to retrieve commit metadata (author, timestamp, message) and parse it.
- **Calculate Time per Commit**: Using timestamps to calculate the time spent between commits by the same contributor.
- **Filter Commits by Contributor**: Identify and group commits by contributor for isolated analysis.
- **Basic Filtering**: Filter out commits that may not contribute to meaningful time analysis (e.g., merge commits).

## F2: Aggregated Functions (Based on F1)

At this level, we aggregate F1 functions to perform meaningful operations over the dataset:

- **Calculate Total Hours per Contributor**: Summing up time spent by each contributor based on commit timestamps.
- **Commit Frequency Analysis**: Calculate commit frequency for each contributor to estimate productivity patterns.
- **Day/Week Filtering**: Aggregate commits by day, week, or other intervals for trend analysis.
- **Basic Time Thresholding**: Set a threshold to define and ignore idle times between commits, ensuring that only active coding periods are considered.

## F3: Higher-Level Analysis

At F3, we use F2 aggregates to produce more complex insights. Minimal novelty is applied to keep functions straightforward:

- **Estimate Active Work Hours**: Filter commit data to estimate active work periods, ignoring long gaps.
- **Determine Contribution Impact**: Weight commits by factors like file changes, size of diffs, etc., to estimate contribution significance.
- **Calculate Cumulative Git Hours**: Aggregate active work hours per contributor and per project over custom time periods.
- **Trend Analysis**: Identify productivity trends over time (e.g., peak work hours, high-output periods).

## F4: Complex Data Modeling (Using F3)

This level combines multiple analyses to create a holistic view of git-hours data:

- **Identify Productivity Patterns**: Detect patterns like most productive hours, weekly work cycles, or irregular work times for each contributor.
- **Heatmap Visualization Data**: Prepare data for a time-based heatmap, showing concentration of activity per hour, day, or week.
- **Role-Based Analysis**: Segment analysis based on different roles if metadata allows, e.g., differentiating between developer, reviewer, etc.

## F5+: Advanced Insights and Cross-Functionality (Based on F4)

Here, we add advanced insights while cross-pollinating functionality for future extensibility.

- **Predictive Modeling**: Use patterns to predict future productivity and active hours for contributors.
- **Comparative Analytics**: Compare productivity trends across different repositories or teams.
- **Automated Reporting**: Generate weekly or monthly summaries of git-hours and productivity patterns.
- **API Integration**: Enable integrations with external systems (e.g., Slack notifications for productivity milestones).

## Summary

The SLMCF for git-hours analysis organizes functionalities in a layered manner, where each level is minimally complex, self-leveling, and modular. This approach ensures scalability for advanced insights while keeping atomic operations independent and foundational.

Code Overview
The code is structured according to the SLMCF methodology, with each function corresponding to different levels:

F0: Atomic Operations
Time Calculation: Handled by Python's datetime module.
Git Command Execution: Managed by gitpython library.
Data Parsing: Parsing commit data using basic Python data structures.

F1: Simple Functions
get_repo(repo_path): Initializes the Git repository.
get_commits(repo): Retrieves all commits.
parse_commit(commit): Extracts necessary information from a commit.
extract_commit_info(commits): Aggregates commit data into a list.

F2: Aggregated Functions
filter_commits(commit_data): Filters out non-meaningful commits like merge commits.
group_commits_by_contributor(commit_data): Groups commits by each contributor.
sort_commits_by_timestamp(contributor_commits): Sorts commits chronologically.
calculate_active_work_time(contributor_commits, time_threshold_hours): Calculates active work hours using a threshold to define work sessions.

F3: Higher-Level Analysis
display_results(active_work_time): Presents the calculated work hours in a readable format.
Main Execution Flow
The main function orchestrates the execution by calling the above functions in order, providing a clear flow from data retrieval to result presentation.
Customization
Time Threshold

The calculate_active_work_time function uses a default time threshold of 4 hours to define active work sessions. You can modify this threshold by changing the time_threshold_hours parameter.

python
Copy code
active_work_time = calculate_active_work_time(contributor_commits, time_threshold_hours=2)
Filtering Criteria

The filter_commits function currently filters out commits with messages starting with "Merge". You can customize this function to add more filtering criteria as needed.

Extensibility
This code provides a solid foundation and can be extended to include:

Trend Analysis

Add functions to analyze productivity trends over time.

Visualization

Integrate libraries like matplotlib or seaborn to visualize the data.

Role-Based Analysis

If contributor roles are identifiable, segment the analysis based on roles.

API Integration

Extend the script to send data to external systems or dashboards.

Conclusion
This script implements the git-hours functionality following the SLMCF methodology, ensuring that each component is minimal, self-contained, and builds upon the previous layers. It's fully documented and ready for further development or immediate use.

How to Use

Install Dependencies

Make sure you have Python 3 installed. Install the required packages using pip:

bash
Copy code
pip install -r requirements.txt
Run the Script

Navigate to the directory containing git_hours.py and run:

bash
Copy code
python git_hours.py /path/to/your/git/repository
Replace /path/to/your/git/repository with the actual path to the Git repository you want to analyze.
