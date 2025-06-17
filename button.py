import pygame
import os
from text_display import TextDisplay
from game_config import Sounds
import sys

class Button:
    def __init__(self, x, y, width, height, text, action_type=None, type=1):
        # Przyjmujemy środek jako pozycję
        self.action_type=action_type
        self.width = width
        self.height = height
        self.base_rect = pygame.Rect(0, 0, width, height)
        self.base_rect.center = (x, y)
        self.current_rect = self.base_rect.copy()
        self.finished=False
        self.text = text

        self.stat_line = None
        self.shop_line = None
        if isinstance(self.action_type, str) and self.action_type.startswith("change_stat-"):
            try:
                tokens = self.action_type.split("-")
                self.stat_line = int(tokens[1])  # linia do zmiany w statystykach i koszcie
                self.shop_line = int(tokens[1])  # to ta sama linia co stat_line dla kosztu
            except:
                pass

        self.action_type = action_type
        self.hovered = False
        self.scale_factor = 1.6
        self.was_pressed = False
        self.type = type
        self.rescale_offset = 1.2 if type == 1 else 1.0

        # Tekst
        self.text_display = TextDisplay(text, self.base_rect.center[0], self.base_rect.center[1], font_size=(self.width+self.height)//10, glow=False, bold=True)

        # Ścieżki do grafik
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        normal_path = os.path.join(BASE_DIR, f"assets/Button{type}.png")
        hover_path = os.path.join(BASE_DIR, f"assets/Button{type}_hover.png")

        # Wczytanie i przeskalowanie grafik
        self.image_normal = pygame.image.load(normal_path).convert_alpha()
        self.image_hover = pygame.image.load(hover_path).convert_alpha()
        self.image_normal = pygame.transform.smoothscale(self.image_normal, (width, height))
        self.image_hover = pygame.transform.smoothscale(
            self.image_hover,
            (int(width * self.scale_factor / self.rescale_offset), int(height * self.scale_factor))
        )

        if self.action_type and self.action_type.startswith("change_stat-"):
            parts = self.action_type.split("-")
            if len(parts) == 4:
                line_n = int(parts[1])
                inc_stat = int(parts[2])
                inc_shop = int(parts[3])
            shop_file = os.path.join(BASE_DIR, "player_shop.txt")
            stats_file = os.path.join(BASE_DIR, "player_stats.txt")
            limit_file = os.path.join(BASE_DIR, "limits.txt")
            with open(shop_file, "r", encoding="utf-8") as f:
                shop_lines = f.readlines()
            if os.path.exists(stats_file):
                with open(stats_file, "r", encoding="utf-8") as f:
                    stat_lines = f.readlines()
            else:
                stat_lines = []
            if os.path.exists(limit_file):
                with open(limit_file, "r", encoding="utf-8") as f:
                    limit_lines = f.readlines()
            else:
                slimit_lines = []
            while len(limit_lines) < line_n:
                limit_lines.append("99999\n")
            try:
                limit_val = int(limit_lines[line_n - 1].strip())
            except ValueError:
                limit_val = 99999
            try:
                current_stat = int(stat_lines[line_n - 1].strip())
            except ValueError:
                current_stat = 0

            if line_n == 2:
                current_stat *= -1
                limit_val *= -1

            if current_stat >= limit_val:
                self.finished=True

    def draw(self, screen):
        image = self.image_hover if self.hovered else self.image_normal
        screen.blit(image, self.current_rect.topleft)
        if self.stat_line:
            try:
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                shop_path = os.path.join(BASE_DIR, "player_shop.txt")
                stats_path = os.path.join(BASE_DIR, "player_stats.txt")

                shop_val = ""
                stats_val = ""

                if os.path.exists(shop_path):
                    with open(shop_path, "r", encoding="utf-8") as f:
                        shop_lines = f.readlines()
                    if len(shop_lines) >= self.shop_line:
                        shop_val = shop_lines[self.shop_line - 1].strip()

                if os.path.exists(stats_path):
                    with open(stats_path, "r", encoding="utf-8") as f:
                        stats_lines = f.readlines()
                    if len(stats_lines) >= self.stat_line:
                        stats_val = stats_lines[self.stat_line - 1].strip()

                # Wyświetl tekst pod przyciskiem
                font = pygame.font.SysFont("Segoe UI", 24)
                if self.stat_line != 8:
                    if self.finished:
                        info_text = f"Stat: {stats_val}"
                    else:
                        info_text = f"Stat: {stats_val} Cost: {shop_val}"
                if self.stat_line == 8:
                    unlocked_values1=stats_lines[7].strip()
                    unlocked_values=unlocked_values1.split()
                    active_values1=stats_lines[5].strip()
                    active_values=active_values1.split()
                    if self.text == "Ricochet":
                        if "ricochet" not in unlocked_values:
                            info_text="Cost: 25"
                        else:
                            if "ricochet" in active_values:
                                info_text="Activated"
                            else:
                                info_text="Deactivated"
                    if self.text == "Explosive":
                        if "explosive" not in unlocked_values:
                            info_text="Cost: 75"
                        else:
                            if "explosive" in active_values:
                                info_text="Activated"
                            else:
                                info_text="Deactivated"
                    if self.text == "Homing":
                        if "homing" not in unlocked_values:
                            info_text="Koszt: 50"
                        else:
                            if "homing" in active_values:
                                info_text="Activated"
                            else:
                                info_text="Deactivated"
                info_surface = font.render(info_text, True, (207, 128, 255)) 
                info_rect = info_surface.get_rect(midtop=(self.base_rect.centerx, self.base_rect.bottom + 5))
                screen.blit(info_surface, info_rect)
            except Exception as e:
                print(f"Błąd przy wyświetlaniu info: {e}")
        self.text_display.draw(screen)

    def update(self, mouse_pos):
        if self.base_rect.collidepoint(mouse_pos):
            if not self.hovered:
                self.hovered = True
                self._apply_hover_effect()
        else:
            if self.hovered:
                self.hovered = False
                self._reset_hover_effect()

    def _apply_hover_effect(self):
        cx, cy = self.base_rect.center
        new_width = int(self.width * self.scale_factor / self.rescale_offset)
        new_height = int(self.height * self.scale_factor)
        self.current_rect = pygame.Rect(0, 0, new_width, new_height)
        self.current_rect.center = (cx, cy)
        self.text_display.glow=True
        Sounds[6].play()

    def _reset_hover_effect(self):
        self.current_rect = self.base_rect.copy()
        self.text_display.glow=False

    def is_clicked(self, mouse_pos, mouse_click):
        if self.current_rect.collidepoint(mouse_pos):
            if mouse_click and not self.was_pressed:
                self.was_pressed = True
                return True
        return False

    def reset_click(self):
        self.was_pressed = False

    def click(self, level):
        from level import Level
        Sounds[5].play()
        if self.action_type and self.action_type == "quit":
            pygame.quit()
            sys.quit()
        if self.action_type and self.action_type == "load_from_launcher":
            print(f"Przycisk kliknięty. Typ akcji: {self.action_type}")
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            launcher = os.path.join(BASE_DIR, "launch_level.txt")
            with open(launcher, "r", encoding="utf-8") as f:
                launches = f.readlines()
            highscore=int(launches[1])
            current=int(launches[0])
            if current <= highscore:
                new_level=Level()
                new_level.load_from_file(f"level{current}.txt")
                return new_level
            else:
                return level
        if self.action_type and self.action_type.startswith("load-"):
            print(f"Przycisk kliknięty. Typ akcji: {self.action_type}")
            if self.action_type.startswith("load-"):
                level_name = self.action_type[len("load-"):]
                new_level = Level()
                new_level.load_from_file(f"{level_name}.txt")
                return new_level
        else:
            if self.action_type and self.action_type.startswith("change_stat-"):
                print(f"Przycisk kliknięty. Typ akcji: {self.action_type}")
                try:
                    # Parsowanie akcji
                    parts = self.action_type.split("-")
                    if len(parts) == 4:
                        line_n = int(parts[1])
                        inc_stat = int(parts[2])
                        inc_shop = int(parts[3])

                        # Ścieżki do plików
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                        shop_file = os.path.join(BASE_DIR, "player_shop.txt")
                        stats_file = os.path.join(BASE_DIR, "player_stats.txt")
                        limit_file = os.path.join(BASE_DIR, "limits.txt")
                        # Wczytaj linie ze sklepu
                        with open(shop_file, "r", encoding="utf-8") as f:
                            shop_lines = f.readlines()

                        if os.path.exists(stats_file):
                            with open(stats_file, "r", encoding="utf-8") as f:
                                stat_lines = f.readlines()
                        else:
                            stat_lines = []

                        balance = int(shop_lines[7].strip())  # linia 8 (indeks 7)
                        if line_n == 8:
                            active1=stat_lines[5].strip()
                            active=active1.split()
                            active=[word for word in active if word != "default"]
                            if self.text=="Ricochet":
                                if level.ricochet_unlocked==False and balance >= 25:
                                    level.ricochet_unlocked=True
                                    balance -= 25
                                    stat_lines[7]=stat_lines[7]+" ricochet"
                                if level.ricochet_unlocked==True:
                                    if "ricochet" in active:
                                        active=[word for word in active if word != "ricochet"]
                                    else:
                                        active.append("ricochet")

                            if self.text=="Explosive":
                                if level.explosive_unlocked==False and balance >= 75:
                                    level.explosive_unlocked=True
                                    balance -= 75
                                    stat_lines[7]=stat_lines[7]+" explosive"
                                if level.explosive_unlocked==True:
                                    if "explosive" in active:
                                        active=[word for word in active if word != "explosive"]
                                    else:
                                        active.append("explosive")

                            if self.text=="Homing":
                                if level.homing_unlocked==False and balance >= 50:
                                    level.homing_unlocked=True
                                    balance -= 50
                                    stat_lines[7]=stat_lines[7]+" homing"
                                if level.homing_unlocked==True:
                                    if "homing" in active:
                                        active=[word for word in active if word != "homing"]
                                    else:
                                        active.append("homing")

                            shop_lines[7] = f"{balance}\n"
                            if "ricochet" not in active and "explosive" not in active and "homing" not in active:
                                stat_lines[5]="default\n"
                            else:
                                stat_lines[5]=" ".join(active)
                                stat_lines[5]+="\n"
                            with open(shop_file, "w", encoding="utf-8") as f:
                                f.writelines(shop_lines)
                            with open(stats_file, "w", encoding="utf-8") as f:
                                f.writelines(stat_lines)
                            return level
                        cost = int(shop_lines[line_n - 1].strip())

                        if os.path.exists(limit_file):
                            with open(limit_file, "r", encoding="utf-8") as f:
                                limit_lines = f.readlines()
                        else:
                            slimit_lines = []
                        while len(limit_lines) < line_n:
                            limit_lines.append("99999\n")
                        try:
                            limit_val = int(limit_lines[line_n - 1].strip())
                        except ValueError:
                            limit_val = 99999
                        try:
                            current_stat = int(stat_lines[line_n - 1].strip())
                        except ValueError:
                            current_stat = 0

                        if line_n == 2:
                            current_stat *= -1
                            limit_val *= -1

                        if current_stat >= limit_val:
                            self.finished=True
                            print(f"Statystyka na limicie ({current_stat} >= {limit_val}) — zakup anulowany.")
                            return level


                        # Bezpieczne rozszerzenie listy, jeśli za krótka
                        while len(shop_lines) < max(8, line_n):
                            shop_lines.append("0\n")

                        if balance >= cost:
                            # Aktualizacja salda
                            balance -= cost
                            shop_lines[7] = f"{balance}\n"

                            # Aktualizacja kosztu ulepszenia
                            cost += inc_shop
                            shop_lines[line_n - 1] = f"{cost}\n"

                            # Zapis do sklepu
                            with open(shop_file, "w", encoding="utf-8") as f:
                                f.writelines(shop_lines)

                            # Wczytaj i zaktualizuj statystyki
                            while len(stat_lines) < line_n:
                                stat_lines.append("0\n")

                            current_stat = int(stat_lines[line_n - 1].strip())
                            if line_n == 2:
                                inc_stat *= -1
                            current_stat += inc_stat
                            stat_lines[line_n - 1] = f"{current_stat}\n"

                            with open(stats_file, "w", encoding="utf-8") as f:
                                f.writelines(stat_lines)

                            print(f"Zmieniono statystyki: linia {line_n} +{inc_stat}, koszt +{inc_shop}")
                            if line_n == 2:
                                current_stat *= -1
                                limit_val *= -1
                                if current_stat == -20:
                                    self.finished = True
                            if current_stat >= limit_val:
                                self.finished = True
                        else:
                            print("Za mało środków.")
                except Exception as e:
                    print(f"Błąd podczas zmiany statystyk: {e}")
            else:
                print("Przycisk kliknięty, ale brak działania.")
        return level