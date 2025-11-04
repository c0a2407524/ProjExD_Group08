import pygame as pg
import random
import sys
import time
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
    """ファイル存在をチェックして読み込み（失敗時は分かりやすく例外を出す）"""
    if not os.path.isfile(path):
        if required:
            raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
        else:
            return None
    return pg.image.load(path).convert_alpha()

# --- 画像パス ---
current_dir = os.path.dirname(__file__)
img_dir = os.path.join(current_dir, "img")
bg_path = os.path.join(img_dir, "background.png")
player_path = os.path.join(img_dir, "player.png")
enemy_path = os.path.join(img_dir, "enemy.png")
pencil_path = os.path.join(img_dir, "pencil.png")
report_path = os.path.join(img_dir, "report.png")
lunch_path = os.path.join(img_dir, "lunch.png") #追加C0A24151
gameover_path = os.path.join(img_dir, "gameover.png")
clear_path = os.path.join(img_dir, "clear.png")

# --- 画像読み込み ---
try:
    background = load_image(bg_path)
    player_img = load_image(player_path)
    enemy_img = load_image(enemy_path)
    pencil_img = load_image(pencil_path)
    report_img = load_image(report_path)
    lunch_img = load_image(lunch_path, required=False) #追加C0A24151
    gameover_img = load_image(gameover_path, required=False)
    clear_img = load_image(clear_path, required=False)
except FileNotFoundError as e:
    print(e)
    print("ex5/img/ フォルダに必要な画像を入れて、ファイル名が正しいか確認してください。")
    pg.quit()
    sys.exit(1)

# --- 画像サイズ調整 ---
background = pg.transform.scale(background, (WIDTH, HEIGHT))
player_img = pg.transform.scale(player_img, (80, 80))
enemy_img = pg.transform.scale(enemy_img, (60, 60))
pencil_img = pg.transform.scale(pencil_img, (24, 48))
report_img = pg.transform.scale(report_img, (24, 36))

# 学食ランチ（無ければフォールバックで金色の四角）#追加C0A24151
if lunch_img is None:
    lunch_img = pg.Surface((28, 28), pg.SRCALPHA)
    pg.draw.rect(lunch_img, (255, 215, 0), lunch_img.get_rect(), border_radius=6)
else:
    lunch_img = pg.transform.scale(lunch_img, (28, 28))

# --- クラス定義（Player.update は引数なし） ---
class Player(pg.sprite.Sprite):
    """主人公キャラクターを表すクラス。矢印キーで操作可能。"""
# --- ゲームオーバー・クリア画像の比率維持＆中央配置 ---
gameover_rect = None
if gameover_img:
    src_rect = gameover_img.get_rect()
    scale = max(WIDTH / src_rect.width, HEIGHT / src_rect.height)
    new_size = (int(src_rect.width * scale), int(src_rect.height * scale))
    gameover_img = pg.transform.scale(gameover_img, new_size)
    gameover_rect = gameover_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

