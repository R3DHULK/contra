import pygame
import sys
import random
import pygame.mixer

pygame.init()

WIDTH = 1200
HEIGHT = 600
score = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contra")

pygame.mixer.init()
Contra_Music = pygame.mixer.Sound("ContraMusic.mp3")

volume = 0.2
Contra_Music.set_volume(volume)

clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, images_left, images_right, jump_images_right, bullet_group, all_sprites, x ,y):
        pygame.sprite.Sprite.__init__(self)
        self.images_left = images_left
        self.images_right = images_right
        self.jump_image_right =  jump_images_right
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.bullet_group = bullet_group
        self.all_sprites = all_sprites
        self.current_frame = 0
        self.direction = "right"
        self.is_move = False
        self.acceleration = 0.2
        self.velocity = 0
        self.frame_delay = 0.1
        self.shoot_delay = 0.5
        self.last_shoot_time = pygame.time.get_ticks()
        self.max_health = 1000
        self.health = self.max_health
        self.is_dead = False


    def update(self):
        if self.is_dead:
            pygame.quit()
            sys.exit()

        self.apply_gravity()
        self.handle_input()
        self.move()
        self.animation()

        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True)
        for bullet in bullet_collisions:
            self.health -= 20

        if self.health <= 0:
            self.is_dead = True

    def apply_gravity(self):
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = 0.1

        if keys[pygame.K_LEFT]:
            self.direction = "left"
            self.rect.x -= speed
            self.is_move = True
        elif keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += speed
            self.is_move = True
        else:
            self.is_move = False

        if keys[pygame.K_SPACE]:
            self.shoot()
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if keys[pygame.K_UP] and self.rect.y >= HEIGHT - self.rect.height:
            self.jump()

    def jump(self):
        self.velocity = -6

    def move(self):
        keys = pygame.key.get_pressed()
        speed =  5

        if keys[pygame.K_LEFT]:
            self.direction == "left"
            self.rect.x -= speed
        elif keys[pygame.K_RIGHT]:
            self.direction == "right"
            self.rect.x += speed

    def animation(self):
        if not self.is_move:
            if self.direction == "left":
                self.image = self.images_left[0]
            else:
                self.image = self.images_right[0]
        else:
            if self.direction == 'left':
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_left):
                    self.current_frame = 0
                self.image = self.images_left[int(self.current_frame)]
            else:
                self.current_frame += self.frame_delay
                if int(self.current_frame) >= len(self.images_right):
                    self.current_frame = 0
                self.image = self.images_right[int(self.current_frame)]

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot_time >= self.shoot_delay * 1000:
            bullet = self.rect.centerx + 80 if self.direction == "right" else self.rect.centerx - 80
            bullet = Bullet(bullet , self.rect.centery, self.direction)
            self.bullet_group.add(bullet)
            self.all_sprites.add(bullet)
            self.last_shoot_time = current_time

    def draw_health_bar(self):
        bar_length = 80
        bar_height = 5
        fill_width = int((self.health / self.max_health) * bar_length)
        fill_color = (0, 255, 0)
        outline_color = (255, 255, 255)
        bar_x = self.rect.centerx - bar_length // 2
        bar_y = self.rect.top - 20
        pygame.draw.rect(screen, outline_color, (bar_x, bar_y, bar_length, bar_height))
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, bullet_group, all_sprites):
        super().__init__()
        self.images_left = [pygame.image.load("./graphics/enemies/standard/left/" + str(i) + ".png") for i in range(3)]
        self.images_right = [pygame.image.load("./graphics/enemies/standard/right/" + str(i) + ".png") for i in range(3)]
        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = player
        self.bullet_group = bullet_group
        self.all_sprites = all_sprites
        self.current_frame = 0
        self.direction = "right"
        self.is_dead = False
        self.acceleration = 0.2
        self.velocity = 0
        self.shoot_timer = random.randint(100, 300)
        self.max_health = 100
        self.health = self.max_health
        self.health_bar_color = (255, 0, 0)
        self.health_bar_width = 80
        self.health_bar_height = 5

    def update(self):
        if not self.is_dead:
            self.apply_gravity()
            self.follow_player()
            self.move()
            self.shoot_timer -= 15

            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = random.randint(100, 300)

        bullet_collisions = pygame.sprite.spritecollide(self, self.bullet_group, True)
        for bullet in bullet_collisions:
            self.health -= 20
            if self.health <= 0:
                self.is_dead = True
                self.respawn()

        if self.direction == "left":
            self.image = self.images_left[self.current_frame]
        elif self.direction == "right":
            self.image = self.images_right[self.current_frame]

        self.animation_movement()

    def respawn(self):
        global score
        self.health = self.max_health
        self.is_dead = False
        self.current_frame = 0
        self.image = self.images_right[0]
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        score += 1

    def apply_gravity(self):
        self.velocity += self.acceleration
        self.rect.y += self.velocity

        if self.rect.y >= HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity = 0

    def follow_player(self):
        MAX_DISTANCE = WIDTH // 2
        if self.player is not None:
            if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
                self.direction = "right" if self.rect.x <= 0 else "left"

            if self.direction == "left":
                self.rect.x -= 2
            elif self.direction == "right":
                self.rect.x += 2

            if abs(self.player.rect.x - self.rect.x) >= MAX_DISTANCE:
                self.direction = "right" if self.player.rect.x > self.rect.x else "left"

    def move(self):
        if self.direction == "left":
            self.rect.x -= 2
        elif self.direction == "right":
            self.rect.x += 2

    def shoot(self):
        bullet_direction = "left" if self.direction == 'left' else "right"
        if bullet_direction == "right":
            bullet_x = self.rect.centerx + 80
            self.image = self.images_right[0]
        else:
            bullet_x = self.rect.centerx - 80
            self.image = self.images_left[0]
        bullet = Bullet(bullet_x, self.rect.centery, bullet_direction)
        self.bullet_group.add(bullet)
        self.all_sprites.add(bullet)

    def animation_movement(self):
        if not self.is_dead:
            if self.direction == "left":
                self.current_frame = (self.current_frame + 1) % len(self.images_left)
                self.image = self.images_left[self.current_frame]
            elif self.direction == "right":
                self.current_frame = (self.current_frame + 1) % len(self.images_right)
                self.image = self.images_right[self.current_frame]

    def draw_health_bar(self):
        pygame.draw.rect(screen, self.health_bar_color, (self.rect.x, self.rect.y - 10, self.health_bar_width, self.health_bar_height))
        health_percentage = self.health / self.max_health
        health_bar_fill = health_percentage * self.health_bar_width
        pygame.draw.rect(screen, (0, 255, 0 ) , (self.rect.x, self.rect.y - 10, health_bar_fill, self.health_bar_height))

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render("Score: " + str(score), True, (255,255,255))
        screen.blit(score_text,(10,10))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.images = [pygame.image.load("./graphics/bullet.png")]
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.direction = direction

    def update(self):
        if self.direction == "up":
            self.rect.y -= 5
        elif self.direction == "down":
            self.rect.y += 5
        elif self.direction == "left":
            self.rect.x -= 5
        elif self.direction == "right":
            self.rect.x += 5

        if self.rect.top < 0 or self.rect.bottom > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()
        self.animation()

    def animation(self):
        self.current_frame = (self.current_frame + 1) % len(self.images)
        self.image = self.images[self.current_frame]

all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()


def main():
    player_images_left = [pygame.image.load(f"./graphics/player/left/{i}.png") for i in range(8)]
    player_images_right = [pygame.image.load(f"./graphics/player/right/{i}.png") for i in range(8)]
    player_jump_images_right = [pygame.image.load(f"./graphics/player/right_jump/0.png")]

    x = WIDTH // 2
    y = HEIGHT // 2

    player = Player(player_images_left, player_images_right, player_jump_images_right, bullet_group, all_sprites, x, y)
    all_sprites.add(player)

    enemy = Enemy(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), player, bullet_group, all_sprites)
    enemy.health_bar_color = (255, 0, 0)
    all_sprites.add(enemy)
    enemy_group.add(enemy)

    background_image = pygame.image.load("./graphics/City2.png").convert()
    background_image = pygame.transform.scale(background_image , (WIDTH, HEIGHT))   

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        Contra_Music.play()
        all_sprites.update()
        screen.blit(background_image, (0, 0))
        player.draw_health_bar()
        enemy.draw_health_bar()
        all_sprites.draw(screen)
        enemy.draw_score()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()