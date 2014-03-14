import psycopg2
import argparse
from pygithub3 import Github

parser = argparse.ArgumentParser(description='Trac tickets to GitHub Issues migration tool.')
parser.add_argument('--dbname', help='Database name')
parser.add_argument('--dbuser', help='Database user')
parser.add_argument('--dbpassword', help='Database password')
parser.add_argument('--ghtoken', help='GitHub token')
parser.add_argument('--ghuser', help='GitHub user')
parser.add_argument('--ghrepo', help='GitHub repository')
args = parser.parse_args()

connection = psycopg2.connect(dbname=args.dbname, user=args.dbuser, password=args.dbpassword)
cursor = connection.cursor()
cursor.execute("SELECT id, summary, description , owner, milestone, component, status FROM ticket ORDER BY id;")

for row in cursor:
	print row

cursor.close()
connection.close()

gh = Github(token='*******************************************', user='andreagrandi', repo='andrea_test1')
gh.issues.create(dict(title='My test issue', body='This needs to be fixed ASAP.', assignee='andreagrandi'))
