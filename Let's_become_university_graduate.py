import pygame as pg
import random
import sys
import os

# --- 初期設定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pg.init()
WIDTH, HEIGHT = 1100, 650
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Let's become university graduate")
clock = pg.time.Clock()
font = pg.font.Font(None, 50)
font_small = pg.font.Font(None, 36)

# --- 画像読み込み補助 ---
def load_image(path, required=True):
    if not os.path.isfile(path):
        if required:
            raise FileNotFoundError(f"画像が見つかりません: {path}")
        else:
            return None
    return pg.image.load(path).convert_alpha()

# --- 画像読み込み ---
img_dir = os.path.join(os.path.dirname(__file__), "img")
background = load_image(os.path.join(img_dir, "background.png"))
player_img = load_image(os.path.join(img_dir, "player.png"))
enemy_img = load_image(os.path.join(img_dir, "enemy.png"))
pencil_img = load_image(os.path.join(img_dir, "pencil.png"))
report_img = load_image(os.path.join(img_dir, "report.png"))
lunch_img = load_image(os.path.join(img_dir, "lunch.png"), required=False)
clear_img = load_image(os.path.join(img_dir, "clear.png"), required=False)
gameover_img = load_image(os.path.join(img_dir, "gameover.png"), required=False)

# --- スケール調整 ---
background = pg.transform.scale(background, (WIDTH, HEIGHT))
player_img = pg.transform.scale(player_img, (80, 80))
enemy_img = pg.transform.scale(enemy_img, (60, 60))
pencil_img = pg.transform.scale(pencil_img, (24, 48))
report_img = pg.transform.scale(report_img, (24, 36))
if lunch_img:
    lunch_img = pg.transform.scale(lunch_img, (28, 28))
else:
    lunch_img = pg.Surface((28, 28), pg.SRCALPHA)
    pg.draw.rect(lunch_img, (255, 215, 0), lunch_img.get_rect(), border_radius=6)

# --- ゲームオーバー/クリア画像中央配置 ---
def center_and_scale(img):
    if not img:
        return None, None
    rect = img.get_rect()
    scale = max(WIDTH / rect.width, HEIGHT / rect.height)
    new_size = (int(rect.width * scale), int(rect.height * scale))
    img = pg.transform.scale(img, new_size)
    rect = img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    return img, rect

gameover_img, gameover_rect = center_and_scale(gameover_img)
clear_img, clear_rect = center_and_scale(clear_img)

