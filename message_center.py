import datetime
import smtplib
from sqlalchemy import func, and_

from config_parser import config
from database_handling import get_session_manager, update_next_goal, update_final_goal, update_max_allowed_weight, \
    get_email_address
from tools.gmail.gmail import get_gmail_service, create_message, send_message
from weights_db_definitions import Users, Weights


def check_for_goals_reached(user):
    with get_session_manager() as session_manager:
        (goal, next_goal,) = session_manager.query(Users.goal,
                                                   Users.next_goal).filter(Users.user == user).first()
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    (avg_this_week,) = session_manager.query(func.avg(Weights.weight)).filter(and_(Weights.user == user,
                                                                                   Weights.date > start_date,
                                                                                   Weights.date <= end_date)).first()
    if avg_this_week < goal:
        update_final_goal(user)
        return 'Fantastic you have reached your final goal of {goal} kg\n- we have lowered final goal with 1 kg.\n'.format(
            goal=next_goal)
    if avg_this_week < next_goal:
        update_next_goal(user)
        return 'Fantastic you have reached your next goal of {goal} kg\n- we have lowered next goal with 1 kg.\n'.format(goal=next_goal)
    return ''


def check_for_enough_weighings(user):
    min_weights = 3
    min_weights_days = 7
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=min_weights_days)
    with get_session_manager() as session_manager:
        (count_weights, ) = session_manager.query(func.count(Weights.weight)).filter(and_(Weights.user == user,
                                                                                          Weights.date > start_date,
                                                                                          Weights.date <= end_date)).first()
        if count_weights < min_weights:
            return 'Only {count_weights} weightings during the last {min_weights_days} days\n' \
                   '- try to get at least {min_weights} in a {min_weights_days} day period\n'.format(count_weights=count_weights,
                                                                                                   min_weights_days=min_weights_days,
                                                                                                   min_weights=min_weights)
    return ''


def check_maximum_weight(user):
    max_weight_days = 30
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=max_weight_days)
    with get_session_manager() as session_manager:
        (max_allowed_weight,) = session_manager.query(Users.max_allowed_weight).filter(Users.user == user).first()
        (max_weight,) = session_manager.query(func.max(Weights.weight)).filter(and_(Weights.user == user,
                                                                                    Weights.date > start_date,
                                                                                    Weights.date <= end_date)).first()
        if max_weight < max_allowed_weight -1:
            update_max_allowed_weight(user)
            return 'Fantastic for the last {days} your weights has been more than 1 kg under the maximum of {max_allowed_weight} kg allowed weight\n' \
                   ' - we lower maximum allowed weight by 1 kg'.format(days=max_weight_days,
                                                                       max_allowed_weight=max_allowed_weight)
        start_date = end_date - datetime.timedelta(days=7)
        (max_count,) = session_manager.query(func.count(Weights.weight)).filter(and_(Weights.user == user,
                                                                                    Weights.date > start_date,
                                                                                    Weights.date <= end_date,
                                                                                    Weights.weight > max_allowed_weight)).first()
        if max_count > 0:
            return 'Warning - during the last {days} days {count} weights have been over the allowed maximum weight of {max_allowed_weight} kg.\n' \
                    '\nNow is the time to get it together.'.format(days=7,
                                                              count=max_count,
                                                              max_allowed_weight=max_allowed_weight)
    return ''


def message_center():
    gmail_service = get_gmail_service()
    users = config.get('WITHINGS', 'users').split(',')
    for user in ['Bitten']:  #users:
        email_body = ''
        email_body += check_for_enough_weighings(user)
        email_body += check_for_goals_reached(user)
        email_body += check_maximum_weight(user)
        if email_body:
            user_email_address = get_email_address(user)
            print 'Sending email to user: ', user, user_email_address
            print email_body
            email_message = create_message(user_email_address, 'Message from weights.', email_body)
            print email_message
            send_message(gmail_service, email_message)