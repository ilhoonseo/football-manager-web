import pygame
import random
import math
from enum import Enum
import os
import sys

pygame.init()

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)

# 화면 설정
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
GREEN = (34, 139, 34)
LIGHT_GREEN = (50, 200, 50)
DARK_GREEN = (0, 100, 0)
PITCH_GREEN = (25, 120, 50)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
CYAN = (0, 200, 200)
PURPLE = (200, 100, 200)
ORANGE = (255, 165, 0)

# 선수 위치
class Position(Enum):
    GK = "GK"      # 골키퍼
    DEF = "DEF"    # 수비수
    MID = "MID"    # 미드필더
    FWD = "FWD"    # 공격수

POSITION_COLORS = {
    Position.GK: CYAN,
    Position.DEF: BLUE,
    Position.MID: YELLOW,
    Position.FWD: RED
}

POSITION_NAMES = {
    Position.GK: "골키퍼",
    Position.DEF: "수비수",
    Position.MID: "미드필더",
    Position.FWD: "공격수"
}

# 한글 폰트 설정
def get_korean_font(size):
    """한글 폰트 반환 - Windows 폰트 파일 직접 사용"""
    
    # Windows 시스템 폰트 디렉토리에서 한글 폰트 찾기
    font_dir = os.path.expandvars(r'%WINDIR%\Fonts')
    
    # 시도할 한글 폰트들 (우선순위 순)
    font_files = [
        'malgun.ttf',     # 맑은고딕 (권장)
        'malgungothic.ttf',
        'gulim.ttc',      # 굴림
        'gulimche.ttc',
        'dotum.ttc',      # 돋움
        'dotumche.ttc',
    ]
    
    # 폰트 파일 찾기
    for font_file in font_files:
        font_path = os.path.join(font_dir, font_file)
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, size)
                return font
            except Exception as e:
                continue
    
    # 폴백: 시스템 기본 폰트로 시도
    try:
        font = pygame.font.SysFont('malgun', size)
        return font
    except:
        pass
    
    try:
        font = pygame.font.SysFont('gulim', size)
        return font
    except:
        pass
    
    # 최후의 수단: 기본 폰트
    return pygame.font.Font(None, size)

class Player:
    def __init__(self, name, position, overall):
        self.name = name
        self.position = position
        self.overall = overall  # 능력치 1-99
        self.salary = 50000 * (overall / 50)
        self.market_value = 1000000 * (overall / 50)
        
    def get_color(self):
        return POSITION_COLORS[self.position]

class Team:
    def __init__(self, name, initial_budget=5000000):
        self.name = name
        self.budget = initial_budget
        self.players = []
        self.formation = "4-3-3"  # 기본 포메이션
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0
        self.tactics = "균형"  # 균형, 공격, 수비
        
    def add_player(self, player):
        if len(self.players) < 11:
            self.players.append(player)
            return True
        return False
    
    def get_starting_xi(self):
        """선발 11명 반환"""
        return self.players[:11]
    
    def get_points(self):
        return self.wins * 3 + self.draws
    
    def get_goal_diff(self):
        return self.goals_for - self.goals_against
    
    def get_team_strength(self):
        """팀의 전체 전력 계산"""
        if not self.players:
            return 0
        return sum(p.overall for p in self.players[:11]) / 11
    
    def get_total_salary(self):
        return sum(p.salary for p in self.players)

