import datetime
from sqlalchemy import func, and_

from config_parser import config
from database_handling import get_session_manager
from tools.misc import get_html_table
from weights_db_definitions import Weights, Users

HTML_BUFFER = '<html>' \
              '<body>' \
              '<h1>Diet status - {today}</h1>' \
              '{html_body}' \
              '</pre>' \
              '</body>' \
              '</html>'


HTML_SECTION = '<h2>{header}</h2>' \
               '{section}'


def get_monthly_history():
    users = config.get('WITHINGS', 'users').split(',')
    history_list_header = ['Month']
    for user in users:
        history_list_header += ['', user[0] + ' avg', user[0] + ' min', user[0] + ' max', user[0] + ' #']
    history_list_header = [history_list_header]
    history_list = []
    with get_session_manager() as session_manager:
        (min_date, ) = session_manager.query(Weights.date).order_by(Weights.date).first()
        min_date = datetime.date(min_date.year, min_date.month, 1)
        while min_date < datetime.date.today():
            month_string = '{year}-{month:0>2}'.format(year=min_date.year, month=min_date.month)
            month_count = 0
            month_row = [month_string]
            for user in users:
                (avg_weight, min_weight, max_weight, count_weight) = \
                    session_manager.query(func.avg(Weights.weight),
                                          func.min(Weights.weight),
                                          func.max(Weights.weight),
                                          func.count(Weights.weight)).\
                        filter(and_(Weights.user == user,
                                    Weights.date.like(month_string + '%'))).first()
                month_count += count_weight
                month_row += ['', avg_weight, min_weight, max_weight, count_weight]
            if month_count >  0:
                history_list += [month_row]
            min_date = min_date + datetime.timedelta(days=32)
            min_date = datetime.date(min_date.year, min_date.month, 1)
    history_list = sorted(history_list, reverse=True)
    history_list = history_list_header + history_list
    #print history_list
    return history_list


def get_history_section():
    header = 'Weight history:'
    section = get_html_table(get_monthly_history())
    return HTML_SECTION.format(header=header,
                               section=section)


def get_stat_last_period(days = 30):
    users = config.get('WITHINGS', 'users').split(',')
    stat_list_header = ['Day']
    for user in users:
        stat_list_header += ['', user[0] + ' weight', user[0] + ' avg weight', user[0] + ' weight loss']
    stat_list_header = [stat_list_header]
    stat_list = []
    last_weights = {}
    last_avg_weights = {}
    min_avg_weight = {}
    min_weights = {}
    for user in users:
        last_weights[user] = []
        last_avg_weights[user] = []
        min_avg_weight[user] = 100
        min_weights[user] = 100 # TODO ??? better ???
    min_date = datetime.datetime.now() - datetime.timedelta(days=days+20)
    min_date = datetime.date(min_date.year, min_date.month, min_date.day)
    with get_session_manager() as session_manager:
        while min_date <= datetime.date.today():
            stat_row = [str(min_date)]
            for user in users:
                weight, avg_weight, weight_loss = None, None, None
                (weight,) = session_manager.query(func.avg(Weights.weight)).\
                    filter(and_(Weights.user == user,
                                Weights.date == str(min_date))).first()
                if weight:
                    last_weights[user].append(weight)
                else:
                    if last_weights[user]:
                        last_weights[user].append(last_weights[user][-1])
                        weight = last_weights[user][-1]
                if last_weights[user]:
                    if not last_avg_weights[user] or len(last_avg_weights[user])<5:
                        avg_weight = last_weights[user][-1]
                        weight_loss = 0
                        last_avg_weights[user].append(avg_weight)
                    else:
                        avg_weight = last_avg_weights[user][-1] + (weight - last_avg_weights[user][-5])/10
                        weight_loss = (last_avg_weights[user][-5]-avg_weight)/5
                        last_avg_weights[user].append(avg_weight)
                last_weights[user] = last_weights[user][-10:]
                last_avg_weights[user] = last_avg_weights[user][-10:]
                if weight and avg_weight and weight_loss:
                    if avg_weight < min_avg_weight[user]:
                        min_avg_weight[user] = avg_weight
                        avg_weight = ('background:#CC9999', avg_weight)
                    if weight < min_weights[user]:
                        min_weights[user] = weight
                        weight = ('background:#CC9999', weight)
                    stat_row += ['', weight, avg_weight, max(weight_loss,0)]
                else:
                    stat_row += ['', '', '', '']
            #print stat_row
            stat_list += [stat_row]
            min_date += datetime.timedelta(days=1)
    stat_list = sorted(stat_list, reverse=True)
    stat_list = stat_list[:days]
    stat_list = stat_list_header + stat_list
    return stat_list


def get_stat_last_period_section():
    last_period_in_days = int(config.get('FLAGS', 'last_period_in_days'))
    header = 'Last {days} days:'.format(days=last_period_in_days)
    section = get_html_table(get_stat_last_period(last_period_in_days))
    return HTML_SECTION.format(header=header,
                               section=section)


