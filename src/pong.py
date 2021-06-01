#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
import random
import time
import operator
import os


def sprite_load_scaled(path, scale):
    sprite = pygame.image.load(path)
    sprite = pygame.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
    return sprite


class Entity:

    def __init__(self, x, y, width, height, speed, sprite, parent):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.sprite = sprite
        self.parent = parent

    def update(self, delta):
        pass

    def render(self):
        self.parent.screen.blit(self.sprite, (self.get_center_x(), self.get_center_y()))

    def get_center_x(self):
        return self.x - self.width / 2

    def get_center_y(self):
        return self.y - self.height / 2

    def up_collision(self):
        if self.y - self.height / 2 <= 0:
            self.y = self.height / 2
            return True
        return False

    def down_collision(self):
        if self.y + self.height / 2 >= self.parent.DISPLAY_HEIGHT:
            self.y = self.parent.DISPLAY_HEIGHT - self.height / 2
            return True
        return False


class Racket(Entity):

    up = False
    down = False

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)

    def update(self, delta):
        if self.up and not self.up_collision():
            self.y -= self.speed * delta
        elif self.down and not self.down_collision():
            self.y += self.speed * delta

    def update_ia(self, delta):
        ball = self.parent.ball
        if ball.y < self.y and not self.up_collision():
            self.y -= self.speed * delta
        elif ball.y > self.y and not self.down_collision():
            self.y += self.speed * delta


class Ball(Entity):

    def __init__(self, x, y, width, height, speed, sprite, parent):
        Entity.__init__(self, x, y, width, height, speed, sprite, parent)
        self.racket_left = self.parent.racket_left
        self.racket_right = self.parent.racket_right
        self.x_speed = 0
        self.y_speed = 0

    def update(self, delta):
        self.x += self.x_speed * delta
        self.y += self.y_speed * delta
        self.collision()

    def collision(self):
        ball_rect = pygame.rect.Rect((self.get_center_x(), self.get_center_y(), self.width, self.height))
        racket_left_rect = pygame.rect.Rect((self.racket_left.get_center_x(), self.racket_left.get_center_y(), self.racket_left.width, self.racket_left.height))
        racket_right_rect = pygame.rect.Rect((self.racket_right.get_center_x(), self.racket_right.get_center_y(), self.racket_right.width, self.racket_right.height))
        angle_in_degrees = 0
        if ball_rect.colliderect(racket_left_rect):
            # print('left')
            angle_in_degrees = -45

            self.set_angle(math.radians(angle_in_degrees))
        elif ball_rect.colliderect(racket_right_rect):
            # print('right')
            angle_in_degrees = 135

            ball_y = self.get_center_y()
            racket_y = self.racket_right.get_center_y()
            racket_height = self.racket_right.height

            print('ball y: ', ball_y)
            print('raq y: ', racket_y)

            if ball_y < racket_y:
                print('menor')
            elif ball_y == racket_y:
                print('center')
            elif ball_y > racket_y:
                print('maior')

            self.set_angle(math.radians(angle_in_degrees))
        if self.up_collision() or self.down_collision():
            self.y_speed *= -1

    def generate(self):
        self.x_speed = 150
        return
        self.x = self.parent.DISPLAY_WIDTH / 2
        self.y = random.randint(self.height, self.parent.DISPLAY_HEIGHT - self.height)
        if random.randint(0, 1) == 0:
            self.set_angle(math.radians(random.randint(35, 125)))
        else:
            self.set_angle(math.radians(random.randint(-125, 35)))

    def set_angle(self, angle_in_radians):
        self.x_speed = self.speed * math.cos(angle_in_radians)
        self.y_speed = self.speed * math.sin(angle_in_radians)


