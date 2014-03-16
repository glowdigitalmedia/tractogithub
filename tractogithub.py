import psycopg2
import argparse
import json
import datetime
from pygithub3 import Github

parser = argparse.ArgumentParser(description='Trac tickets to GitHub Issues migration tool.')
parser.add_argument('--dbname', help='Database name')
parser.add_argument('--dbuser', help='Database user')
parser.add_argument('--dbpassword', help='Database password')
parser.add_argument('--ghtoken', help='GitHub token')
parser.add_argument('--ghuser', help='GitHub user')
parser.add_argument('--ghrepo', help='GitHub repository')
parser.add_argument('--users', help='Users map JSON file (users.json)')
args = parser.parse_args()

# Load users map from a .json file
# the file must contain a key->value map with trac_user->github_user
# so the Issues can be assigned properly

if args.users:
    users_json_data = open(args.users).read()
    users_map = json.loads(users_json_data)

# Initialize the GitHub API with access token, user and repository
gh = Github(token=args.ghtoken, user=args.ghuser, repo=args.ghrepo)

connection = psycopg2.connect(dbname=args.dbname, user=args.dbuser, password=args.dbpassword)
cursor = connection.cursor()

# Get all the Milestones from Trac
cursor.execute("SELECT name, description, due, completed FROM milestone;")

milestones_map = {}

for name, description, due, completed in cursor:
    milestone = dict(title=name, description=description)

    if int(due) > 0:
        # Convert the date from trac in64 format to GitHub ISO 8601
        mil_due = datetime.datetime.utcfromtimestamp(int(str(due)[:-6])).isoformat()
        milestone["due_on"] = mil_due

    if int(completed) > 0:
        milestone["state"] = "closed"

    gh_milestone = gh.issues.milestones.create(milestone)

    # Create a temporary Milestones map that we will use later when creating tickets
    milestones_map[name] = gh_milestone.number
    print gh_milestone

# Create missing Labels on Issues
gh.issues.labels.create(dict(name='task', color='FFAA00'))
gh.issues.labels.create(dict(name='concern', color='009999'))
gh.issues.labels.create(dict(name='requirement', color='00B25C'))

# Get all the Tickets from Trac
cursor.execute("SELECT id, summary, description, owner, milestone, component, status, type FROM ticket ORDER BY id;")

# Will use this cursor to query comments for each Ticket
comments_cursor = connection.cursor()

for ticket_id, summary, description, owner, milestone, component, status, ticket_type in cursor:
    issue = dict(title=summary, body=description)

    if args.users:
        if owner != '':
            if users_map.has_key(owner):
                issue["assignee"] = users_map.get(owner)

    if milestone != '':
        if milestones_map.has_key(milestone):
            issue["milestone"] = milestones_map.get(milestone)

    gh_issue = gh.issues.create(issue)

    if ticket_type == 'defect':
        gh.issues.labels.add_to_issue(gh_issue.number, 'bug')
    if ticket_type == 'task':
        gh.issues.labels.add_to_issue(gh_issue.number, 'task')
    if ticket_type == 'enhancement':
        gh.issues.labels.add_to_issue(gh_issue.number, 'enhancement')
    if ticket_type == 'concern':
        gh.issues.labels.add_to_issue(gh_issue.number, 'concern')
    if ticket_type == 'requirement':
        gh.issues.labels.add_to_issue(gh_issue.number, 'requirement')

    comments_sql = 'SELECT author, newvalue AS body FROM ticket_change WHERE field=%s AND ticket=%s'
    comments_data = ("comment", str(ticket_id))
    comments_cursor.execute(comments_sql, comments_data)

    if status == 'closed':
        gh.issues.update(gh_issue.id, dict(title=gh_issue.title, state='closed'))

    print gh_issue

# Close used cursors and database connection
comments_cursor = connection.cursor()
cursor.close()
connection.close()
