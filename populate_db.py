import requests 
from database import Database

#  response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
# latest_version = response.json()[0]
# print(type(latest_version))
# response = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/pt_BR/champion.json')

def check_version():
    db = Database.get_instance()
    actual_version = db.get_latest_version()

    response = requests.get('https://ddragon.leagueoflegends.com/api/versions.json')
    latest_version = response.json()[0]

    are_equal = actual_version == latest_version

    if (not are_equal):
        db.insert_version(latest_version)

    return (are_equal, latest_version)

def populate_db(version):

    db = Database.get_instance()
    response = requests.get(f'https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion.json')
    data = response.json()['data']

    for champion in data.values():
        nome_id = champion['id']
        db.insert_champion(int(champion['key']), champion['name'], nome_id, f'https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{nome_id}.png')

    print('Db populado com sucesso!') 

def update_db():
    latest_version = check_version()
    if not latest_version[0]:
        print(f'Versoes diferentes! Populando DB\nVersão atualizada: {latest_version[1]}')
        populate_db(latest_version[1])
    else:
        print('Versões iguais! Nada a ser atualizado.')