class MatchSimulator:
    @staticmethod
    def simulate_match(home_team, away_team):
        """경기 시뮬레이션"""
        home_strength = home_team.get_team_strength()
        away_strength = away_team.get_team_strength()
        
        # 홈 어드밴티지 (5% 보너스)
        home_strength *= 1.05
        
        # 기본 득점 계산
        home_goals = MatchSimulator.calculate_goals(home_strength, away_strength, 
                                                    home_team.tactics)
        away_goals = MatchSimulator.calculate_goals(away_strength, home_strength, 
                                                    away_team.tactics)
        
        return home_goals, away_goals
    
    @staticmethod
    def calculate_goals(team_strength, opponent_strength, tactics):
        """득점 계산"""
        base_goals = 2.0
        
        # 전술에 따른 수정
        if tactics == "공격":
            base_goals += 0.5
        elif tactics == "수비":
            base_goals -= 0.5
        
        # 팀 강도 반영
        ratio = team_strength / max(opponent_strength, 1)
        base_goals *= (0.5 + ratio * 0.5)
        
        # 운의 요소
        variance = random.gauss(0, 0.5)
        goals = max(0, int(base_goals + variance + 0.5))
        
        return goals

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Football Manager - 축구 팀 매니저")
        self.clock = pygame.time.Clock()
        
        # 한글 폰트 설정
        self.font_title = get_korean_font(40)
        self.font_large = get_korean_font(32)
        self.font_medium = get_korean_font(24)
        self.font_small = get_korean_font(18)
        
        self.player_team = self.create_team()
        self.cpu_teams = [self.create_cpu_team(f"팀 {i}") for i in range(1, 4)]
        
        self.game_state = "menu"  # menu, main, match, transfer, formation
        self.selected_player = None
        self.current_week = 1
        self.season = 1
        self.match_results = []
        self.formation_setup = False
        self.animation_frame = 0
        
    def create_team(self):
        """플레이어 팀 생성"""
        team = Team("당신의 팀")
        positions = [Position.GK] + [Position.DEF] * 4 + [Position.MID] * 3 + [Position.FWD] * 3
        
        names = ["이준성", "박준호", "김민준", "이승우", "조현우",
                 "손흥민", "이강인", "황인범", "손준호", "김신욱", "조규성"]
        
        for name, pos in zip(names, positions):
            overall = random.randint(70, 88)
            team.add_player(Player(name, pos, overall))
        
        return team
    
    def create_cpu_team(self, name):
        """CPU 팀 생성"""
        team = Team(name)
        positions = [Position.GK] + [Position.DEF] * 4 + [Position.MID] * 3 + [Position.FWD] * 3
        
        cpu_names = ["이대호", "박주영", "기성용", "이청용", "차두리",
                     "설기현", "박종우", "고종수", "이동국", "유상철", "정대세"]
        
        for i, (pos, name) in enumerate(zip(positions, cpu_names)):
            overall = random.randint(65, 85)
            team.add_player(Player(f"{name}_{i}", pos, overall))
        
        return team
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state != "menu":
                        self.game_state = "main"
                elif event.key == pygame.K_m:
                    if self.game_state == "main":
                        self.play_next_match()
                elif event.key == pygame.K_t:
                    if self.game_state == "main":
                        self.game_state = "transfer"
                elif event.key == pygame.K_f:
                    if self.game_state == "main":
                        self.game_state = "formation"
                elif event.key == pygame.K_1:
                    if self.game_state == "formation":
                        self.player_team.formation = "4-3-3"
                elif event.key == pygame.K_2:
                    if self.game_state == "formation":
                        self.player_team.formation = "4-2-4"
                elif event.key == pygame.K_3:
                    if self.game_state == "formation":
                        self.player_team.formation = "3-5-2"
                elif event.key == pygame.K_4:
                    if self.game_state == "formation":
                        self.player_team.formation = "5-3-2"
                elif event.key == pygame.K_5:
                    if self.game_state == "formation":
                        self.player_team.tactics = "균형"
                elif event.key == pygame.K_6:
                    if self.game_state == "formation":
                        self.player_team.tactics = "공격"
                elif event.key == pygame.K_7:
                    if self.game_state == "formation":
                        self.player_team.tactics = "수비"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                self.handle_click(mouse_pos)
        
        return True
    
    def handle_click(self, pos):
        """마우스 클릭 처리"""
        if self.game_state == "menu":
            if self.start_button_rect.collidepoint(pos):
                self.game_state = "main"
        
        elif self.game_state == "main":
            # 상단 버튼 클릭
            if 50 <= pos[0] <= 150 and 20 <= pos[1] <= 50:
                self.play_next_match()
            elif 170 <= pos[0] <= 270 and 20 <= pos[1] <= 50:
                self.game_state = "transfer"
            elif 290 <= pos[0] <= 390 and 20 <= pos[1] <= 50:
                self.game_state = "formation"
    
    def play_next_match(self):
        """경기 진행"""
        opponent = random.choice(self.cpu_teams)
        home_goals, away_goals = MatchSimulator.simulate_match(self.player_team, opponent)
        
        # 통계 업데이트
        self.player_team.goals_for += home_goals
        self.player_team.goals_against += away_goals
        opponent.goals_for += away_goals
        opponent.goals_against += home_goals
        
        if home_goals > away_goals:
            self.player_team.wins += 1
            opponent.losses += 1
        elif home_goals == away_goals:
            self.player_team.draws += 1
            opponent.draws += 1
        else:
            self.player_team.losses += 1
            opponent.wins += 1
        
        self.match_results.append({
            'week': self.current_week,
            'opponent': opponent.name,
            'goals_for': home_goals,
            'goals_against': away_goals,
            'result': '승' if home_goals > away_goals else '무' if home_goals == away_goals else '패'
        })
        
        self.current_week += 1
        self.game_state = "match"
    
    def draw_menu(self):
        """메뉴 화면"""
        # 그라데이션 배경
        for y in range(WINDOW_HEIGHT):
            color = (
                int(0 + (25 - 0) * y / WINDOW_HEIGHT),
                int(100 + (120 - 100) * y / WINDOW_HEIGHT),
                int(0 + (50 - 0) * y / WINDOW_HEIGHT)
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # 축구장 패턴
        for x in range(0, WINDOW_WIDTH, 100):
            for y in range(0, WINDOW_HEIGHT, 100):
                pygame.draw.rect(self.screen, (35, 130, 60, 50), (x, y, 100, 100), 1)
        
        # 제목
        title = self.font_title.render("⚽ FOOTBALL MANAGER", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_large.render("축구 팀 매니징 게임", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 시작 버튼
        self.start_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 250, 200, 60)
        pygame.draw.rect(self.screen, LIGHT_GREEN, self.start_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.start_button_rect, 4)
        
        start_text = self.font_large.render("게임 시작", True, BLACK)
        start_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, start_rect)
        
        # 설명
        info_texts = [
            "M: 경기 진행  |  T: 선수 이적  |  F: 포메이션 설정  |  ESC: 메뉴",
            "",
            "당신은 축구 팀의 감독입니다.",
            "전술을 짜고 포메이션을 설정하여 리그 우승을 목표로 하세요!"
        ]
        
        y = 380
        for text in info_texts:
            if text:
                info = self.font_small.render(text, True, CYAN)
                self.screen.blit(info, (WINDOW_WIDTH // 2 - 250, y))
            y += 35
    
    def draw_main(self):
        """메인 화면"""
        self.screen.fill(DARK_GRAY)
        
        # 축구장 배경
        pygame.draw.rect(self.screen, PITCH_GREEN, (700, 80, 680, 700))
        pygame.draw.rect(self.screen, WHITE, (700, 80, 680, 700), 3)
        
        # 중원선
        pygame.draw.line(self.screen, WHITE, (1040, 80), (1040, 780), 2)
        # 중원 원
        pygame.draw.circle(self.screen, WHITE, (1040, 430), 50, 2)
        pygame.draw.circle(self.screen, WHITE, (1040, 430), 5, 2)
        
        # 페널티 박스
        pygame.draw.rect(self.screen, WHITE, (700, 150, 150, 560), 2)
        pygame.draw.rect(self.screen, WHITE, (1230, 150, 150, 560), 2)
        
        # 골 에어리어
        pygame.draw.rect(self.screen, WHITE, (700, 250, 50, 360), 2)
        pygame.draw.rect(self.screen, WHITE, (1330, 250, 50, 360), 2)
        
        # 상단 버튼
        self.draw_button(20, 20, 120, 40, "🎮 경기 진행 [M]", LIGHT_GREEN)
        self.draw_button(160, 20, 120, 40, "🔄 이적 [T]", BLUE)
        self.draw_button(300, 20, 120, 40, "⚙️ 포메이션 [F]", ORANGE)
        
        # 팀 정보 좌측
        self.draw_team_info(20, 80, self.player_team)
        
        # 포메이션 시각화
        self.draw_formation_visualization(700, 80, self.player_team)
        
        # 순위표 우측 상단
        self.draw_standings(20, 450)
        
        # 경기 결과 우측 하단
        self.draw_recent_matches(700, 800)
    
    def draw_button(self, x, y, w, h, text, color):
        """버튼 그리기"""
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 3)
        text_surface = self.font_small.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw_team_info(self, x, y, team):
        """팀 정보 표시"""
        # 배경박스
        pygame.draw.rect(self.screen, DARK_GRAY, (x - 5, y - 5, 310, 360))
        pygame.draw.rect(self.screen, YELLOW, (x - 5, y - 5, 310, 360), 2)
        
        title = self.font_medium.render(team.name, True, YELLOW)
        self.screen.blit(title, (x + 10, y + 5))
        
        texts = [
            f"경기: {team.wins + team.draws + team.losses}",
            f"승: {team.wins} 무: {team.draws} 패: {team.losses}",
            f"득점: {team.goals_for} 실점: {team.goals_against}",
            f"점수: {team.get_points()}",
            f"전술: {team.tactics}",
            f"포메이션: {team.formation}",
            f"팀 강도: {team.get_team_strength():.1f}",
        ]
        
        y_offset = y + 40
        for text in texts:
            text_surface = self.font_small.render(text, True, CYAN)
            self.screen.blit(text_surface, (x + 10, y_offset))
            y_offset += 25
    
    def draw_standings(self, x, y):
        """순위표 표시"""
        # 배경박스
        pygame.draw.rect(self.screen, DARK_GRAY, (x - 5, y - 5, 660, 330))
        pygame.draw.rect(self.screen, CYAN, (x - 5, y - 5, 660, 330), 2)
        
        title = self.font_medium.render("⚽ 리그 순위", True, YELLOW)
        self.screen.blit(title, (x + 10, y + 5))
        
        all_teams = [self.player_team] + self.cpu_teams
        all_teams.sort(key=lambda t: (t.get_points(), t.get_goal_diff()), reverse=True)
        
        y_offset = y + 35
        header = self.font_small.render("순 팀 이름         경기 승 무 패 점수 득실", True, CYAN)
        self.screen.blit(header, (x + 10, y_offset))
        y_offset += 25
        
        for i, team in enumerate(all_teams):
            color = YELLOW if team == self.player_team else WHITE
            text = self.font_small.render(
                f"{i+1:2}. {team.name:<10} {team.wins+team.draws+team.losses:2}  {team.wins:2}  {team.draws:2}  {team.losses:2}  {team.get_points():3}  {team.get_goal_diff():+3}",
                True, color
            )
            self.screen.blit(text, (x + 10, y_offset))
            y_offset += 24
    
    def draw_recent_matches(self, x, y):
        """최근 경기 결과"""
        # 배경박스
        pygame.draw.rect(self.screen, DARK_GRAY, (x - 5, y + 5, 680, 80))
        pygame.draw.rect(self.screen, PURPLE, (x - 5, y + 5, 680, 80), 2)
        
        title = self.font_medium.render("📊 최근 경기 결과", True, YELLOW)
        self.screen.blit(title, (x + 10, y + 10))
        
        y_offset = y + 35
        recent = self.match_results[-3:] if self.match_results else []
        for match in reversed(recent):
            color = GREEN if match['result'] == '승' else YELLOW if match['result'] == '무' else RED
            text = self.font_small.render(
                f"주차 {match['week']}: {match['opponent']} {match['goals_for']}:{match['goals_against']} [{match['result']}]",
                True, color
            )
            self.screen.blit(text, (x + 10, y_offset))
            y_offset += 20
    
    def draw_match(self):
        """경기 결과 화면"""
        # 그라데이션 배경
        for y in range(WINDOW_HEIGHT):
            color = (
                int(34 + (50 - 34) * y / WINDOW_HEIGHT),
                int(139 + (100 - 139) * y / WINDOW_HEIGHT),
                int(34 + (50 - 34) * y / WINDOW_HEIGHT)
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        if self.match_results:
            last_match = self.match_results[-1]
            
            # 축구공 애니메이션
            ball_y = 100 + math.sin(self.animation_frame * 0.05) * 20
            pygame.draw.circle(self.screen, WHITE, (WINDOW_WIDTH // 2, int(ball_y)), 15)
            pygame.draw.circle(self.screen, WHITE, (WINDOW_WIDTH // 2, int(ball_y)), 15, 2)
            self.animation_frame += 1
            
            title = self.font_title.render("경기 결과", True, YELLOW)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 160))
            self.screen.blit(title, title_rect)
            
            # 스코어
            score_text = self.font_large.render(
                f"{self.player_team.name}",
                True, WHITE
            )
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2 - 200, 250))
            self.screen.blit(score_text, score_rect)
            
            score_num = self.font_title.render(
                str(last_match['goals_for']),
                True, YELLOW
            )
            score_num_rect = score_num.get_rect(center=(WINDOW_WIDTH // 2 - 100, 280))
            self.screen.blit(score_num, score_num_rect)
            
            vs = self.font_large.render("vs", True, WHITE)
            vs_rect = vs.get_rect(center=(WINDOW_WIDTH // 2, 280))
            self.screen.blit(vs, vs_rect)
            
            score_num2 = self.font_title.render(
                str(last_match['goals_against']),
                True, YELLOW
            )
            score_num2_rect = score_num2.get_rect(center=(WINDOW_WIDTH // 2 + 100, 280))
            self.screen.blit(score_num2, score_num2_rect)
            
            opponent_text = self.font_large.render(
                f"{last_match['opponent']}",
                True, WHITE
            )
            opponent_rect = opponent_text.get_rect(center=(WINDOW_WIDTH // 2 + 200, 250))
            self.screen.blit(opponent_text, opponent_rect)
            
            result_color = GREEN if last_match['result'] == '승' else YELLOW if last_match['result'] == '무' else RED
            result_text = self.font_title.render(
                last_match['result'], True, result_color
            )
            result_rect = result_text.get_rect(center=(WINDOW_WIDTH // 2, 380))
            self.screen.blit(result_text, result_rect)
            
            info = self.font_medium.render("클릭하거나 ESC를 눌러 계속", True, CYAN)
            info_rect = info.get_rect(center=(WINDOW_WIDTH // 2, 500))
            self.screen.blit(info, info_rect)
    
    def draw_formation_visualization(self, x, y, team):
        """포메이션을 축구장에 시각화"""
        # 선발 11명을 포메이션에 따라 배치
        formations_map = {
            "4-3-3": [(1,), (0, 2, 3, 4), (5, 6, 7), (8, 9, 10)],
            "4-2-4": [(1,), (0, 2, 3, 4), (5, 6), (7, 8, 9, 10)],
            "3-5-2": [(1,), (0, 2, 3), (4, 5, 6, 7, 8), (9, 10)],
            "5-3-2": [(1,), (0, 2, 3, 4, 5), (6, 7, 8), (9, 10)]
        }
        
        formation_positions = formations_map.get(team.formation, formations_map["4-3-3"])
        players = team.get_starting_xi()
        
        # 각 라인별로 배치
        field_width = 680
        field_height = 700
        
        for line_idx, line in enumerate(formation_positions):
            line_y = y + 120 + line_idx * (field_height // 4)
            num_in_line = len(line)
            
            for pos_idx, player_idx in enumerate(line):
                if player_idx < len(players):
                    player = players[player_idx]
                    line_x = x + 50 + (field_width - 100) * (pos_idx + 0.5) / num_in_line
                    
                    # 선수 원 그리기
                    color = player.get_color()
                    pygame.draw.circle(self.screen, color, (int(line_x), int(line_y)), 18)
                    pygame.draw.circle(self.screen, WHITE, (int(line_x), int(line_y)), 18, 2)
                    
                    # 등번호
                    number_text = self.font_small.render(str(player_idx + 1), True, BLACK)
                    number_rect = number_text.get_rect(center=(int(line_x), int(line_y)))
                    self.screen.blit(number_text, number_rect)
    
    def draw_transfer(self):
        """이적 시장 화면"""
        self.screen.fill(DARK_GRAY)
        
        # 배경박스
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, BLUE, (10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), 3)
        
        title = self.font_large.render("🔄 이적 시장", True, YELLOW)
        self.screen.blit(title, (30, 25))
        
        info = self.font_medium.render(f"예산: ${self.player_team.budget:,.0f}", True, CYAN)
        self.screen.blit(info, (30, 70))
        
        y_offset = 120
        for team in self.cpu_teams:
            team_title = self.font_medium.render(f"📋 {team.name} - 판매 선수:", True, YELLOW)
            self.screen.blit(team_title, (30, y_offset))
            y_offset += 35
            
            for player in team.players[:3]:
                pos_name = POSITION_NAMES.get(player.position, player.position.value)
                text = self.font_small.render(
                    f"  🧑 {player.name} ({pos_name}) 능력치:{player.overall} - ${player.market_value:,.0f}",
                    True, player.get_color()
                )
                self.screen.blit(text, (30, y_offset))
                y_offset += 25
            
            y_offset += 15
        
        info = self.font_small.render("ESC: 뒤로 가기", True, CYAN)
        self.screen.blit(info, (30, WINDOW_HEIGHT - 50))
    
    def draw_formation(self):
        """포메이션 설정 화면"""
        self.screen.fill(DARK_GRAY)
        
        # 배경박스
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.draw.rect(self.screen, ORANGE, (10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), 3)
        
        title = self.font_large.render("⚙️ 포메이션 설정", True, YELLOW)
        self.screen.blit(title, (30, 25))
        
        formations = ["4-3-3", "4-2-4", "3-5-2", "5-3-2"]
        tactics = ["균형", "공격", "수비"]
        
        y_offset = 100
        
        # 포메이션 선택
        self.screen.blit(self.font_medium.render("🎯 포메이션:", True, CYAN), (30, y_offset))
        y_offset += 40
        
        for i, formation in enumerate(formations):
            color = LIGHT_GREEN if formation == self.player_team.formation else GRAY
            symbol = "✓" if formation == self.player_team.formation else " "
            text = self.font_medium.render(
                f"  {symbol} {i+1}. {formation}",
                True, color
            )
            self.screen.blit(text, (50, y_offset))
            y_offset += 35
        
        y_offset += 20
        
        # 전술 선택
        self.screen.blit(self.font_medium.render("📍 전술:", True, CYAN), (30, y_offset))
        y_offset += 40
        
        for i, tactic in enumerate(tactics):
            color = LIGHT_GREEN if tactic == self.player_team.tactics else GRAY
            symbol = "✓" if tactic == self.player_team.tactics else " "
            text = self.font_medium.render(
                f"  {symbol} {i+1}. {tactic}",
                True, color
            )
            self.screen.blit(text, (50, y_offset))
            y_offset += 35
        
        info = self.font_small.render("ESC: 뒤로 가기 (숫자 키로 선택)", True, CYAN)
        self.screen.blit(info, (30, WINDOW_HEIGHT - 50))
    
    def draw(self):
        """화면 그리기"""
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "main":
            self.draw_main()
        elif self.game_state == "match":
            self.draw_match()
        elif self.game_state == "transfer":
            self.draw_transfer()
        elif self.game_state == "formation":
            self.draw_formation()
        
        pygame.display.flip()
    
    def run(self):
        """메인 루프"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
