import pygame
from copy import deepcopy
from random import choice, randrange

# largeur, hauteur nb de carreau en longeur et hauteur
WIDTH, HEIGHT = 10, 20
# carreau 
TILE = 45
# Resolution ecran
RES = 750, 940
# Resolution de la grille
GAME_RES = WIDTH * TILE, HEIGHT * TILE
FPS = 60

pygame.init()
# initialisation de l'ecran
screen = pygame.display.set_mode(RES)
# initialisation de la grille
game_screen = pygame.Surface(GAME_RES)
# initialisation de l'objet permettant de suivre le temps
clock = pygame.time.Clock()

# creation de la grille 
grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(WIDTH) for y in range(HEIGHT)]

# coordonnées des tetrominos
figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]


figures = [[pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

# background + resize
bg = pygame.image.load('asset/img/tetris-bg.jpg').convert()
bg = pygame.transform.scale(bg, RES)
bg2 = pygame.image.load('asset/img/bg2.jpg').convert()
bg2 = pygame.transform.scale(bg2, GAME_RES)

# texte
main_font = pygame.font.Font('asset/font/me123.ttf', 40)
font = pygame.font.Font('asset/font/me123.ttf', 25)
title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = main_font.render('score :', True, pygame.Color('green'))
title_record = main_font.render('record :', True, pygame.Color('blue'))

# tetrominos color
get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

# score
score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

# evite de sortir de la grille
def check_borders():
    if figure[i].x < 0 or figure[i].x > WIDTH - 1:
        return False
    elif figure[i].y > HEIGHT - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

# recupére le score enregistré
def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')

# enregistre le score
def set_record(record, score):
    save = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(save))


while True:
    # recupére le score enregistré
    record = get_record()
    
    dx, rotate = 0, False
    screen.blit(bg, (0, 0))
    # game_screen.fill(pygame.Color('black'))
    screen.blit(game_screen, (20, 20))
    game_screen.blit(bg2, (0, 0))

    # delais de disparition des lignes
    for i in range(lines):
        pygame.time.wait(200)

    # evenement des touches
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
                
    # x mouvement droite gauche
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # y mouvement haut: changement de position et bas: descente rapide
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break

    # disparition des lignes + augmentation de la vitesse
    line, lines = HEIGHT - 1, 0
    for row in range(HEIGHT - 1, -1, -1):
        count = 0
        for i in range(WIDTH):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < WIDTH:
            line -= 1
        else:
            anim_speed += 3
            lines += 1

    # score
    score += scores[lines]

    # rotation
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y

            if not check_borders():
                figure = deepcopy(figure_old)
                break
    # 
    [pygame.draw.rect(game_screen, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # tetrominos
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_screen, color, figure_rect)

    # 
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_screen, col, figure_rect)

    # tetrominos suivant
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(screen, next_color, figure_rect)

    # titles
    screen.blit(title_tetris, (485, 20))
    screen.blit(title_score, (535, 780))
    screen.blit(font.render(str(score), True, pygame.Color('red')), (550, 840))
    screen.blit(title_record, (525, 650))
    screen.blit(font.render(record, True, pygame.Color('gold')), (550, 710))

    # game over on reinitialise tout
    for i in range(WIDTH):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(WIDTH)]for i in range(HEIGHT)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_screen, get_color(), i_rect)
                screen.blit(game_screen, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
