import time

class Bike:
    def __init__(self):
        # physics constants
        self.speed = 0.0
        self.max_speed = 25.0
        self.acceleration = 8.0      # units/sec^2
        self.brake_force = 12.0
        self.friction = 4.0

        # scoring
        self.distance = 0.0
        self.start_time = time.time()

        # lane system
        self.lane = "CENTER"

    def update(self, gas, brake, lane, dt):
        # lane update
        self.lane = lane

        # acceleration
        if gas:
            self.speed += self.acceleration * dt

        # braking
        if brake:
            self.speed -= self.brake_force * dt

        # friction (always applies)
        self.speed -= self.friction * dt

        # clamp speed
        self.speed = max(0, min(self.speed, self.max_speed))

        # update distance
        self.distance += self.speed * dt

    def get_score(self):
        time_elapsed = time.time() - self.start_time
        avg_speed = self.distance / max(time_elapsed, 1)
        return int(self.distance * avg_speed)

    def debug_print(self):
        print(
            f"Speed: {self.speed:.2f} | "
            f"Distance: {self.distance:.2f} | "
            f"Lane: {self.lane} | "
            f"Score: {self.get_score()}",
            end="\r"
        )


# TEST LOOP 
if __name__ == "__main__":
    bike = Bike()
    last_time = time.time()

    print("Testing physics... Press Ctrl+C to stop")

    try:
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            # TEMP TEST INPUTS (we replace with CV later)
            gas = True
            brake = False
            lane = "CENTER"

            bike.update(gas, brake, lane, dt)
            bike.debug_print()

            time.sleep(0.016)  # ~60 FPS

    except KeyboardInterrupt:
        print("\nTest ended")
