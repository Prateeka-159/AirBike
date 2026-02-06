import pygame
import random
import time
from bike_physics import Bike
from controller import CVController

pygame.init()

spawn_distance = 0
SPAWN_GAP = 350   # vertical gap between traffic waves

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AirBike")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# lanes (x positions)
LANES = [150, 300, 450]

# player
bike_x = LANES[1]
bike_y = 650
bike_width, bike_height = 60, 100
current_lane = 1

# traffic cars
cars = []
CAR_WIDTH, CAR_HEIGHT = 60, 100
spawn_timer = 0

bike = Bike()
controller = CVController()

def spawn_car():
    safe_lane = random.randint(0, 2)
    lanes_to_spawn = [0, 1, 2]
    lanes_to_spawn.remove(safe_lane)

    # decide spawn pattern
    spawn_type = random.choice(["one", "two"])

    if spawn_type == "one":
        lane = random.choice(lanes_to_spawn)
        cars.append([lane, LANES[lane], -120])

    if spawn_type == "two":
        for lane in lanes_to_spawn:
            cars.append([lane, LANES[lane], -120])

spawn_car()   # spawn first traffic wave

def check_collision():
    for lane, x, y in cars:
        if lane == current_lane and abs(y - bike_y) < 80:
            return True
    return False

running = True
last_time = time.time()

while running:
    dt = clock.tick(60) / 1000
    now = time.time()

    # INPUT (CV + KEYBOARD HYBRID)

    # 1) Read CV controller once per frame
    cv_gas, cv_brake, lane_name = controller.update()

    # 2) Read keyboard (fallback)
    keys = pygame.key.get_pressed()
    kb_gas = keys[pygame.K_RIGHT]
    kb_brake = keys[pygame.K_LEFT]

    # 3) Combine inputs
    gas = cv_gas or kb_gas
    brake = cv_brake or kb_brake

    # 4) Lane change from CV (edge-triggered)
    if lane_name == "LEFT" and current_lane > 0:
        current_lane -= 1
    elif lane_name == "RIGHT" and current_lane < 2:
        current_lane += 1

    # 5) Event loop only for quitting + optional keyboard lane backup
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and current_lane > 0:
                current_lane -= 1
            if event.key == pygame.K_d and current_lane < 2:
                current_lane += 1

    # smooth lane movement
    target_x = LANES[current_lane]
    bike_x += (target_x - bike_x) * 0.15

    # PHYSICS 
    bike.update(gas, brake, ["LEFT","CENTER","RIGHT"][current_lane], dt)

    # WAVE SPAWN SYSTEM 
    spawn_distance += bike.speed * 20 * dt

    if spawn_distance > SPAWN_GAP:
        spawn_car()
        spawn_distance = 0

    # move cars
    for car in cars:
        car[2] += bike.speed * 20 * dt

    cars[:] = [car for car in cars if car[2] < HEIGHT + 100]

    # collision
    if check_collision():
        running = False

    # DRAW
    screen.fill((30,30,30))

    # road
    pygame.draw.rect(screen, (60,60,60), (100,0,400,HEIGHT))

    # lane lines
    pygame.draw.line(screen,(255,255,255),(250,0),(250,HEIGHT),3)
    pygame.draw.line(screen,(255,255,255),(350,0),(350,HEIGHT),3)

    # draw bike
    pygame.draw.rect(screen,(0,200,255),(bike_x-30,bike_y,bike_width,bike_height))

    # draw cars
    for lane, x, y in cars:
        pygame.draw.rect(screen,(255,50,50),(x-30,y,CAR_WIDTH,CAR_HEIGHT))

    # HUD
    speed_text = font.render(f"Speed: {int(bike.speed)}", True, (255,255,255))
    score_text = font.render(f"Score: {bike.get_score()}", True, (255,255,255))

    screen.blit(speed_text,(10,10))
    screen.blit(score_text,(10,40))

    pygame.display.update()

pygame.quit()
print("GAME OVER")
print("Final Score:", bike.get_score())
