import datetime
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_parser import config
from weights_db_definitions import Weights, Comments, Users


@contextmanager
def get_session_manager():
    sqlite_db_url = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                config.get('DATABASE', 'sqlite_db_filename'))
    engine = create_engine(sqlite_db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def add_comment(comment, date=datetime.datetime.now()):
    # TODO if type date str date = datetime.datetime.strptime(date, '%Y-%m-%d')
    with get_session_manager() as session_manager:
        comment_entry = Comments(comment=comment,
                                 date=date)
        session_manager.add(comment_entry)
        session_manager.commit()


def get_comments():
    with get_session_manager() as session_manager:
        return session_manager.query(Comments).all()


def add_weight(user, weight, date=datetime.datetime.now()):
    # TODO if type date str date = datetime.datetime.strptime(date, '%Y-%m-%d')
    with get_session_manager() as session_manager:
        weight_entry = Weights(user=user,
                               date=date,
                               weight=weight)
        session_manager.add(weight_entry)
        session_manager.commit()


def get_weights():
    with get_session_manager() as session_manager:
        return session_manager.query(Weights).all()


def has_weight(user, date):
    with get_session_manager() as session_manager:
        if session_manager.query(Weights).filter_by(user=user,
                                                    date=date).all():
            return True
        else:
            return False


def get_email_address(user):
    with get_session_manager() as session_manager:
        (email_address,) = session_manager.query(Users.email_address).filter_by(user=user).one()
    return email_address


def update_sqlite_with_data_from_withings(withings_data):
    with get_session_manager() as session_manager:
        for user in withings_data:
            for date in withings_data[user]:
                if not has_weight(user, date):
                    print(user, date, withings_data[user][date], has_weight(user, date))
                    add_weight(user, withings_data[user][date], date)
        session_manager.commit()


def update_next_goal(user):
    with get_session_manager() as session_manager:
        user_entry = session_manager.query(Users).filter_by(user=user).first()
        user_entry.next_goal -= 1
        session_manager.commit()


def update_final_goal(user):  # Only used when final goal reached
    with get_session_manager() as session_manager:
        user_entry = session_manager.query(Users).filter_by(user=user).first()
        user_entry.goal -= 1
        user_entry.next_goal = user_entry.goal
        session_manager.commit()


def update_max_allowed_weight(user):
    with get_session_manager() as session_manager:
        user_entry = session_manager.query(Users).filter_by(user=user).first()
        user_entry.max_allowed_weight += -1
        session_manager.commit()
