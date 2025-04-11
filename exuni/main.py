import gspread
from google.oauth2.service_account import Credentials
import database
import queries
import argparse
from pathlib import Path

def cli():
    parser = argparse.ArgumentParser(description="Query Student Feedback Submissions")
    parser.add_argument("-d", "--database-path", help="Path to the database (if it does not exist, it will be created)", default="dpi.db")

    subparsers = parser.add_subparsers(dest="command")

    # Update the database
    update_parser = subparsers.add_parser("update", help="Update the database from Google Sheets")
    update_parser.add_argument('type', choices=['group', 'contribution'],
                               help='Specify whether to update the group sheet or the contribution sheet.')
    update_parser.add_argument('sheet_key', type=str, help='Google Sheets key to update the database.')
    update_parser.add_argument('--credentials', help='Path to the Google Sheets API credentials file.',
                               default="credentials.json", type=lambda p: p if Path(p).is_file() else parser.error(f"File {p} does not exist."))

    # Query the database
    query_parser = subparsers.add_parser("query", help="Query the database")
    query_parser.add_argument('query_type', choices=['less_than', 'later_than', 'without_feedback'],
                              help='Query type to execute.')
    query_parser.add_argument('query_params', type=str, nargs='+', help='Parameters for the query (e.g., for less_than: score value; for later_than: date).')

    # Parse arguments
    return parser.parse_args()

def get_sheet(sheet_key:str, credentials_file:str):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_key).sheet1

def main():
    args = cli()
    dirname = os.path.dirname(__file__)
    schema_file = os.path.join(dirname, "schema.sql")
    conn = database.init_db(args.database_path, schema_file)
    if args.command == "update":
        sheet = get_sheet(args.sheet_key, args.credentials)
        if args.type == "group":
            database.insert_group_data(sheet, conn)
        elif args.type == "contribution":
            sheet_num = int(sheet.title[-1])  # TODO: FIND A BETTER SOLUTION
            database.insert_contribution_data(sheet, conn, sheet_num)
    elif args.command == "query":
        if args.query_type == "less_than" and args.query_params:
            score = float(args.query_params[0])
            exercise_num = int(args.query_params[1])
            result = queries.get_feedbacks_where_score_less_than(score, exercise_num, conn)
        elif args.query_type == "later_than" and args.query_params:
            date = args.query_params[0]
            exercise_num = int(args.query_params[1])
            result = queries.get_students_submitted_feedback_later_than(date, exercise_num, conn)
        elif args.query_type == "without_feedback" and args.query_params:
            exercise_num = int(args.query_params[0])
            result = queries.get_students_without_feedback_submission(exercise_num, conn)
        for row in result:
            row = map(str, row)
            print(", ".join(row))


if __name__ == '__main__':
    main()
