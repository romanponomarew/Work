import pygame as pg
import sys

W = 900
H = 600

sc = pg.display.set_mode((W, H))
sc.fill((100, 150, 200))

# Load and set up graphics.
background_image = pg.image.load("airport_scheme2.png").convert()
# Set positions of graphics
background_position = [0, 0]
sc.blit(background_image, background_position)

dog_surf = pg.image.load('airplane4.png')
dog_surf = pg.transform.scale(dog_surf, (60, 60))
dog_rect = dog_surf.get_rect(
    bottomright=(W, H))
sc.blit(dog_surf, dog_rect)

dog_surf1 = pg.image.load('airplane4.png')
dog_surf1 = pg.transform.scale(dog_surf1, (60, 60))
dog_rect1 = dog_surf1.get_rect(
    bottomleft=(W -700, H - 170))

sc.blit(dog_surf1, dog_rect1)


pg.display.update()

while 1:
    for i in pg.event.get():
        if i.type == pg.QUIT:
            sys.exit()

    pg.time.delay(20)