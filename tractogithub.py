import psycopg2
import argparse
import json
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
users_json_data = open(args.users).read()
users_map = json.loads(users_json_data)

# Initialize the GitHub API with access token, user and repository
gh = Github(token=args.ghtoken, user=args.ghuser, repo=args.ghrepo)

connection = psycopg2.connect(dbname=args.dbname, user=args.dbuser, password=args.dbpassword)
cursor = connection.cursor()
cursor.execute("SELECT id, summary, description , owner, milestone, component, status FROM ticket ORDER BY id;")

for row in cursor:
	print row

cursor.close()
connection.close()


gh.issues.create(dict(title='My test issue', body='This needs to be fixed ASAP.', assignee='andreagrandi'))
