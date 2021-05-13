import pandas as pd
import requests

headers = {
    'x-rapidapi-key': "########################",#insert api key
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com"
}


def get_player_info(last_name, headers):
    url = "https://api-nba-v1.p.rapidapi.com/players/lastName/" + last_name

    response = requests.request("GET", url, headers=headers)
    return response


def get_top10(headers):
    players = ['Anthony Edwards', 'James Wiseman', ' LaMelo Ball', 'Patrick Williams', 'Isaac Okoro', 'Onyeka Okongwu',
               'Killian Hayes'
        , 'Obi Toppin', 'Deni Avdija', 'Jalen Smith']

    return_players = []
    for name in players:
        last_name = name.split()[1]

        player_info = get_player_info(last_name, headers).json()

        for player in player_info['api']['players']:
            if player['startNba'] == '2020':
                return_players.append(player)

    return pd.json_normalize(return_players)


def get_stats(players_id, headers):
    stats = []

    for p_id in players_id:
        url = "https://api-nba-v1.p.rapidapi.com/statistics/players/playerId/" + p_id
        response = requests.request("GET", url, headers=headers)

        df = pd.json_normalize(response.json()['api']['statistics'])
        stats.append(df)

    return stats


def add_date(stats, headers):
    stats_d = []

    url = "https://api-nba-v1.p.rapidapi.com/games/seasonYear/2020"
    response = requests.request("GET", url, headers=headers)
    df_season = pd.json_normalize(response.json()['api']['games'])

    for df in stats:
        df_d = df.copy().merge(df_season[['gameId', 'startTimeUTC']], how='inner', on='gameId')
        stats_d.append(df_d)

    return stats_d


def get_data(headers):

    player_data = get_top10(headers)
    stats = pd.concat(add_date(get_stats(player_data['playerId'],headers),headers))
    return stats.merge(player_data[['lastName','playerId']], how='inner', on='playerId')


stats = get_data(headers)

print(stats)

stats.to_csv('data_10draft')
