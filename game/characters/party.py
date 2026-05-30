# game/party.py

class Party:
    def __init__(self, members=None):
        self.members = members or []

    def add_member(self, character):
        self.members.append(character)

    def get_alive_members(self):
        return [member for member in self.members if member.is_alive()]

    def get_conscious_members(self):
        return [
            member for member in self.get_alive_members()
            if not member.is_unconscious()
        ]

    def is_defeated(self):
        return len(self.get_alive_members()) == 0

    def get_member(self, index):
        if index < 0 or index >= len(self.members):
            return None

        return self.members[index]