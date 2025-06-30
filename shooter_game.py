from pygame import *
from random import randint
import os
import sys

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

init()
mixer.init() # загружаем движок звуков
window = display.set_mode((700, 500))
clock = time.Clock()

# загрузка картинок
background = transform.scale(image.load(os.path.join(base_path, "images", "galaxy.jpg")), (700, 500))
image_player = transform.scale(image.load(os.path.join(base_path, "images", "rocket.png")), (65, 96))
image_enemy = transform.scale(image.load(os.path.join(base_path, "images", "asteroid.png")), (70, 70))
image_bullet = transform.scale(image.load(os.path.join(base_path, "images", "bullet.png")), (21, 42))

# загрузка музыки
mixer.music.load(os.path.join(base_path, "images", 'space.ogg'))
mixer.music.set_volume(0.1) # 10% громкости

# загрузка звуков
fire_sound = mixer.Sound(os.path.join(base_path, "images", 'fire.ogg'))
fire_sound.set_volume(0.3) # 30% громкости


enemy_list = []
bullet_list = []
score = 0
miss_score = 0
score_font = font.Font(None, 36) 

last_shoot_time = 0 
cooldown_time = 500 
sph = 0
spcl = 10000
last_shift = 0
shift_cooldown = 100


RED = (255, 0, 0)
sp = 2
class Area(): 
    
    def __init__(self, x, y, width, height, image): 
        self.rect = Rect(x, y, width, height) 
        self.image = image 
    
    
    def fill(self):
        if self.image:
            window.blit(self.image, self.rect.topleft)
        else: 
            draw.rect(window, (166, 166, 166), self.rect)

    def fill_color(self, color):
        draw.rect(window, color, self.rect)


class Player(Area): 
    # метод рисует картинку поверх прямоугольника
    def fill(self):
        if self.image: # если картинка задана, отображаем картинку
            rotated_image = transform.rotate(image_player, current_angle)
            rotated_rect = rotated_image.get_rect(center=player.rect.center)
            window.blit(rotated_image, rotated_rect.topleft)
        else: # если картинка НЕ задана, просто рисуем серый прямоугольник
            draw.rect(window, RED, self.rect)
            

class Enemy(Area):
    def __init__(self, x, y, width, height, image=None):
        super().__init__(x, y, width, height, image)
        self.speed = sp 

  
    def move(self):
        self.rect.y += self.speed

    
class Bullet(Area):
    def shoot(self):
        self.rect.y -= 10



hero = Area(318, 380, 65, 96, image_player)
enemy = Area(318, 380, 70, 70, image_enemy)
player = Player(318, 380, 65, 96, image_player)
current_angle = 0
orig_image = image_player


move_left = False
move_right = False
shift = False
real_shift_score = 0
run = True
win = False


gameover_font = font.Font(None, 65) 
game_over = False

def show_lose_screen():
    window.blit(background, (0, 0))
    gameover_surf = score_font.render("Ты Проиграл!", True, (255, 255, 255))
    window.blit(gameover_surf, (200, 250))
    score_surf = score_font.render("Нажми R Для Рестарта", True, (255, 255, 255))
    window.blit(score_surf, (210, 310))


def show_win_screen():
    window.blit(background, (0, 0))
    gameover_surf = score_font.render("Ты Победил!", True, (255, 255, 255))
    window.blit(gameover_surf, (200, 250))
    score_surf = score_font.render("Нажми R Для Рестарта", True, (255, 255, 255))
    window.blit(score_surf, (210, 310))
    

def game_reset():
    global score, miss_score, enemy_list, bullet_list, player, game_over, move_left, move_right, win, sp, real_shift_score
    score = 0
    miss_score = 0
    enemy_list = []
    bullet_list = []
    player = Area(318, 380, 65, 96, image_player)
    game_over = False
    move_left = False
    move_right = False
    win = 0
    sp = 2
    real_shift_score = 0


spm = 4

while run:
    if game_over:
        show_lose_screen()
        for e in event.get():
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN:
                if e.key == K_r:
                    game_reset()
        display.update()
        clock.tick(40)
    elif win:
        show_win_screen()
        for e in event.get():
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN:
                if e.key == K_r:
                    game_reset()
        display.update()
        clock.tick(40)
    else:
    

        window.blit(background, (0, 0))

        score_surf = score_font.render("Счёт: " + str(score), True, (255, 255, 255))
        window.blit(score_surf, (10, 10))

        miss_surf = score_font.render("Пропущенно: " + str(miss_score), True, (255, 255, 255))
        window.blit(miss_surf, (10, 50))

        shift_surf = score_font.render("Ускорение: " + str(real_shift_score), True, (255, 255, 255))
        window.blit(shift_surf, (10, 400))
        

        shift_score = time.get_ticks()

        for e in event.get():
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN: 
                if e.key == K_a:
                    move_left = True
                if e.key == K_d:
                    move_right = True
                if e.key == K_LSHIFT:
                    shift = True
                        
            if e.type == KEYUP: 
                if e.key == K_a:
                    move_left = False
                if e.key == K_d:
                    move_right = False
                if e.key == K_LSHIFT:
                    shift = False
                   
                if e.key == K_SPACE:
                    current_time = time.get_ticks()
                    if current_time - last_shoot_time > cooldown_time:
                        
                        bx = hero.rect.centerx - 10 
                        by = hero.rect.top
                        
                        bullet = Bullet(bx, by, 21, 42, image_bullet)
                        
                        bullet_list.append(bullet)
                        last_shoot_time = current_time  
                
           


        
        if shift_score - last_shift > shift_cooldown:
            real_shift_score += 1
            last_shift = shift_score
            
        if shift:
            if real_shift_score > 0:
                        spm = 8
                        real_shift_score -= 1
            else: 
                spm = 4
                    
        if move_right:
            hero.rect.x += spm
            current_angle = min(current_angle - 2,  - 60)
        if move_left:
            hero.rect.x -= spm
            current_angle = min(current_angle + 2,  60)
        else:
            current_angle *= 0.9


        
        if hero.rect.left < 0:
            hero.rect.left = 0
        if hero.rect.right > 700:
            hero.rect.right = 700

        if randint(1, 30) == 1:
            enemy = Enemy(randint(50, 650), -50, 70, 70, image_enemy)
            enemy_list.append(enemy)
            sptime = time.get_ticks()
            if sptime - sph > spcl:
                sp += 1
                sph = sptime  

        for e in enemy_list:
            e.fill()
            e.move()

            if hero.rect.colliderect(e.rect) or miss_score == 10:
                game_over = True
            
        

        for enemy in enemy_list:
            if enemy.rect.top > 500:
                enemy_list.remove(enemy)

                miss_score += 1

        for b in bullet_list:
            b.fill()
            b.shoot()
            for enemy in enemy_list:
                if enemy.rect.colliderect(b.rect):
                    enemy_list.remove(enemy)
                    bullet_list.remove(b)
                    score += 1
                    if score == 20:
                        win = True
        for bulllet in bullet_list:
            if bullet.rect.top < 0:
                bullet_list.remove(bullet)

        
                

        hero.fill()
        

    display.update()
    clock.tick(40)