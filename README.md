# Weights project introduction

This project is for
* getting wifi uploaded weights from withings homepage and storing the data
* analyzing the data
* informing the user of progress and potential weight gains.

# All steps are run by run_weights.py

The steps are:

1) get_data_from_withings - fetches all data from withings and returns it - Done!

2) parse_data_from_withings - parses data from withings and inserts new data into sqlite database

3) create_html_page - creates status web page (and uploads it)

4) message_center - sends emails to users if certain events has happened
    Messages:
        - Remind user to do weighings if below 2 a week
        + if average weight below maximum-1 for 1 month - lower maximum weight and congratulate user
        + average weigth first time under