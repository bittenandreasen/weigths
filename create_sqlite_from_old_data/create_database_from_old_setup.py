import datetime
import glob
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from string import strip

from weights_db_definitions import Comments, Weights, Base, Users

sqlite_db_url = 'sqlite:///' + os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                         'weights.sqlite'))


@contextmanager
def get_session_manager():
    engine = create_engine(sqlite_db_url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def create_database():
    engine = create_engine(sqlite_db_url, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def insert_old_data():
    with get_session_manager() as session_manager:
        cfg_files = glob.glob('*.cfg')
        for cfg_file in cfg_files:
            with open(cfg_file, 'rb') as fh:
                cfg_buffer = fh.readlines()
            cfg_buffer = [l.split(';') for l in cfg_buffer]
            if cfg_file == 'comments.cfg':
                print 'Parsing comments: ', cfg_file, len(cfg_buffer)
                for date, comment in cfg_buffer:
                    comment = strip(comment)
                    date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    print date, comment
                    comment_entry = Comments(comment=comment,
                                             date=date)
                    session_manager.add(comment_entry)
            else:
                if cfg_file.find('bit.cfg') != -1: user = 'Bitten'
                else: user = 'Sebastian'
                print 'Parsing user data: ', user, cfg_file, len(cfg_buffer)
                for date, weight, is_withings_weight, average_weight, weight_loss in cfg_buffer:
                    if date < '2011-12-21' or is_withings_weight == 'True ':
                        print user, date, weight, is_withings_weight
                        date = datetime.datetime.strptime(date, '%Y-%m-%d')
                        weigth_entry = Weights(user=user,
                                               date=date,
                                               weight=weight)
                        session_manager.add(weigth_entry)
        session_manager.commit()


def insert_user_data():
    bit = Users(user='Bitten',
                max_allowed_weight=88,
                goal=60,
                next_goal=87)
    seb = Users(user='Sebastian',
                max_allowed_weight=90,
                goal=63,
                next_goal=89
                )
    with get_session_manager() as session_manager:
        session_manager.add(bit)
        session_manager.add(seb)
        session_manager.commit()


create_database()
print 'created db with table definitions'
insert_old_data()
print 'done with inserts'
insert_user_data()
print 'initialized user data'