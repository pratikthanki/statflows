import seaborn as sns;
import matplotlib.pyplot as plt
from shared_config import sql_config
from shared_modules import sql_server_connection, load_data

sns.set(style="ticks", color_codes=True)

conn, cursor = sql_server_connection(sql_config, 'nba')

game_play_columns = 'cl,de,etype,evt,gid,locX,locY,mtype,period,pid,tid'
game_id = 11500018
query = 'SELECT {0} FROM GamePlays WHERE gid = {1}'.format(game_play_columns, game_id)

game_plays = load_data(query=query, sql_config=sql_config, database='nba')
game_plays.columns = game_play_columns.split(',')

print(game_play_columns.split(','))

shots_made = game_plays.loc[(game_plays['etype'] == 1)]
shots_missed = game_plays.loc[(game_plays['etype'] == 2)]
shots_all = game_plays.loc[((game_plays['etype'] == 1) | (game_plays['etype'] == 2))]

# scatter plot with distribution on axis
g = sns.JointGrid(
    x="locX",
    y="locY",
    data=shots_all).plot_joint(
    plt.scatter,
    color=".5",
    edgecolor="white").plot_marginals(
    sns.distplot,
    kde=False,
    color=".5")

# hex plot
g = sns.jointplot(
    x="locX",
    y="locY",
    data=shots_all,
    kind="hex",
    stat_func=None).set_axis_labels("x", "y")

plt.show()