def get_user_stat_last_period(user, days=40):
    last_weights = [[], []]
    min_date = datetime.datetime.now() - datetime.timedelta(days=days + 20)
    min_date = datetime.date(min_date.year, min_date.month, min_date.day)
    with get_session_manager() as session_manager:
        while min_date <= datetime.date.today():
            (weight,) = session_manager.query(func.avg(Weights.weight)). \
                filter(and_(Weights.user == user,
                            Weights.date == str(min_date))).first()
            if weight:
                last_weights[0].append(weight)
            else:
                if last_weights[0]:
                    last_weights[0].append(last_weights[0][-1])
            if last_weights[0]:
                last_weights[1].append(sum(last_weights[0][-5:])/min(len(last_weights[0]),5))
            min_date += datetime.timedelta(days=1)
    return last_weights[-days:]


def create_graph(graph_title, input_values, input_values_titles):
    color_codes = ['0000FF', 'FF0000', '00FF00']
    color_codes = color_codes[:len(input_values)]
    color_codes = ','.join(color_codes)
    # Checking input
    if len(input_values) != len(input_values_titles):
        raise AssertionError('Number of values and titles for these do not match.')
    # Redying input for graph
    days = [len(input_value) for input_value in input_values]
    if len(set(days)) != 1:
        raise AssertionError('Input values of uneven length')
    days = days[0]
    min_value = min([min(input_value) for input_value in input_values])
    max_value = min([max(input_value) for input_value in input_values])
    scale = 100/(max_value - min_value)
    input_values = [[(v-min_value)*scale for v in input_value] for input_value in input_values]
    input_values = [[str(v) for v in input_value] for input_value in input_values]
    input_values = [','.join(input_value) for input_value in input_values]
    input_values = '|'.join(input_values)
    input_values_titles = [''.join(input_value_title) for input_value_title in input_values_titles]
    input_values_titles = '|'.join(input_values_titles)
    # Putting image together
    graph = '<img src=\"https://chart.googleapis.com/chart?chs=660x330&cht=lc&chco={color_codes}'.format(
        color_codes=color_codes)
    graph += '&chd=t:{input_values}'.format(input_values=input_values)
    graph += '&chxt=x,y&chxr=1,{min_value},{max_value}'.format(min_value=min_value,
                                                               max_value=max_value)
    graph += '&chxl=0:{days}'.format(days=days)
    graph += '&chxs=0,t&chdl={input_values_titles}'.format(input_values_titles=input_values_titles)
    graph += '&chdlp=b&chma=0,5,5,25&chtt={graph_title}'.format(graph_title=graph_title)
    graph += '">'
    return graph


def get_user_graph_section(days=40):
    users = config.get('WITHINGS', 'users').split(',')
    header = 'Graphs:'
    section = ''
    for user in users:
        graph_title = 'Last {days} days for {user}'.format(days=days,
                                                       user=user)
        section += create_graph(graph_title, get_user_stat_last_period(user, days), ['weight', 'avg. weight'])
    return HTML_SECTION.format(header=header,
                               section=section)


def get_goal_status():  # TODO check this works after message center implemented
    goal_list = [['User',
                  'Avg. weight this week',
                  'BMI',
                  'Next goal',
                  'Final goal',
                  'Weight loss',
                  'Expected days next goal',
                  'Expected days final goal']]
    users = config.get('WITHINGS', 'users').split(',')
    with get_session_manager() as session_manager:
        for user in users:
            (goal, next_goal, height) = session_manager.query(Users.goal,
                                                       Users.next_goal,
                                                       Users.height_in_cm).filter(Users.user == user).first()
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=7)
            (avg_this_week,) = session_manager.query(func.avg(Weights.weight)).filter(and_(Weights.user == user,
                                                                                        Weights.date > start_date,
                                                                                        Weights.date <= end_date)).first()
            end_date = start_date
            start_date = end_date - datetime.timedelta(days=7)
            (avg_last_week,) = session_manager.query(func.avg(Weights.weight)).filter(and_(Weights.user == user,
                                                                                        Weights.date > start_date,
                                                                                        Weights.date <= end_date)).first()
            weight_loss = (avg_last_week - avg_this_week)/7
            days_to_next_goal = (avg_this_week-next_goal)/weight_loss
            days_to_final_goal = (avg_this_week-goal)/weight_loss
            if days_to_next_goal < 0:
                days_to_next_goal = 'NA'
                days_to_final_goal = 'NA'
            else:
                days_to_next_goal = int(days_to_next_goal)
                days_to_final_goal = int(days_to_final_goal)
            bmi = avg_this_week / ((height/100.0) ** 2)
            goal_list += [[user, avg_this_week, bmi, next_goal, goal, weight_loss, days_to_next_goal, days_to_final_goal]]
    return goal_list


def get_goal_status_section():
    header = 'Goals:'
    section = get_html_table(get_goal_status())
    return HTML_SECTION.format(header=header,
                               section=section)


def get_html_body():
    html_body = ''
    html_body += get_goal_status_section()
    html_body += get_user_graph_section(days=40)
    html_body += get_stat_last_period_section()
    html_body += get_history_section()
    return html_body


def get_html_buffer():
    today = datetime.datetime.now()
    today = today.strftime('%A %d %B, %Y')
    html_body = get_html_body()
    return HTML_BUFFER.format(today=today,
                              html_body=html_body)


def create_html_page():
    html_buffer = get_html_buffer()
    #print(html_buffer)
    with open('withings.html', 'w') as fh:
        fh.write(html_buffer)
