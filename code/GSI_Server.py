# server = GSIServer(("127.0.0.1", 3000), "S8RL9Z6Y22TYQK45JB4V8PHRJJMD9DS9")
# server.start_server()
#
# server.get_info("map", "name")
# server.get_info("player", "state", "flashed)


from http.server import BaseHTTPRequestHandler, HTTPServer
from operator import attrgetter
from threading import Thread
import json


# import gamestate
# import payloadparser

class GSI_Server(HTTPServer):
    def __init__(self, server_adress, env=None):
        super(GSI_Server, self).__init__(server_adress, RequestHandler)
        self.env = env
        self.running = False

    def start_server(self):
        try:
            thread = Thread(target=self.serve_forever)
            thread.start()
            first_time = True
            while self.running == False:
                if first_time == True:
                    print("DOTA Underlords GSI Server starting..")
                first_time = False
                self.running = True
        except:
            print("Could not start server.")


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length).decode("utf-8")

        payload = json.loads(body)

        for block in payload['block']:
            if len(block) > 0:
                # print(data)
                for data in block['data']:

                    if 'public_player_state' in data:

                        publicData = data['public_player_state']

                        if 'is_human_player' not in publicData:
                            continue
                        elif not publicData['is_human_player']:
                            continue

                        print("PUBLIC")
                        print(publicData)

                        if 'combat_type' in publicData:
                            self.server.env.combatType = publicData['combat_type']
                        if 'combat_result' in publicData:
                            combatResult = publicData['combat_result']

                            if publicData['wins'] != self.server.env.wins:
                                self.server.env.wins = publicData['wins']
                                self.server.env.round += 1
                                self.server.env.newRoundStarted = True
                                # print(f"it is now round WIN: {self.server.env.round}")
                                # print(self.server.env.combatResult)
                            elif publicData['losses'] != self.server.env.losses:
                                self.server.env.losses = publicData['losses']
                                self.server.env.round += 1
                                self.server.env.newRoundStarted = True
                                # print(f"it is now round LOSS: {self.server.env.round}")
                                # print(self.server.env.combatResult)
                            elif self.server.env.combatResult != combatResult and combatResult != 1 and combatResult != 2:
                                print("There was a draw?")
                                self.server.env.combatResult = combatResult
                                self.server.env.round += 1
                                self.server.env.newRoundStarted = True
                                # print(f"it is now round DRAW: {self.server.env.round}")
                                # print(self.server.env.combatResult)
                            else:
                                self.server.env.newRoundStarted = False

                        if 'health' in publicData:
                            self.server.env.health = publicData['health']
                        if 'gold' in publicData:
                            self.server.env.gold = publicData['gold']
                        if 'board_unit_limit' in publicData:
                            self.server.env.level = publicData['board_unit_limit']
                        if 'next_level_xp' in publicData:
                            self.server.env.remainingEXP = publicData['next_level_xp'] - publicData['xp']
                        if 'final_place' in publicData:
                            self.server.env.finalPlace = publicData['final_place']

                        if 'units' in publicData:
                            units = publicData['units']  # It's all units

                        if 'item_slots' in publicData:

                            items = []
                            for item in publicData['item_slots']:
                                items.append((item['slot_index'], item['item_id']))
                            self.server.env.gsiItems = items

                    elif 'private_player_state' in data:

                        privateData = data['private_player_state']

                        if 'shopLocked' in privateData:
                            self.server.env.lockedIn = privateData['shopLocked']

                        if 'reroll_cost' in privateData:
                            self.server.env.rerollCost = privateData['reroll_cost']

                        if 'can_select_underlord' in privateData:
                            can_select_underlord = privateData['can_select_underlord']

                            if can_select_underlord:

                                underlordPicks = []

                                for underlord in privateData['underlord_picker_offering']:
                                    underlordPicks.append((underlord['underlord_id'], underlord['build_id']))

                                self.server.env.underlordPicks = underlordPicks
                            else:
                                self.server.env.underlordPicks = None

                        if 'oldest_unclaimed_reward' in privateData:

                            itemChoices = []

                            for item in privateData['oldest_unclaimed_reward']['choices']:
                                itemChoices.append(item['item_id'])
                            self.server.env.itemPicks = itemChoices

                        else:
                            self.server.env.itemPicks = None

                        if 'used_item_reward_reroll_this_round' in privateData:
                            self.server.env.rerolledItem = privateData['used_item_reward_reroll_this_round']

                        if 'shop_units' in privateData:
                            shopUnits = []

                            # print('updating shopUnits')

                            for i in range(5):
                                shopUnits.append(privateData['shop_units'][i]['unit_id'])
                            self.server.env.shopUnits = shopUnits
                        # else:
                        #     self.server.env.shopUnits = None

                    else:
                        print("lol what now?")

        # self.server.running = True
        #
        # self.server.parser.parse_payload(payload, self.server.gamestate)
        self.server.running = True

#
# server = GSI_Server(('localhost', 3000))
# server.start_server()
#
# print('non blocking?')
