import pygame, math, os, random

WINDOW_SIZE = (960, 540)
SURFACE_SIZE = (240, 135)

clock = pygame.time.Clock()

class Car:
	# this code stolen from https://rmgi.blog/pygame-2d-car-tutorial.html

	pos = pygame.math.Vector2(32, 32)
	velocity = pygame.math.Vector2(0, 0)
	speed = 50
	angle = 0
	length = 6
	steering = 0

	def __init__(self):
		# load image, rotated 270 to face right direction
		self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./assets/car.png"), (9, 12)), 270) # the actual sprite is 6 x 8
		self.rect = self.image.get_rect(topleft = self.pos)

	def update(self):
		dt = clock.get_time() / 1000

		# velocity for car, accounting 4 rotation
		if self.steering:
			turningRadius = self.length / math.sin(math.radians(self.steering))
			angularVelocity = self.velocity.x / turningRadius
		else:
			angularVelocity = 0
		
		self.pos += self.velocity.rotate(-self.angle) * dt
		self.angle += math.degrees(angularVelocity) * dt
		self.rect = self.image.get_rect(topleft = self.pos)

		# input
		keys = pygame.key.get_pressed()
		
		if keys[pygame.K_z]:
			self.velocity.x = self.speed
		elif keys[pygame.K_x]:
			self.velocity.x = -self.speed / 2
		else:
			self.velocity.x = 0

		if keys[pygame.K_LEFT]:
			self.steering = 20
		elif keys[pygame.K_RIGHT]:
			self.steering = -20
		else:
			self.steering = 0

	def draw(self, surface):
		# draw rotated sprite
		surface.blit(pygame.transform.rotate(self.image, self.angle), self.pos)

class Enemy():
	frames = 0
	dead = False

	def __init__(self, pos = (96, 96)):
		# load image, rotated 270 to face right direction
		self.image = pygame.transform.scale(pygame.image.load("./assets/guy.png"), (5, 8))
		self.blood = pygame.image.load("./assets/blood.png")
		self.pos = pygame.math.Vector2(pos)
		self.rect = self.image.get_rect(topleft = self.pos)

		self.angle = random.randint(0, 360)
	
	def update(self):
		if not self.dead:
			# timer based stuff
			if self.frames % 4 == 0:
				# animation
				self.image = pygame.transform.flip(self.image, True, False)
			if self.frames % (60 * 3) == 0:
				# changing angles after 3 seconds
				self.angle = random.randint(0, 360)
			
			self.pos += pygame.math.Vector2(0.2, 0).rotate(-self.angle)
			self.rect = self.image.get_rect(topleft = self.pos)

			# more changing angles stuff in case guy hits edge
			if self.pos.y <= 0 or self.pos.y + self.rect.h >= SURFACE_SIZE[1]:
				self.angle = random.randint(0, 360)
			
			if self.pos.x <= 0 or self.pos.x + self.rect.w >= SURFACE_SIZE[0]:
				self.angle = random.randint(0, 360)

		self.frames += 1

	def draw(self, surface):
		if self.dead:
			surface.blit(self.blood, (self.pos.x - 3, self.pos.y - 2))
		surface.blit(self.image, self.pos)

class Game:
	surface = pygame.surface.Surface(SURFACE_SIZE)
	window  = pygame.display.set_mode(WINDOW_SIZE)
	active  = True
	counter = 0
	score   = 0

	pygame.display.set_caption("death race 76")

	def __init__(self):
		pygame.mixer.pre_init(44100, 16, 2, 4096)
		pygame.init()

		self.car = Car()
		#self.enemy = Enemy()
		self.enemies = [Enemy(), Enemy((64, 64))]

		pygame.mixer.music.load("./assets/music/" + random.choice(os.listdir("./assets/music/")))
		pygame.mixer.music.play()
	
	def __del__(self):
		pygame.quit()
	
	def add_enemy(self):
		while True:
			posx = random.randint(0, SURFACE_SIZE[0] - 5)
			posy = random.randint(0, SURFACE_SIZE[1] - 7)

			if pygame.Rect.colliderect(self.car.rect, pygame.Rect(posx, posy, 5, 7)):
				continue
			
			for enemy in self.enemies:
				if pygame.Rect.colliderect(enemy.rect, pygame.Rect(posx, posy, 5, 7)):
					continue

			break

		self.enemies.append(Enemy((posx, posy)))

	def update(self):
		eventList = pygame.event.get()

		for event in eventList:
			if event.type == pygame.QUIT:
				self.active = False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.active = False
				
				if event.key == pygame.K_m:
					pygame.mixer.music.set_volume(0)
		
		if self.counter < (60 * 60):
			self.car.update()
			for enemy in self.enemies:
				enemy.update()

			for enemy in self.enemies:
				if pygame.Rect.colliderect(self.car.rect, enemy.rect):
					if not enemy.dead:
						enemy.dead = True

						if self.car.velocity.x >= 0:
							self.score += 1
						else:
							self.score += 2
						
						print("score: " + str(self.score))
						self.add_enemy()
					else:
						self.car.speed = 15
					break
				else:
					self.car.speed = 50
		else:
			print("game over! you got " + str(self.score) + " points!")

		self.counter += 1
				
	
	def draw(self):
		self.surface.fill((0, 0, 0))
		for enemy in self.enemies:
			enemy.draw(self.surface)
		self.car.draw(self.surface)

		self.window.blit(pygame.transform.scale(self.surface, WINDOW_SIZE), (0, 0))
		pygame.display.flip()
	
	def main(self):
		while self.active:
			self.update()
			self.draw()

			clock.tick(60)

game = Game()
game.main()
del game