import random
from enum import Enum
import numpy as np


class Player:

    def __init__(self, name):
        status = playerStatus.alive
        self.name = name
        self.roles = []
        if not isinstance(status, playerStatus):
            raise TypeError('status must be an instance of playerStatus Enum')
        self.status = status

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        if role in self.roles:
            self.roles.pop(role)


class Role:

    def __init__(self, name, desc, value, activeAt):
        self.name = name
        self.desc = desc  # Hilfetext
        self.value = value  # Wertigkeit der Rolle (Böse negativ, Gut positiv)
        if not isinstance(activeAt, ActiveAt):
            raise TypeError('activeAt must be an instance of ActiveAt Enum')
        self.activeAt = activeAt
    """def get_name(self):
        return self.name
    def get_desc(self):
        return self.desc
    def get_value(self):
        return self.value
    def get_activeAt(self):
        return self.activeAt"""


class Werewolf(Role):

    def __init__(self):
        super().__init__("Werwolf", "Ist voll böse", -4, ActiveAt.night)

    def wakeup(game):
        game.send_message("Die Werwölfe erwachen")
        wwPoll = Poll("Wen wollt ihr töten?",
                      game.get_players_with_role(gameRoles.villager))
        game.send_poll(wwPoll, game.get_players_with_role(gameRoles.werewolf))
        return wwPoll.evaluate()


class Villager(Role):

    def __init__(self):
        super().__init__("Dorfbewohner", "Will nicht sterben", 1, ActiveAt.never)


class Seer(Role):
    def __init__(self):
        super().__init__("Seherin",
                         "Gehört zum Dorf. Kann jede Nacht eine Identität sehen.", 3, ActiveAt.night)


class Poll:

    def __init__(self, message, pollElements):
        self.message = message
        self.pollElements = pollElements
        self.pollValues = [0]*len(pollElements)

    def evaluate(self):
        maxIndex = np.argmax(self.pollValues)
        if self.pollValues[maxIndex] > 0:
            return self.pollElements[maxIndex]
        else:
            return None

    def add_vote(self, key):
        self.pollValues[key-1] += 1

    def __repr__(self):
        repr = ""
        it = 1
        for ele in self.pollElements:
            repr += str(it)+". "+ele.name+"\n"
            it += 1
        return repr


class ActiveAt(Enum):
    night = 1
    day = 2
    never = 3


class playerStatus(Enum):
    alive = 1
    death = 2
    ghost = 3


class gameRoles(Enum):
    villager = Villager
    werewolf = Werewolf
    seer = Seer


class WWGame:

    def __init__(self, players, roles):
        self.players = players
        self.roles = roles

    def init_game(self):
        self.assign_roles_to_players()
        self.publish_roles_to_players()

    def assign_roles_to_players(self):
        for player in self.players:
            player.add_role(random.choice(self.roles))

    def publish_roles_to_players(self):
        for player in self.players:
            for role in player.roles:
                self.send_message(player.name+" ist " +
                                  role.value().name, [player])

    def send_message(self, message, players=None):
        if players is None:
            players = self.players
        for player in players:
            print(message)

    def get_alive_players(self, players=None):
        if players is None:
            players = self.players
        return list(filter(lambda x: x.status == playerStatus.alive, players))

    def get_players_with_role(self, role):
        return list(filter(lambda x: role in x.roles and x.status == playerStatus.alive, self.players))

    def is_the_game_won(self):
        if len(self.get_players_with_role(gameRoles.villager)) == 0 or len(self.get_players_with_role(gameRoles.werewolf)) == 0:
            if self.get_alive_players()[0].roles[0] == gameRoles.villager:
                self.send_message("Die Dorfbewohner haben gewonnen!")
            else:
                self.send_message("Die Werwölfe haben gewonnen!")
            for player in self.players:
                self.send_message(player.name+" war " +
                                  player.roles[0].value().name+"!")
            return True
        else:
            return False

    def start_game(self):
        self.send_message("Willkommen beim Spiel!")

        while not self.is_the_game_won():
            deaths = self.start_night()
            self.start_day(deaths)

    def start_night(self):
        deaths = []
        self.send_message("Das Dorf schläft ein")
        deaths.append(Werewolf.wakeup(self))
        return deaths

    def start_day(self, deaths):
        self.send_message("Das Dorf wacht auf")
        if self.set_death(deaths):
            return
        dorfPoll = Poll("Wen wollt ihr an den Galgen hängen?",
                        self.get_alive_players())
        self.send_poll(dorfPoll, self.get_alive_players())
        death = dorfPoll.evaluate()
        self.set_death([death])

    def set_death(self, deaths):
        '''
        returns True if game is won
        returns False otherwise
        '''
        for death in deaths:
            death.status = playerStatus.death
            self.send_message(death.name+" ist gestorben!")
        return self.is_the_game_won()

    def send_poll(self, poll, players):
        self.send_message(poll.message, players)
        self.send_message(repr(poll), players)
        for player in self.get_alive_players(players):
            poll.add_vote(self.intInput("Wähle eine Nummer: ",
                          player, 1, len(poll.pollElements)))

    def intInput(self, message, player, min, max):
        while True:
            try:
                inp = int(input(message))
                if inp >= min and inp <= max:
                    return inp
            except:
                self.send_message("Gib eine Zahl zwischen " +
                                  min+" und "+max+" ein!", [player])
                pass
