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

# --- 画像読み込み補助 ---
def load_image(path, required=True):
    """
    ファイル存在をチェックして読み込み（失敗時は分かりやすく例外を出す）
    """
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
item_path = os.path.join(img_dir, "item.png")

# --- 画像読み込み（例外が起きたら原因を表示） ---
try:
    background = load_image(bg_path)
    player_img = load_image(player_path)
    enemy_img = load_image(enemy_path)
    pencil_img = load_image(pencil_path)
    report_img = load_image(report_path)
    item_img = load_image(item_path)
except FileNotFoundError as e:
    print(e)
    print("ex5/img/ フォルダに必要な画像を入れて、ファイル名が正しいか確認してください。")
    pg.quit()
    sys.exit(1)

# --- 画像サイズ調整（必要に応じて変更してください） ---
# 背景は画面サイズに合わせる
background = pg.transform.scale(background, (WIDTH, HEIGHT))

# キャラ等のサイズ（ここを変えると見た目調整できます）
player_img = pg.transform.scale(player_img, (80, 80))
enemy_img  = pg.transform.scale(enemy_img,  (60, 60))
pencil_img = pg.transform.scale(pencil_img, (24, 48))
report_img = pg.transform.scale(report_img, (24, 36))
item_img = pg.transform.scale(item_img, (24, 48))

# --- クラス定義（Player.update は引数なし） ---
class Player(pg.sprite.Sprite):
    """主人公キャラクターを表すクラス。矢印キーで操作可能。"""

    def __init__(self):
        """Player インスタンスを初期化する。"""
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-60))
        self.speed = 6

    def update(self):
        """プレイヤー位置を更新する。キー入力に応じて移動。"""
        # keys をここで取得することで all_sprites.update() だけで動く
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pg.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pg.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        # 画面内に留める
        self.rect.clamp_ip(screen.get_rect())

class Pencil(pg.sprite.Sprite):
    """プレイヤーが発射する「えんぴつ」弾を表すクラス。"""
    def __init__(self, x, y, dx = 0):
        """
        弾を初期化。

        Args:
            x (int): 発射位置のX座標。
            y (int): 発射位置のY座標。
        """
        super().__init__()
        self.image = pencil_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -12
        self.dx = dx

    def update(self):
        """弾を上方向に移動し、画面外で消去する。"""
        self.rect.y += self.speed
        self.rect.x += self.dx
        if self.rect.bottom < 0  or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Enemy(pg.sprite.Sprite):
    """課題（敵）キャラクターを表すクラス。下方向に移動し、一定間隔で弾を撃つ。"""
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50),
                                                random.randint(-120, -40)))
        self.speed = random.randint(2, 4)
        self.shoot_delay = random.randint(80, 200)

    def update(self):
        self.rect.y += self.speed
        self.shoot_delay -= 1
        if self.rect.top > HEIGHT:
            # 画面外に出たら上にリスポーン
            self.rect.y = random.randint(-120, -40)
            self.rect.x = random.randint(50, WIDTH-50)
            self.speed = random.randint(2, 4)
        if self.shoot_delay <= 0:
            report = Report(self.rect.centerx, self.rect.bottom)
            enemy_reports.add(report)
            all_sprites.add(report)
            self.shoot_delay = random.randint(100, 260)

class Report(pg.sprite.Sprite):
    """敵が発射する「レポート」弾を表すクラス。"""
    def __init__(self, x, y):
        """
        レポート弾を初期化。

        Args:
            x (int): 発射位置のX座標。
            y (int): 発射位置のY座標。
        """        
        super().__init__()
        self.image = report_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

    def update(self):
        """レポート弾を下方向に移動し、画面外に出たら削除する。"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Item(pg.sprite.Sprite):
    """プレイヤーが取得できるアイテムを表すクラス。一定速度で下に落下する。"""

    def __init__(self, x: int, y: int) -> None:
        """
        アイテムを初期化する。

        Args:
            x (int): 初期X座標。
            y (int): 初期Y座標。
        """
        super().__init__()
        self.image: pg.Surface = item_img
        self.rect: pg.Rect = self.image.get_rect(center=(x, y))
        self.speed: int = random.randint(2, 4)

    def update(self) -> None:
        """アイテムを下方向に移動し、画面外に出たら再配置する。"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            # 上にリスポーン
            self.rect.y = random.randint(-120, -40)
            self.rect.x = random.randint(50, WIDTH - 50)
            self.speed = random.randint(2, 4)


# --- グループ定義 ---
all_sprites = pg.sprite.Group()
pencils = pg.sprite.Group()
enemies = pg.sprite.Group()
enemy_reports = pg.sprite.Group()
items = pg.sprite.Group()

player = Player()
all_sprites.add(player)   # ← ここは必ず追加しておく（描画されるように）

# 敵を追加
for i in range(5):
    e = Enemy()
    enemies.add(e)
    all_sprites.add(e)
for i in range(2):
    item = Item(random.randint(50, WIDTH-50), random.randint(-150, -50))
    items.add(item)
    all_sprites.add(item)

score = 0
i_frug = 0 

# --- メインループ ---
running = True
while running:
    clock.tick(60)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and i_frug == 1:
        # 真っすぐ発射
            pencil = Pencil(player.rect.centerx, player.rect.top)
            # 左斜め発射
            pencil_left = Pencil(player.rect.centerx, player.rect.top, dx=-5)
            # 右斜め発射
            pencil_right = Pencil(player.rect.centerx, player.rect.top, dx=5)

            all_sprites.add(pencil, pencil_left, pencil_right)
            pencils.add(pencil, pencil_left, pencil_right)

        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            # スペースで鉛筆弾を作り、グループへ追加
            pencil = Pencil(player.rect.centerx, player.rect.top)
            all_sprites.add(pencil)
            pencils.add(pencil)
        

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
    if pg.sprite.spritecollideany(player, enemy_reports):
        running = False  # ゲームオーバー

    # プレイヤーとアイテムの衝突判定
    item_hits = pg.sprite.spritecollide(player, items, True)
    for _ in item_hits:
        i_frug = 1  # 例：アイテムを取ると弾数が増える
    # 新しいアイテムをリスポーン
        i = Item(random.randint(50, WIDTH-50), random.randint(-150, -50))
        items.add(i)
        all_sprites.add(i)

    # 描画
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    score_text = font.render(f"単位: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    pg.display.flip()

# --- ゲームオーバー画面 ---
screen.fill((0, 0, 0))
gameover_text = font.render("GAME OVER", True, (255, 0, 0))
score_text = font.render(f"取得単位: {score}", True, (255, 255, 255))
screen.blit(gameover_text, (WIDTH//2 - 150, HEIGHT//2 - 50))
screen.blit(score_text, (WIDTH//2 - 150, HEIGHT//2))
pg.display.flip()
pg.time.wait(2500)

pg.quit()
sys.exit()
