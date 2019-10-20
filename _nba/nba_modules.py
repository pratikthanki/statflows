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
