"""
PyGame UI for Guandan game
"""
import pygame
from typing import Optional

from guandan_core.game import GuandanGame
from guandan_core.cards import Card, Rank, Suit


class GuandanUI:
    """PyGame UI for Guandan card game"""

    # Window settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    CARD_WIDTH = 70
    CARD_HEIGHT = 100
    CARD_SPACING = -30  # Negative for overlapping cards

    # Colors
    TABLE_COLOR = (34, 139, 34)  # Green felt
    CARD_COLOR = (255, 255, 255)  # White card
    CARD_BACK_COLOR = (50, 100, 200)  # Blue card back
    SELECTED_BORDER_COLOR = (255, 215, 0)  # Gold
    TEXT_COLOR = (255, 255, 255)  # White text
    BUTTON_COLOR = (70, 130, 180)  # Steel blue
    BUTTON_HOVER_COLOR = (100, 160, 220)
    INFO_BG_COLOR = (0, 0, 0, 150)  # Semi-transparent black

    # Position names
    POSITION_NAMES = {
        0: '南家',
        1: '西家',
        2: '北家',
        3: '东家',
    }

    def __init__(self):
        """Initialize the UI"""
        pygame.init()
        pygame.font.init()

        # Create window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("掼蛋游戏")

        # Fonts - macOS Chinese font support
        import os
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS PingFang
            '/System/Library/Fonts/STHeiti Light.ttc',  # macOS Heiti
            '/System/Library/Fonts/Hiragino Sans GB.ttc',  # macOS Hiragino
        ]

        # Try to find a working Chinese font
        self.font_large = None
        self.font_medium = None
        self.font_small = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_large = pygame.font.Font(font_path, 32)
                    self.font_medium = pygame.font.Font(font_path, 24)
                    self.font_small = pygame.font.Font(font_path, 18)
                    break
                except:
                    continue

        # Fallback to default
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)

        # Game instance
        self.game = GuandanGame()
        self.game.deal_cards()

        # UI state
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_cards: list[Card] = []

        # Card click areas for each position
        self.card_areas: dict[int, list[tuple]] = {}  # player_id -> list of (x, y, width, height, card)

        # AI delay for auto-play
        self.ai_delay = 1000  # ms
        self.last_ai_time = 0
        self.message: Optional[str] = None
        self.message_time = 0

    def run(self):
        """Main game loop"""
        while self.running:
            current_time = pygame.time.get_ticks()

            # Handle AI moves
            if self.game.current_player != 0:  # Not player's turn
                if current_time - self.last_ai_time > self.ai_delay:
                    self._ai_play()
                    self.last_ai_time = current_time

            self._handle_events()
            self._render()
            self.clock.tick(30)

        pygame.quit()

    def _handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse(event.pos, event.button)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._play_cards()
                elif event.key == pygame.K_h:
                    self._hint()
                elif event.key == pygame.K_r:
                    self._restart()

    def _handle_mouse(self, pos: tuple, button: int):
        """Handle mouse clicks"""
        # Force update card_areas first
        self._update_card_areas()

        # Right click = pass (不出)
        if button == 3:
            self._pass_cards()
            return

        # Left click only below here
        # Check if clicking on "pass" button
        if hasattr(self, 'pass_button_rect'):
            if self.pass_button_rect.collidepoint(pos):
                self._pass_cards()
                return

        # Check if clicking on player's cards - iterate in reverse (right to left)
        # because rightmost cards are drawn on top in overlapping layout
        if 0 in self.card_areas:
            # Reverse the list to check rightmost cards first
            for x, y, w, h, card in reversed(self.card_areas[0]):
                # Check if click is within card bounds
                if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                    if button == 1:  # Left click - select/deselect
                        self._toggle_card_selection(card)
                    return

    def _update_card_areas(self):
        """Update card click areas based on current hand"""
        self.card_areas = {}
        player = self.game.players[0]
        hand = player.hand
        if not hand:
            return

        card_y = self.WINDOW_HEIGHT - self.CARD_HEIGHT - 50
        # Correct formula: n cards = n * width + (n-1) * spacing
        total_width = len(hand) * self.CARD_WIDTH + (len(hand) - 1) * self.CARD_SPACING
        start_x = (self.WINDOW_WIDTH - total_width) // 2

        for i, card in enumerate(hand):
            card_x = start_x + i * (self.CARD_WIDTH + self.CARD_SPACING)
            self.card_areas.setdefault(0, []).append(
                (card_x, card_y, self.CARD_WIDTH, self.CARD_HEIGHT, card)
            )

    def _toggle_card_selection(self, card: Card):
        """Toggle card selection"""
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            self.selected_cards.append(card)

    def _play_cards(self):
        """Try to play selected cards"""
        if not self.selected_cards:
            self._show_message("请先选择要出的牌")
            return

        if self.game.current_player != 0:
            self._show_message("等待其他玩家...")
            return

        # Check if player has already played this round
        if len(self.game.current_play) > 0 and self.game.current_play[0] is not None:
            self._show_message("你已出过牌了")
            return

        # Check if selection is valid
        legal_actions = self.game.get_legal_actions(0)

        # Check if selected cards match any legal action
        selected_set = set(self.selected_cards)
        for action in legal_actions:
            if set(action) == selected_set:
                # Try to play the cards
                if self.game.play_cards(0, self.selected_cards):
                    self.selected_cards = []
                    self._show_message("出牌成功")
                return

        # Invalid selection
        self._show_message("选择不符合规则")
        self.selected_cards = []

    def _ai_play(self):
        """AI plays automatically"""
        player_id = self.game.current_player
        legal_actions = self.game.get_legal_actions(player_id)

        if not legal_actions:
            # Pass - use pass_play to properly record the pass
            self.game.pass_play(player_id)
            return

        # Simple AI: play the first valid action
        action = legal_actions[0]
        self.game.play_cards(player_id, action)

    def _hint(self):
        """Show hint for valid moves"""
        if self.game.current_player != 0:
            self._show_message("等待其他玩家...")
            return

        legal_actions = self.game.get_legal_actions(0)
        if not legal_actions:
            self._show_message("没有合法的出牌")
            return

        # Get the first valid action
        best_action = legal_actions[0]
        self.selected_cards = list(best_action)
        self._show_message("提示: 建议出牌")

    def _restart(self):
        """Restart the game"""
        self.game = GuandanGame()
        self.game.deal_cards()
        self.selected_cards = []
        self._show_message("游戏重新开始")

    def _show_message(self, msg: str):
        """Show a temporary message"""
        self.message = msg
        self.message_time = pygame.time.get_ticks()

    def _render(self):
        """Render the game state"""
        # Fill background
        self.screen.fill(self.TABLE_COLOR)

        # Update card click areas
        self._update_card_areas()

        # Render four players' hands
        self._render_player_hand(0, 'bottom')  # South (self)
        self._render_player_hand(2, 'top')      # North
        self._render_player_hand(1, 'left')      # West
        self._render_player_hand(3, 'right')     # East

        # Render current play (center area)
        self._render_current_play()

        # Render game info
        self._render_game_info()

        # Render message
        if self.message:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_time < 2000:
                self._render_message(self.message)
            else:
                self.message = None

        # Render pass button if player can pass
        self._render_pass_button()

        # Render help text
        self._render_help_text()

        pygame.display.flip()

    def _render_player_hand(self, player_id: int, position: str):
        """Render a player's hand"""
        player = self.game.players[player_id]
        hand = player.hand
        is_current = (player_id == self.game.current_player)

        # Calculate position
        if position == 'bottom':
            # Player's own hand (bottom, horizontal)
            card_y = self.WINDOW_HEIGHT - self.CARD_HEIGHT - 50
            card_spacing = self.CARD_SPACING
            # Correct formula: n cards = n * width + (n-1) * spacing
            total_width = len(hand) * self.CARD_WIDTH + (len(hand) - 1) * card_spacing
            start_x = (self.WINDOW_WIDTH - total_width) // 2

            for i, card in enumerate(hand):
                card_x = start_x + i * (self.CARD_WIDTH + card_spacing)
                is_selected = card in self.selected_cards
                self._render_card(card_x, card_y, card, is_selected)

            # Render player name
            name = f"{self.POSITION_NAMES[player_id]} (你)" if player_id == 0 else self.POSITION_NAMES[player_id]
            if is_current:
                name = f"→ {name} ←"
            name_surface = self.font_medium.render(name, True, self.TEXT_COLOR)
            self.screen.blit(name_surface, (start_x, card_y + self.CARD_HEIGHT + 5))

        elif position == 'top':
            # Opponent top (simplified - show card backs)
            card_y = 50
            card_spacing = 15
            num_visible = min(len(hand), 10)  # Show up to 10 cards
            total_width = num_visible * card_spacing
            start_x = (self.WINDOW_WIDTH - total_width) // 2

            for i in range(num_visible):
                card_x = start_x + i * card_spacing
                self._render_card_back(card_x, card_y)

            # Render player name
            name = self.POSITION_NAMES[player_id]
            if is_current:
                name = f"→ {name} ←"
            name_surface = self.font_medium.render(name, True, self.TEXT_COLOR)
            name_x = (self.WINDOW_WIDTH - name_surface.get_width()) // 2
            self.screen.blit(name_surface, (name_x, card_y + self.CARD_HEIGHT + 5))

            # Card count
            count_surface = self.font_small.render(f"{len(hand)}张", True, self.TEXT_COLOR)
            self.screen.blit(count_surface, (name_x + name_surface.get_width() + 10, card_y + self.CARD_HEIGHT + 10))

        elif position == 'left':
            # Left opponent (vertical)
            card_x = 50
            card_spacing = 12
            num_visible = min(len(hand), 8)
            start_y = (self.WINDOW_HEIGHT - num_visible * card_spacing) // 2

            for i in range(num_visible):
                card_y = start_y + i * card_spacing
                self._render_card_back(card_x, card_y, vertical=True)

            # Render player name
            name = self.POSITION_NAMES[player_id]
            if is_current:
                name = f"→ {name} ←"
            name_surface = self.font_medium.render(name, True, self.TEXT_COLOR)
            self.screen.blit(name_surface, (card_x + self.CARD_WIDTH + 10, start_y))

            # Card count
            count_surface = self.font_small.render(f"{len(hand)}张", True, self.TEXT_COLOR)
            self.screen.blit(count_surface, (card_x + self.CARD_WIDTH + 10, start_y + 30))

        elif position == 'right':
            # Right opponent (vertical)
            card_x = self.WINDOW_WIDTH - self.CARD_WIDTH - 50
            card_spacing = 12
            num_visible = min(len(hand), 8)
            start_y = (self.WINDOW_HEIGHT - num_visible * card_spacing) // 2

            for i in range(num_visible):
                card_y = start_y + i * card_spacing
                self._render_card_back(card_x, card_y, vertical=True)

            # Render player name
            name = self.POSITION_NAMES[player_id]
            if is_current:
                name = f"← {name} →"
            name_surface = self.font_medium.render(name, True, self.TEXT_COLOR)
            name_x = card_x - name_surface.get_width() - 10
            self.screen.blit(name_surface, (name_x, start_y))

            # Card count
            count_surface = self.font_small.render(f"{len(hand)}张", True, self.TEXT_COLOR)
            self.screen.blit(count_surface, (name_x, start_y + 30))

    def _render_card(self, x: int, y: int, card: Card, is_selected: bool = False):
        """Render a single card"""
        # Card background
        card_rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        pygame.draw.rect(self.screen, self.CARD_COLOR, card_rect, border_radius=5)

        # Card border
        border_color = self.SELECTED_BORDER_COLOR if is_selected else (0, 0, 0)
        pygame.draw.rect(self.screen, border_color, card_rect, width=2, border_radius=5)

        # If selected, draw card slightly higher
        if is_selected:
            y_offset = -15

        # Card rank and suit
        if card.suit is not None:
            # Color based on suit
            if card.suit in (Suit.HEART, Suit.DIAMOND):
                color = (220, 20, 60)  # Red
            else:
                color = (0, 0, 0)  # Black

            # Rank
            rank_text = Card.RANK_NAMES.get(card.rank, str(card.rank))
            rank_surface = self.font_large.render(rank_text, True, color)
            self.screen.blit(rank_surface, (x + 5, y + 5))

            # Suit symbol
            suit_symbol = Card.SUIT_SYMBOLS.get(card.suit, '')
            suit_surface = self.font_medium.render(suit_symbol, True, color)
            self.screen.blit(suit_surface, (x + 5, y + 35))

            # Corner suit
            corner_suit = self.font_small.render(suit_symbol, True, color)
            self.screen.blit(corner_suit, (x + self.CARD_WIDTH - 20, y + self.CARD_HEIGHT - 25))
            corner_rank = self.font_small.render(rank_text, True, color)
            self.screen.blit(corner_rank, (x + self.CARD_WIDTH - 35, y + self.CARD_HEIGHT - 25))
        else:
            # Joker
            if card.rank == Rank.SMALL_JOKER:
                color = (100, 100, 255)
                text = "小王"
            else:
                color = (255, 100, 100)
                text = "大王"

            text_surface = self.font_large.render(text, True, color)
            text_x = x + (self.CARD_WIDTH - text_surface.get_width()) // 2
            text_y = y + (self.CARD_HEIGHT - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))

    def _render_card_back(self, x: int, y: int, vertical: bool = False):
        """Render card back"""
        if vertical:
            w, h = self.CARD_HEIGHT, self.CARD_WIDTH
        else:
            w, h = self.CARD_WIDTH, self.CARD_HEIGHT

        card_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, self.CARD_BACK_COLOR, card_rect, border_radius=5)

        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), card_rect, width=2, border_radius=5)

        # Draw pattern
        pattern_color = (30, 60, 150)
        for i in range(3):
            offset = 10 + i * 15
            pygame.draw.rect(self.screen, pattern_color,
                           (x + offset, y + offset, w - 2*offset, h - 2*offset), border_radius=3)

    def _render_current_play(self):
        """Render the current play area (center)"""
        center_x = self.WINDOW_WIDTH // 2
        center_y = self.WINDOW_HEIGHT // 2

        # Draw a subtle play area background
        play_area_rect = pygame.Rect(center_x - 200, center_y - 100, 400, 200)
        s = pygame.Surface((400, 200))
        s.set_alpha(50)
        s.fill((0, 0, 0))
        self.screen.blit(s, (center_x - 200, center_y - 100))

        if not self.game.current_play:
            # No cards played yet
            hint_text = self.font_small.render("等待出牌...", True, (200, 200, 200))
            text_x = center_x - hint_text.get_width() // 2
            text_y = center_y - hint_text.get_height() // 2
            self.screen.blit(hint_text, (text_x, text_y))
            return

        # Debug: show current_play state
        debug_text = f"current_play: {self.game.current_play}"
        debug_surf = self.font_small.render(debug_text, True, (255, 0, 0))
        self.screen.blit(debug_surf, (10, 50))

        # Render each player's played cards
        for player_id, cards in enumerate(self.game.current_play):
            if cards is None:
                continue

            # Calculate position for each player's play
            if player_id == 0:  # South
                x = center_x - len(cards) * 20 // 2
                y = center_y + 80
                label = "南家"
            elif player_id == 2:  # North
                x = center_x - len(cards) * 20 // 2
                y = center_y - 80 - self.CARD_HEIGHT
                label = "北家"
            elif player_id == 1:  # West
                x = center_x - 150
                y = center_y - self.CARD_HEIGHT // 2
                label = "西家"
            else:  # East
                x = center_x + 150
                y = center_y - self.CARD_HEIGHT // 2
                label = "东家"

            # Render label
            label_surf = self.font_small.render(label, True, (255, 255, 0))
            self.screen.blit(label_surf, (x, y - 20))

            # Render played cards
            for i, card in enumerate(cards):
                card_x = x + i * 20
                self._render_card(card_x, y, card)

    def _render_game_info(self):
        """Render game information"""
        # Current player info
        info_y = 20
        current_text = f"当前出牌: {self.POSITION_NAMES[self.game.current_player]}"
        current_surface = self.font_medium.render(current_text, True, self.TEXT_COLOR)
        self.screen.blit(current_surface, (20, info_y))

        # Level info
        level_text = f"等级: {self.game.base_level}"
        level_surface = self.font_medium.render(level_text, True, self.TEXT_COLOR)
        self.screen.blit(level_surface, (20, info_y + 30))

        # Last play info
        if self.game.current_play:
            last_play = None
            for play in reversed(self.game.current_play):
                if play is not None:
                    last_play = play
                    break

            if last_play:
                card_names = [str(c) for c in last_play]
                last_text = f"上家出牌: {', '.join(card_names[:5])}"
                if len(card_names) > 5:
                    last_text += "..."
                last_surface = self.font_small.render(last_text, True, self.TEXT_COLOR)
                self.screen.blit(last_surface, (20, info_y + 60))

    def _render_message(self, msg: str):
        """Render a message in the center of screen"""
        # Draw background
        text_surface = self.font_large.render(msg, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))

        # Background
        bg_rect = text_rect.inflate(40, 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect.topleft)

        # Border
        pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, width=2)

        # Text
        self.screen.blit(text_surface, text_rect)

    def _render_pass_button(self):
        """Render pass button when player can pass"""
        # Check if player can pass (not first to play or has no valid moves)
        if self.game.current_player != 0:
            return

        # Check if there are legal actions (if none, player must pass)
        legal_actions = self.game.get_legal_actions(0)
        if legal_actions:
            return  # Player has valid moves, no pass button needed

        # Draw pass button
        button_width = 100
        button_height = 40
        button_x = self.WINDOW_WIDTH - button_width - 20
        button_y = self.WINDOW_HEIGHT - self.CARD_HEIGHT - 100

        self.pass_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, self.BUTTON_COLOR, self.pass_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pass_button_rect, 2, border_radius=5)

        text_surface = self.font_medium.render("不出", True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.pass_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def _pass_cards(self):
        """Player chooses to pass"""
        if self.game.current_player != 0:
            self._show_message("等待其他玩家...")
            return

        # Check if player can pass
        legal_actions = self.game.get_legal_actions(0)
        if legal_actions:
            self._show_message("你有合法的牌可以出")
            return

        # Pass
        self.game.pass_play(0)
        self._show_message("不出")

    def _render_help_text(self):
        """Render help text at bottom"""
        help_text = "左键: 选牌/出牌 | 右键: 不出 | 空格: 出牌 | H: 提示 | R: 重新开始"
        help_surface = self.font_small.render(help_text, True, (200, 200, 200))
        help_x = (self.WINDOW_WIDTH - help_surface.get_width()) // 2
        self.screen.blit(help_surface, (help_x, self.WINDOW_HEIGHT - 30))


if __name__ == '__main__':
    ui = GuandanUI()
    ui.run()