# --- クラス定義 ---
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img.copy()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 6
        self.max_hp = 3
        self.hp = self.max_hp
        self.inv_timer = 0

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]: self.rect.x -= self.speed
        if keys[pg.K_RIGHT]: self.rect.x += self.speed
        if keys[pg.K_UP]: self.rect.y -= self.speed
        if keys[pg.K_DOWN]: self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())

        if self.inv_timer > 0:
            self.inv_timer -= 1
            self.image.set_alpha(90 if (self.inv_timer // 5) % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)

class Pencil(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pencil_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -12

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Report(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = report_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Enemy(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50),
                                                random.randint(-120, -40)))
        self.speed = random.randint(2, 4)
        self.shoot_delay = random.randint(80, 200)

    def update(self):
        self.rect.y += self.speed
        self.shoot_delay -= 1
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-120, -40)
            self.rect.x = random.randint(50, WIDTH - 50)
        if self.shoot_delay <= 0:
            report = Report(self.rect.centerx, self.rect.bottom)
            enemy_reports.add(report)
            all_sprites.add(report)
            self.shoot_delay = random.randint(100, 260)

class Lunch(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = lunch_img
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40),
                                                random.randint(-180, -60)))
        self.speed = random.randint(2, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.transform.scale(enemy_img, (120, 120))
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.speed_x = 3
        self.hp = 50
        self.timer = 0
        self.shoot_delay = 45

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1
        self.timer += 1
        if self.timer >= self.shoot_delay:
            report = Report(self.rect.centerx, self.rect.bottom)
            enemy_reports.add(report)
            all_sprites.add(report)
            self.timer = 0

# --- ゲーム初期化 ---
def reset_game():
    global all_sprites, pencils, enemies, enemy_reports, lunches, player, score, running, frame_count, bosses
    all_sprites = pg.sprite.Group()
    pencils = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemy_reports = pg.sprite.Group()
    lunches = pg.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for _ in range(5):
        e = Enemy()
        enemies.add(e)
        all_sprites.add(e)
    score = 0
    running = True
    frame_count = 0
    bosses = False

# --- ゲーム変数 ---
target_score = 30
INVINCIBLE_DURATION = 10000
pickup_msg = ""
pickup_timer = 0
lunch_spawn_timer = random.randint(300, 1000)
boss_spawn_time = 20 * 60

# --- メインループ ---
reset_game()
while True:
    while running:
        clock.tick(60)
        frame_count += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                pencil = Pencil(player.rect.centerx, player.rect.top)
                all_sprites.add(pencil)
                pencils.add(pencil)

        # ボス出現
        if not bosses and frame_count >= boss_spawn_time:
            boss = Boss()
            all_sprites.add(boss)
            bosses = True

        # ボスと弾の衝突
        if bosses:
            hits = pg.sprite.spritecollide(boss, pencils, True)
            for _ in hits:
                boss.hp -= 1
                if boss.hp <= 0:
                    boss.kill()
                    score += 50
                    bosses = False
                    frame_count = 0

        # ランチ出現
        lunch_spawn_timer -= 1
        if lunch_spawn_timer <= 0:
            l = Lunch()
            lunches.add(l)
            all_sprites.add(l)
            lunch_spawn_timer = random.randint(600, 1200)

        all_sprites.update()

        # 弾と敵
        hits = pg.sprite.groupcollide(enemies, pencils, True, True)
        for _ in hits:
            score += 1
            e = Enemy()
            enemies.add(e)
            all_sprites.add(e)

        # 敵弾とプレイヤー
        if pg.sprite.spritecollideany(player, enemy_reports):
            if player.inv_timer == 0:
                player.hp -= 1
                player.inv_timer = 60
                if player.hp <= 0:
                    result = "gameover"
                    running = False

        # プレイヤーとランチ
        got_list = pg.sprite.spritecollide(player, lunches, dokill=True)
        if got_list:
            before = player.hp
            player.hp = min(player.max_hp, player.hp + 1)
            pickup_msg = "🍛 HP回復！" if player.hp > before else "🍛 満腹！（上限）"
            pickup_timer = 60

        # クリア条件
        if score >= target_score:
            result = "clear"
            running = False

        # --- 描画 ---
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        screen.blit(font.render(f"単位: {score}", True, (255, 255, 255)), (10, 10))
        hearts = "♥" * player.hp + "♡" * (player.max_hp - player.hp)
        screen.blit(font.render(f"HP: {hearts}", True, (255, 160, 160)), (10, 60))
        if pickup_timer > 0:
            msg = font_small.render(pickup_msg, True, (255, 255, 0))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 16))
            pickup_timer -= 1
        pg.display.flip()

    # --- ゲームオーバー／クリア画面 ---
    screen.fill((0, 0, 0))
    if result == "clear":
        if clear_img: screen.blit(clear_img, clear_rect)
        text1 = font.render("🎓 CONGRATULATIONS! 🎓", True, (255, 255, 0))
        text2 = font.render("大学を卒業しました！", True, (255, 255, 255))
    else:
        if gameover_img: screen.blit(gameover_img, gameover_rect)
        text1 = font.render("GAME OVER", True, (255, 0, 0))
        text2 = font.render(f"取得単位: {score}", True, (255, 255, 255))

    text3 = font.render("Press any key to restart", True, (200, 200, 200))
    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 50))
    pg.display.flip()

    # --- リスタート待機 ---
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit()
            if event.type == pg.KEYDOWN:
                waiting = False
                reset_game()