class Pong:

    # constants
    BLACK = (0, 0, 0)
    DARK_GRAY = (50, 50, 50)
    WHITE = (255, 255, 255)
    SCALE = 8
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600

    STATE_PLAYING = 0
    STATE_MAIN_MENU = 1
    STATE_PAUSE_MENU = 2

    def __init__(self):
        # print(os.getcwd())
        pygame.init()
        icon = pygame.image.load('src/res/icon.png')
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        random.seed(time.time())

        # keys
        self.k_up = False
        self.k_down = False
        self.k_w = False
        self.k_s = False
        self.k_enter = False
        self.k_esc = False

        # sprites
        self.clean_color = self.DARK_GRAY
        self.sprite_scanline = pygame.image.load('src/res/sprite/scanline_overlay.png')
        self.sprite_tv_vignette = pygame.image.load('src/res/sprite/tv_vignette_overlay.png')
        self. sprite_num = []
        for i in range(10):
            self.sprite_num.append(sprite_load_scaled('src/res/sprite/sprite_num_' + str(i) + '.png', int(self.SCALE / 2)))
        self.sprite_net = sprite_load_scaled('src/res/sprite/net.png', self.SCALE)
        sprite_ball = sprite_load_scaled('src/res/sprite/ball.png', self.SCALE)
        sprite_racket = sprite_load_scaled('src/res/sprite/racket.png', self.SCALE)
        self.font_title = pygame.font.Font('src/res/font/bit5x3.ttf', 128)
        self.font = pygame.font.Font('src/res/font/bit5x3.ttf', 32)

        # objects
        self.racket_left = Racket(50, 300, 16, 64, 250, sprite_racket, self)
        self.racket_right = Racket(750, 300, 16, 64, 250, sprite_racket, self)
        self.ball = Ball(400, 300, 16, 16, 250, sprite_ball, self)

        # control
        self.running = False
        self.effects = True
        self.player = False
        self.state = self.STATE_MAIN_MENU
        self.menu_op = 0
        self.score_left = 0
        self.score_right = 0
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.elapsed = 0

    def run(self):
        self.running = True

        # main loop
        while self.running:
            self.delta = self.elapsed / 1000.0
            self.update()
            self.render()
            self.elapsed = self.clock.tick(60)

        pygame.quit()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.k_up = True
                elif event.key == pygame.K_DOWN:
                    self.k_down = True
                elif event.key == pygame.K_w:
                    self.k_w = True
                elif event.key == pygame.K_s:
                    self.k_s = True
                elif event.key == pygame.K_RETURN:
                    self.k_enter = True
                elif event.key == pygame.K_ESCAPE:
                    self.k_esc = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.k_up = False
                elif event.key == pygame.K_DOWN:
                    self.k_down = False
                elif event.key == pygame.K_w:
                    self.k_w = False
                elif event.key == pygame.K_s:
                    self.k_s = False
                elif event.key == pygame.K_RETURN:
                    self.k_enter = False
                elif event.key == pygame.K_ESCAPE:
                    self.k_esc = False

        if self.state == self.STATE_PLAYING:
            if self.k_esc:
                self.state = self.STATE_PAUSE_MENU
            # self.racket_left.up = self.k_w
            # self.racket_left.down = self.k_s
            # self.racket_left.update(self.delta)
            self.racket_left.update_ia(self.delta)
            self.racket_right.up = self.k_up
            self.racket_right.down = self.k_down
            self.racket_right.update(self.delta)
            self.ball.update(self.delta)
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU:
            if self.k_up or self.k_w:
                self.menu_op = 0
            elif self.k_down or self.k_s:
                self.menu_op = 1
            if self.k_enter:
                if self.menu_op == 0:
                    if self.state == self.STATE_MAIN_MENU:
                        self.start_match()
                    self.state = self.STATE_PLAYING
                else:
                    if self.state == self.STATE_MAIN_MENU:
                        self.running = False
                    else:
                        self.state = self.STATE_MAIN_MENU
                    self.menu_op = 0
                self.k_enter = False

    def render(self):
        self.screen.fill(self.clean_color)

        if self.state == self.STATE_PLAYING:
            self.draw_score()
            self.draw_net()
            self.draw_racket()
            self.draw_ball()
        elif self.state == self.STATE_MAIN_MENU or self.state == self.STATE_PAUSE_MENU:
            self.draw_menu()

        if self.effects:
            self.draw_overlay_effects()
        else:
            self.clean_color = self.BLACK

        pygame.display.flip()

    def start_match(self):
        self.racket_left.y = self.DISPLAY_HEIGHT / 2
        self.racket_right.y = self.DISPLAY_HEIGHT / 2
        self.ball.generate()

    def draw_score(self):
        x_left = 200
        x_right = 600
        top = 50
        half_width = 32
        self.screen.blit(self.sprite_num[self.score_left], (x_left - half_width, top))
        self.screen.blit(self.sprite_num[self.score_left], (x_right - half_width, top))
        pass

    def draw_net(self):
        y = 20
        for i in range(18):
            self.screen.blit(self.sprite_net, (self.DISPLAY_WIDTH / 2 - 4, y + i * 32))

    def draw_racket(self):
        self.racket_left.render()
        self.racket_right.render()

    def draw_ball(self):
        self.ball.render()

    def draw_menu(self):
        padding = (16, 8)
        adjust = (2, 1, 0, 0)
        if self.state == self.STATE_PAUSE_MENU:
            str1 = 'CONTINUE'
            str2 = 'BACK TO MAIN MENU'
            str3 = 'PAUSED'
        else:
            str1 = 'PLAY'
            str2 = 'EXIT'
            str3 = 'PONG'
        str1_size = self.font.size(str1) + padding
        str2_size = self.font.size(str2) + padding
        pos1 = (int(self.DISPLAY_WIDTH / 2 - str1_size[0] / 2),
                int(self.DISPLAY_HEIGHT / 2 - str1_size[1] / 2),
                str1_size[0],
                str1_size[1])
        pos2 = (int(self.DISPLAY_WIDTH / 2 - str2_size[0] / 2),
                int((self.DISPLAY_HEIGHT / 2 - str2_size[1] / 2) + str2_size[1] * 1.5),
                str2_size[0],
                str2_size[1])
        if self.menu_op == 0:
            str1_r = self.font.render(str1, False, self.BLACK)
            str2_r = self.font.render(str2, False, self.WHITE)
            pygame.draw.rect(self.screen, self.WHITE, pos1)
        else:
            str1_r = self.font.render(str1, False, self.WHITE)
            str2_r = self.font.render(str2, False, self.BLACK)
            pygame.draw.rect(self.screen, self.WHITE, pos2)
        pos1 = tuple(map(operator.add, pos1, adjust))
        pos2 = tuple(map(operator.add, pos2, adjust))
        title = self.font_title.render(str3, False, self.WHITE)
        title_w = title.get_width()
        self.screen.blit(title, (int(self.DISPLAY_WIDTH / 2 - title_w / 2), 96))
        self.screen.blit(str1_r, pos1)
        self.screen.blit(str2_r, pos2)

    def draw_overlay_effects(self):
        self.screen.blit(self.sprite_scanline, (0, 0))
        self.screen.blit(self.sprite_tv_vignette, (0, 0))