clear_rect = None
if clear_img:
    src_rect = clear_img.get_rect()
    scale = max(WIDTH / src_rect.width, HEIGHT / src_rect.height)
    new_size = (int(src_rect.width * scale), int(src_rect.height * scale))
    clear_img = pg.transform.scale(clear_img, new_size)
    clear_rect = clear_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# --- クラス定義 ---
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.base_image = player_img
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-60))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 6
        # --- HP & 無敵 --- #追加C0A24151
        self.max_hp = 3
        self.hp = self.max_hp
        self.inv_timer = 0  # 被弾後の無敵フレーム


    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pg.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pg.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())
        # 無敵時間のカウントダウン #追加C0A24151
        if self.inv_timer > 0:
            self.inv_timer -= 1
        # 被弾中の点滅 #追加C0A24151
        if self.inv_timer > 0:
            # 5フレ周期で明滅（80↔255）
            if (self.inv_timer // 5) % 2 == 0:
                self.image.set_alpha(90)
            else:
                self.image.set_alpha(255)
        else:
            # 通常時は不透明
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
            self.speed = random.randint(2, 4)
        if self.shoot_delay <= 0:
            report = Report(self.rect.centerx, self.rect.bottom)
            enemy_reports.add(report)
            all_sprites.add(report)
            self.shoot_delay = random.randint(100, 260)

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

class Lunch(pg.sprite.Sprite): #追加C0A24151
    """学食ランチ（回復アイテム）。取得でHP+1（上限あり）。"""
    def __init__(self, x=None, y=None):
        super().__init__()
        self.image = lunch_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x if x is not None else random.randint(40, WIDTH - 40)
        self.rect.y = y if y is not None else random.randint(-180, -60)
        self.speed = random.randint(2, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# --- グループ定義 ---
all_sprites = pg.sprite.Group()
pencils = pg.sprite.Group()
enemies = pg.sprite.Group()
enemy_reports = pg.sprite.Group()
lunches = pg.sprite.Group() #追加C0A24151

player = Player()
all_sprites.add(player)   # ← ここは必ず追加しておく（描画されるように）
# 敵を追加
for i in range(5):
    e = Enemy()
    enemies.add(e)
    all_sprites.add(e)

score = 0
#invincibleで無敵時間なのかを判別する
invincible : bool
invincible = False
invincible_end_time = 0
#無敵時間を設定(ミリ秒)
INVINCIBLE_DURATION: int
INVINCIBLE_DURATION = 10000
start = pg.time.get_ticks()

#追加C0A24151
pickup_msg = ""         # 取得メッセージ 
pickup_timer = 0        # メッセージ表示フレーム
# 学食ランチの出現タイミング（10〜20秒に1回くらい）
lunch_spawn_timer = random.randint(300, 1000)  # 60fps前提

# --- メインループ ---
running = True
while running:
    clock.tick(60)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            # スペースで鉛筆弾を作り、グループへ追加
            pencil = Pencil(player.rect.centerx, player.rect.top)
            all_sprites.add(pencil)
            pencils.add(pencil)
        # スコアが15以上であればiキーを押したときにinvincibleフラグをオンにする
        if event.type == pg.KEYDOWN and event.key == pg.K_i and score >=15:
            if invincible == False:
                invincible = True
                start = pg.time.get_ticks()
    
    # --- 学食ランチの出現 --- #追加C0A24151
    lunch_spawn_timer -= 1
    if lunch_spawn_timer <= 0:
        l = Lunch()
        lunches.add(l)
        all_sprites.add(l)
        lunch_spawn_timer = random.randint(600, 1200)

    current = pg.time.get_ticks()
    elapsed = current - start
    # まとめて更新（Player.update は内部でキー取得している）
    all_sprites.update()

    # 衝突判定：弾と敵
    hits = pg.sprite.groupcollide(enemies, pencils, True, True)
    for hit in hits:
        score += 1
        e = Enemy()
        enemies.add(e)
        all_sprites.add(e)
    # 衝突判定：敵の弾とプレイヤー
    # 衝突時の無敵モードを判定する
    if pg.sprite.spritecollideany(player, enemy_reports):
        current = pg.time.get_ticks()#現在時刻の入手
        if invincible == True:
            running = True
            if elapsed >= INVINCIBLE_DURATION:#30秒以上たったら無敵モードを解除
                invincible = False
        elif invincible == False:
            running = False # 無敵モード解除状態で敵に当たるとゲームオーバー

    #追加C0A24151
    # 衝突判定：敵の弾とプレイヤー（HP制＋無敵時間）
    if pg.sprite.spritecollideany(player, enemy_reports):
        if player.inv_timer == 0:
            player.hp -= 1
            player.inv_timer = 60  # 1秒間無敵（60fps）
            if player.hp <= 0:
                running = False  # ゲームオーバー
    
    # 衝突判定：プレイヤーと学食ランチ（回復）
    got_list = pg.sprite.spritecollide(player, lunches, dokill=True)
    if got_list:
        before = player.hp
        player.hp = min(player.max_hp, player.hp + 1)
        if player.hp > before:
            pickup_msg = "🍛 元気回復！HP+1"
        else:
            pickup_msg = "🍛 お腹いっぱい！（上限）"
        pickup_timer = 60  # 1秒表示

    # 描画
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)

    # スコア
    score_text = font.render(f"HP: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    #追加C0A24151
    # HP表示（ハート）：例 ♥♥♡
    hearts = "♥" * player.hp + "♡" * (player.max_hp - player.hp)
    hp_text = font.render(f"HP: {hearts}", True, (255, 160, 160))
    screen.blit(hp_text, (10, 60))
    # 取得メッセージ
    if pickup_timer > 0:
        msg_surf = font_small.render(pickup_msg, True, (255, 255, 0))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 16))
        pickup_timer -= 1
    
def reset_game() -> None:
    """ゲームをリセットして再スタートする。 (Reset and restart the game.)"""
    global all_sprites, pencils, enemies, enemy_reports, player, score, running
    all_sprites = pg.sprite.Group()
    pencils = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemy_reports = pg.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(5):
        e = Enemy()
        enemies.add(e)
        all_sprites.add(e)

    score = 0
    running = True

# --- 初期化 ---
reset_game()
target_score = 30

# --- メインループ ---
while True:  # リスタート対応
    while running:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                pencil = Pencil(player.rect.centerx, player.rect.top)
                all_sprites.add(pencil)
                pencils.add(pencil)

        all_sprites.update()

        # 衝突判定
        hits = pg.sprite.groupcollide(enemies, pencils, True, True)
        for hit in hits:
            score += 1
            e = Enemy()
            enemies.add(e)
            all_sprites.add(e)

        if pg.sprite.spritecollideany(player, enemy_reports):
            result = "gameover"
            running = False

        if score >= target_score:
            result = "clear"
            running = False

        # 描画
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        score_text = font.render(f"単位: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pg.display.flip()

    # --- クリア or ゲームオーバー画面 ---
    if result == "clear":
        if clear_img and clear_rect:
            screen.blit(clear_img, clear_rect)
        else:
            screen.fill((0, 0, 0))
        text1 = None
        text2 = None
    else:
        if gameover_img and gameover_rect:
            screen.blit(gameover_img, gameover_rect)
        else:
            screen.fill((0, 0, 0))
        text1 = font.render("GAME OVER", True, (255, 0, 0))
        text2 = font.render(f"取得単位: {score}", True, (255, 255, 255))

    text3 = font.render("Press any key to restart", True, (200, 200, 200))

    if text1:
        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2 - 50, HEIGHT // 2 - 100))
    if text2:
        screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2 - 50, HEIGHT // 2 - 30))

    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2 - 50, HEIGHT // 2 + 50))
    pg.display.flip()

    # --- リスタート待機 ---
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                waiting = False
                reset_game()


