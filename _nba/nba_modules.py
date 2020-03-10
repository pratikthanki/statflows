import datetime


def parse_time_elapsed(time_str, period):
    max_minutes = 12 if period < 5 else 5

    minutes, sec = [int(i) for i in time_str.split(':')]

    min_elapsed = max_minutes - minutes - 1
    sec_elapsed = 60 - sec

    return (min_elapsed * 60) + sec_elapsed


def calculate_time_elapsed(row):
    time_in_period_now = parse_time_elapsed(row['cl'], row['period'])
    period = row['period']

    if period > 4:
        return (12 * 60 * 4) + ((period - 5) * 5 * 60) + time_in_period_now
    else:
        return ((period - 1) * 12 * 60) + time_in_period_now


def current_nba_season(dt=None):
    if not dt:
        today = datetime.date.today()
    else:
        today = dt

    if today.month in (7, 8, 9, 10, 11, 12):
        y = today.year
        current_season = str(y) + '-' + str(y + 1)
    else:
        y = today.year
        current_season = str(y - 1) + '-' + str(y)

    return current_season


pbp_e_types = {
    1: 'Shot made',
    2: 'Shot Missed',
    3: 'Free Throw',
    4: 'Rebound',
    5: 'Turnover',
    6: 'Foul',
    7: 'Violation:Kicked Ball',
    8: 'Substitution',
    9: 'Team Timeout',
    10: 'Jump Ball',
    11: 'Ejection',
    12: 'Start Period',
    13: 'End Period',
    18: 'Instant Replay',
    20: 'Stoppage'
}
