import pygame
import random
import time
from bike_physics import Bike
from controller import CVController

pygame.init()

# GAME SETTINGS
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("AirBike")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

ROAD_LEFT = 200
ROAD_RIGHT = WIDTH - 200

spawn_distance = 0
SPAWN_GAP = 350

# PLAYER 
bike_x = WIDTH // 2
bike_y = 600
bike_width, bike_height = 30, 70
STEER_SPEED = 350

bike = Bike()
controller = CVController()

# TRAFFIC
cars = []

def spawn_car():
    x = random.randint(ROAD_LEFT + 60, ROAD_RIGHT - 60)
    y = -120
    scale = 0.4
    cars.append([x, y, scale])

spawn_car()

def check_collision():
    for x, y, scale in cars:
        car_w = int(50 * scale)
        car_h = int(90 * scale)

        if abs(x - bike_x) < (car_w/2 + 15) and abs(y - bike_y) < car_h:
            return True
    return False

# GAME LOOP 
running = True

while running:
    dt = clock.tick(60) / 1000

    # INPUT 
    cv_gas, cv_brake, lane_name = controller.update()

    keys = pygame.key.get_pressed()
    kb_gas = keys[pygame.K_RIGHT]
    kb_brake = keys[pygame.K_LEFT]

    gas = cv_gas or kb_gas
    brake = cv_brake or kb_brake

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # CONTINUOUS STEERING 
    if lane_name == "LEFT":
        bike_x -= STEER_SPEED * dt
    elif lane_name == "RIGHT":
        bike_x += STEER_SPEED * dt

    bike_x = max(ROAD_LEFT + 20, min(bike_x, ROAD_RIGHT - 20))

    # PHYSICS 
    bike.update(gas, brake, "CENTER", dt)

    # SPAWN TRAFFIC 
    spawn_distance += bike.speed * 20 * dt
    if spawn_distance > SPAWN_GAP:
        spawn_car()
        spawn_distance = 0

    # MOVE CARS (Perspective)
    for car in cars:
        car[1] += bike.speed * 20 * dt
        car[2] += 0.25 * dt

    # remove offscreen cars
    cars[:] = [car for car in cars if car[1] < HEIGHT + 150]

    # COLLISION 
    if check_collision():
        running = False

    # DRAW
    screen.fill((30,30,30))

    # road
    pygame.draw.rect(screen,(60,60,60),(ROAD_LEFT,0,ROAD_RIGHT-ROAD_LEFT,HEIGHT))

    # center road line
    pygame.draw.line(screen,(255,255,255),(WIDTH//2,0),(WIDTH//2,HEIGHT),3)

    # draw cars
    for x, y, scale in cars:
        w = int(50 * scale)
        h = int(90 * scale)
        pygame.draw.rect(screen,(255,50,50),(x - w//2, y, w, h))

    # draw bike
    pygame.draw.rect(screen,(0,200,255),(bike_x-15,bike_y,bike_width,bike_height))

    # HUD
    speed_text = font.render(f"Speed: {int(bike.speed)}", True, (255,255,255))
    score_text = font.render(f"Score: {bike.get_score()}", True, (255,255,255))
    screen.blit(speed_text,(20,20))
    screen.blit(score_text,(20,60))

    pygame.display.update()

pygame.quit()
print("GAME OVER")
print("Final Score:", bike.get_score())
