from lcu_driver import Connector
from database import Database

# LCU assignedPosition → chave interna do DB
LCU_LANE_MAP = {
    "top":     "TOP",
    "jungle":  "JG",
    "middle":  "MID",
    "bottom":  "ADC",
    "utility": "SUPP",
}


class PreGameManager:
    def __init__(self):
        self.connector = Connector()
        self.db = Database.get_instance()

        #Config
        self.auto_queue = False
        self.auto_ban = False
        self.auto_pick = False
        self.auto_hover = False
        self.max_tries = 10

        #Control variables
        self.already_ban = False
        self.already_pick = False
        self.already_hovered = False
        self.ranked_queue = None 

    def setup_auto_accept(self):
        @self.connector.ws.register('/lol-matchmaking/v1/ready-check', event_types=('CREATE','UPDATE'))
        async def on_ready_check(connection, event):

            if not self.auto_queue:
                return

            if event.data['state'] != 'InProgress':
                return 
            
            if event.data['playerResponse'] == 'Accepted':
                return
            
            response = await connection.request('post', '/lol-matchmaking/v1/ready-check/accept')
            if response.status == 204:
                print("Partida aceita")
                return 

    def setup_champion_select(self):
        @self.connector.ws.register('/lol-champ-select/v1/session', event_types=("CREATE", "UPDATE"))
        async def handler(connection, event):

            # Checks if this is some mode that you can pick your champion and caches the result
            if self.ranked_queue == False:
                print('debug non_ranked = false')
                return

            if self.ranked_queue is None:
                queue_id = event.data['queueId']
                if queue_id not in [420, 440, 3110]:
                    self.ranked_queue = False
                    return
                else:
                    self.ranked_queue = True 
            #

            player_cell = event.data['localPlayerCellId']
            lobby_phase = event.data['timer']['phase']
            player_action_phase = None
            player_action_id = None
            player_lane = None

            for t in event.data['myTeam']:
                if t['cellId'] == player_cell:
                    raw_pos = t['assignedPosition']
                    player_lane = LCU_LANE_MAP.get(raw_pos.lower())
                    print(f"[CHAMP-SELECT] assignedPosition='{raw_pos}' → lane='{player_lane}'")



            for action_group in event.data['actions']:
                for action in action_group:

                    if action['actorCellId'] != player_cell:
                        continue

                    if lobby_phase == 'PLANNING' and action['type'] == 'pick':
                        player_action_phase = action['type']
                        player_action_id = action['id']

                    elif lobby_phase == 'BAN_PICK' and action['isInProgress'] == True:
                        player_action_phase = action['type']
                        player_action_id = action['id']

    
            print(f"[CHAMP-SELECT] fase={lobby_phase} | action_phase={player_action_phase} | action_id={player_action_id} | lane={player_lane}")
            

            # Hovering logic
            if lobby_phase == 'PLANNING' and self.auto_hover and not self.already_hovered:
                picks = self.db.get_picks_by_lane(player_lane)
                if picks:
                    champion_to_be_hovered = picks[0]['champion_id']
                    print(f"[HOVER] Hovering campeão id={champion_to_be_hovered} (1º pick da lane {player_lane})")
                else:
                    champion_to_be_hovered = self.db.get_random_champion_id()
                    print(f"[HOVER] Sem picks para lane '{player_lane}', hover aleatório id={champion_to_be_hovered}")

                await connection.request('patch', f'/lol-champ-select/v1/session/actions/{player_action_id}',
                                         data={"championId": champion_to_be_hovered, "completed": False})
                self.already_hovered = True

            # Banning logic
            if player_action_phase == 'ban' and lobby_phase == 'BAN_PICK' and self.auto_ban and not self.already_ban:

                bans = self.db.get_bans()

                ally_pick_intent = [
                    t['championPickIntent'] 
                    for t in event.data['myTeam'] 
                    if t['championPickIntent'] != 0 and t['cellId'] != player_cell
                ]

                ban = next((b for b in bans if b['champion_id'] not in ally_pick_intent), None)
                if ban:
                    ban_id = ban['champion_id']
                else:
                    tries = 0
                    ban_id = self.db.get_random_champion_id()
                    while ban_id in ally_pick_intent and tries < self.max_tries:
                        ban_id = self.db.get_random_champion_id()
                        tries += 1

                if ban_id:
                    await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % player_action_id, data={"championId": ban_id, "completed": True})
                    self.already_ban = True
                else:
                    print('capotemo o corsa')

            #Pick logic
            if player_action_phase == 'pick' and lobby_phase == 'BAN_PICK' and self.auto_pick and not self.already_pick:
                picks = self.db.get_picks_by_lane(player_lane)

                all_bans = event.data['bans']['myTeamBans'] + event.data['bans']['theirTeamBans']
                picked = [
                    t['championId']
                    for t in event.data['myTeam'] + event.data['theirTeam']
                    if t['championId'] != 0
                ]

                unavailable = all_bans + picked 

                tries = 0
                pick = next((p for p in picks if p['champion_id'] not in unavailable), None)

                if pick:
                    pick_id = pick['champion_id']
                    print(f"[PICK] Pickando id={pick_id} (prioridade {pick['prioridade']}, lane {player_lane})")
                else:
                    print(f"[PICK] Todos os picks da lane '{player_lane}' indisponíveis, sorteando aleatório")
                    pick_id = self.db.get_random_champion_id()
                    while pick_id in unavailable and tries < self.max_tries:
                        pick_id = self.db.get_random_champion_id()
                        tries += 1

                if pick_id:
                    await connection.request('patch', '/lol-champ-select/v1/session/actions/%d' % player_action_id, data={"championId": pick_id, "completed": True})
                    self.already_pick = True
                else:
                    print('[PICK] Nenhum campeão disponível para pickar')

        @self.connector.ws.register('/lol-champ-select/v1/session', event_types=("DELETE",))
        async def reset_control_variables(connection, event):
            print('resetou')
            self.already_pick = False
            self.already_ban = False
            self.already_hovered = False
            self.ranked_queue = None
        