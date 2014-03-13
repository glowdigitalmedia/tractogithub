import psycopg2
import argparse

parser = argparse.ArgumentParser(description='Trac tickets to GitHub Issues migration tool.')
parser.add_argument('--dbname', help='Database name')
parser.add_argument('--dbuser', help='Database user')
parser.add_argument('--dbpassword', help='Database password')
args = parser.parse_args()

connection = psycopg2.connect(dbname=args.dbname, user=args.user, password=args.password)
cur = connection.cursor()
