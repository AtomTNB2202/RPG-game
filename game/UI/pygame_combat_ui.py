# game/ui/pygame_combat_ui.py

import pygame


class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action

    def draw(self, screen, font):
        pygame.draw.rect(screen, (60, 60, 70), self.rect)
        pygame.draw.rect(screen, (180, 180, 190), self.rect, 2)

        label = font.render(self.text, True, (240, 240, 240))
        screen.blit(
            label,
            (
                self.rect.x + 10,
                self.rect.y + self.rect.height // 2 - label.get_height() // 2
            )
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class CombatUI:
    def __init__(self, session):
        pygame.init()

        self.session = session

        self.width = 1100
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RPG Combat Demo")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)

        self.selected_actor = None
        self.selected_part_key = None

        self.buttons = [
            Button((40, 620, 140, 45), "Attack", "attack"),
            Button((200, 620, 140, 45), "Skill", "skill"),
            Button((360, 620, 140, 45), "Guard", "guard"),
            Button((520, 620, 140, 45), "Analyze", "analyze"),
            Button((680, 620, 140, 45), "Run", "run"),
        ]

        self.party_rects = []
        self.part_rects = []

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_click(self, pos):
        for actor, rect in self.party_rects:
            if rect.collidepoint(pos):
                if not actor.is_unconscious() and actor.is_alive():
                    self.selected_actor = actor
                return

        for part_key, rect in self.part_rects:
            if rect.collidepoint(pos):
                self.selected_part_key = part_key
                return

        for button in self.buttons:
            if button.is_clicked(pos):
                self.handle_action(button.action)
                return

    def handle_action(self, action_type):
        if self.session.finished:
            return

        if action_type == "attack":
            if self.selected_actor is None:
                self.session.logs.append("Choose a party member first.")
                return

            if self.selected_part_key is None:
                self.session.logs.append("Choose an enemy body part first.")
                return

            action = {
                "type": "attack",
                "actor": self.selected_actor,
                "target_part": self.selected_part_key
            }

        elif action_type == "guard":
            if self.selected_actor is None:
                self.session.logs.append("Choose a party member first.")
                return

            action = {
                "type": "guard",
                "actor": self.selected_actor
            }

        elif action_type == "analyze":
            action = {
                "type": "analyze"
            }

        elif action_type == "run":
            action = {
                "type": "run"
            }

        elif action_type == "skill":
            self.session.logs.append("Skill UI is not implemented yet.")
            return

        else:
            return

        self.session.submit_action(action)

    def draw(self):
        self.screen.fill((25, 25, 30))

        self.draw_title()
        self.draw_party_panel()
        self.draw_enemy_panel()
        self.draw_log_panel()
        self.draw_buttons()
        self.draw_selection_info()

    def draw_title(self):
        title = self.font.render("RPG Combat Demo", True, (255, 255, 255))
        self.screen.blit(title, (40, 20))

        if self.session.finished:
            result = self.session.result["outcome"]
            text = self.font.render(f"Combat Finished: {result.upper()}", True, (255, 220, 120))
            self.screen.blit(text, (760, 20))

    def draw_party_panel(self):
        x = 40
        y = 70
        w = 460
        h = 250

        pygame.draw.rect(self.screen, (35, 35, 45), (x, y, w, h))
        pygame.draw.rect(self.screen, (120, 120, 140), (x, y, w, h), 2)

        title = self.font.render("PARTY", True, (255, 255, 255))
        self.screen.blit(title, (x + 15, y + 10))

        self.party_rects = []

        row_y = y + 45

        for member in self.session.party.members:
            rect = pygame.Rect(x + 15, row_y, w - 30, 55)
            self.party_rects.append((member, rect))

            if member == self.selected_actor:
                color = (70, 90, 120)
            else:
                color = (50, 50, 60)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (130, 130, 150), rect, 1)

            condition = "UNCONSCIOUS" if member.is_unconscious() else "READY"

            line1 = f"{member.name} | {condition}"
            line2 = (
                f"HP {member.hp}/{member.max_hp} | "
                f"MP {member.mp}/{member.max_mp} | "
                f"Pain {member.pain}/{member.max_pain}"
            )

            self.screen.blit(
                self.small_font.render(line1, True, (240, 240, 240)),
                (rect.x + 10, rect.y + 8)
            )
            self.screen.blit(
                self.small_font.render(line2, True, (210, 210, 210)),
                (rect.x + 10, rect.y + 30)
            )

            row_y += 65

    def draw_enemy_panel(self):
        x = 560
        y = 70
        w = 500
        h = 380

        enemy = self.session.enemy

        pygame.draw.rect(self.screen, (35, 35, 45), (x, y, w, h))
        pygame.draw.rect(self.screen, (120, 120, 140), (x, y, w, h), 2)

        title = self.font.render("ENEMY", True, (255, 255, 255))
        self.screen.blit(title, (x + 15, y + 10))

        enemy_info = (
            f"{enemy.name} | HP {enemy.hp}/{enemy.max_hp} | "
            f"ATK {enemy.attack} | DEF {enemy.defense}"
        )

        self.screen.blit(
            self.small_font.render(enemy_info, True, (230, 230, 230)),
            (x + 15, y + 45)
        )

        intent = enemy.current_intent.get("hint", "No intent.")
        self.screen.blit(
            self.small_font.render(f"Intent: {intent}", True, (255, 220, 140)),
            (x + 15, y + 75)
        )

        self.part_rects = []

        row_y = y + 115

        for part_key, part in enemy.body_parts.items():
            rect = pygame.Rect(x + 15, row_y, w - 30, 45)
            self.part_rects.append((part_key, rect))

            if part_key == self.selected_part_key:
                color = (90, 70, 70)
            else:
                color = (50, 50, 60)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (130, 130, 150), rect, 1)

            text = (
                f"{part.name} | HP {part.hp}/{part.max_hp} | "
                f"ACC {int(part.accuracy * 100)}% | {part.status}"
            )

            self.screen.blit(
                self.small_font.render(text, True, (230, 230, 230)),
                (rect.x + 10, rect.y + 12)
            )

            row_y += 52

    def draw_log_panel(self):
        x = 40
        y = 340
        w = 460
        h = 250

        pygame.draw.rect(self.screen, (35, 35, 45), (x, y, w, h))
        pygame.draw.rect(self.screen, (120, 120, 140), (x, y, w, h), 2)

        title = self.font.render("COMBAT LOG", True, (255, 255, 255))
        self.screen.blit(title, (x + 15, y + 10))

        logs = self.session.get_latest_logs(limit=9)

        line_y = y + 45

        for log in logs:
            rendered = self.small_font.render(log[:58], True, (220, 220, 220))
            self.screen.blit(rendered, (x + 15, line_y))
            line_y += 22

    def draw_buttons(self):
        for button in self.buttons:
            button.draw(self.screen, self.font)

    def draw_selection_info(self):
        x = 560
        y = 470

        actor_name = self.selected_actor.name if self.selected_actor else "None"
        part_name = self.selected_part_key if self.selected_part_key else "None"

        lines = [
            f"Selected actor: {actor_name}",
            f"Selected target part: {part_name}",
            "Flow: choose actor -> choose enemy part -> click action"
        ]

        for i, line in enumerate(lines):
            self.screen.blit(
                self.small_font.render(line, True, (230, 230, 230)),
                (x, y + i * 24)
            )