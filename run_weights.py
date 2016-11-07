from create_html_page import create_html_page
from database_handling import update_sqlite_with_data_from_withings
from get_data_from_withings import get_data_from_withings
from message_center import message_center


def main():
    #withings_data = get_data_from_withings()
    #update_sqlite_with_data_from_withings(withings_data)
    message_center()
    #create_html_page()


if __name__ == '__main__':
    main()