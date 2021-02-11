import pygame, math, os, random, shelve

WINDOW_SIZE = (512, 384)
SURFACE_SIZE = (256, 192)
GAME_SIZE = (248, 152)

saveFile = shelve.open(".save")
hierarchy = []

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

		#self.hum = pygame.mixer.Sound.play(pygame.mixer.Sound("./assets/sfx/car.wav"), loops = -1)

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
		
		# collision
		if self.pos.y <= 4 or self.pos.y + self.rect.h >= GAME_SIZE[1] + 4:
			self.pos.y = (4 if self.pos.y <= 4 else GAME_SIZE[1] - self.rect.h + 3)
		
		if self.pos.x <= 4 or self.pos.x + self.rect.w >= GAME_SIZE[0] + 4:
			self.pos.x = (4 if self.pos.x <= 4 else GAME_SIZE[0] - self.rect.w + 3)

		# volume
		""" if self.velocity.x != 0:
			self.hum.set_volume(1.0)
		else:
			self.hum.set_volume(0) """

	def draw(self, surface):
		# draw rotated sprite
		surface.blit(pygame.transform.rotate(self.image, self.angle), self.pos)

class Enemy():
	frames = 0
	dead = False

	def __init__(self, pos = (96, 96)):
		# load image, rotated 270 to face right direction
		self.image = pygame.transform.scale(pygame.image.load("./assets/guy.png"), (5, 8))
		self.cross = pygame.image.load("./assets/cross.png")
		self.pos = pygame.math.Vector2(pos)
		self.rect = self.image.get_rect(topleft = self.pos)

		self.angle = random.randint(0, 360)
		self.scream = pygame.mixer.Sound("./assets/sfx/death.wav")
	
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
			if self.pos.y <= 4 or self.pos.y + self.rect.h >= GAME_SIZE[1] + 4:
				self.angle = random.randint(0, 360)
				self.pos.y = (5 if self.pos.y <= 4 else GAME_SIZE[1] - self.rect.h + 3)
			
			if self.pos.x <= 4 or self.pos.x + self.rect.w >= GAME_SIZE[0] + 4:
				self.angle = random.randint(0, 360)
				self.pos.x = (5 if self.pos.x <= 4 else GAME_SIZE[0] - self.rect.w + 3)

		self.frames += 1

	def draw(self, surface):
		if self.dead:
			surface.blit(self.cross, self.pos)
		else:
			surface.blit(self.image, self.pos)

class Arcade:
	counter = (60 * 63)
	score   = 0
	remove  = False

	def __init__(self):
		self.car = Car()
		#self.enemy = Enemy()
		self.enemies = [Enemy(), Enemy((64, 64))]

		self.font = pygame.font.Font("./assets/m5x7.ttf", 24)

		self.scoreText = self.font.render(str(self.score), True, (255, 255, 255))
		self.timerText = self.font.render(str(int(self.counter / 60)), True, (255, 255, 255))
	
	def add_enemy(self):
		while True:
			posx = random.randint(4, GAME_SIZE[0] - 1)
			posy = random.randint(4, GAME_SIZE[1] - 3)

			if pygame.Rect.colliderect(self.car.rect, pygame.Rect(posx, posy, 5, 7)):
				continue
			
			for enemy in self.enemies:
				if pygame.Rect.colliderect(enemy.rect, pygame.Rect(posx, posy, 5, 7)):
					continue
			break

		self.enemies.append(Enemy((posx, posy)))

	def update(self, eventList):
		if self.counter >= 0 and self.counter <= (60 * 60):
			self.car.update()
			for enemy in self.enemies:
				enemy.update()

			if any(pygame.Rect.colliderect(self.car.rect, enemy.rect) for enemy in self.enemies):
				self.car.speed = 15

				for enemy in self.enemies:
					if pygame.Rect.colliderect(self.car.rect, enemy.rect):
						if not enemy.dead:
							enemy.dead = True
							pygame.mixer.Sound.play(enemy.scream)

							if self.car.velocity.x >= 0:
								self.score += 1
							else:
								self.score += 2
							
							self.add_enemy()
			else:
				if not self.counter > (60 * 60):
					self.car.speed = 50
			
			self.scoreText = self.font.render(str(self.score), True, (255, 255, 255))
			self.timerText = self.font.render(str(int(self.counter / 60)), True, (255, 255, 255))
		else:
			if self.counter > -(60 * 5):
				if self.score > saveFile["highScore"]:
					saveFile["highScore"] = self.score

			else:
				self.remove = True
		
		self.counter -= 1
	
	def draw(self, surface):
		pygame.draw.rect(surface, (255, 255, 255), (4, 4, GAME_SIZE[0], GAME_SIZE[1]), 1)
		
		for enemy in self.enemies:
			enemy.draw(surface)
		self.car.draw(surface)

		surface.blit(self.timerText, (8, ((SURFACE_SIZE[1] - (GAME_SIZE[1] + 4)) / 2) + (GAME_SIZE[1] + 4) - (self.timerText.get_rect().h / 2)))
		surface.blit(self.scoreText, ((SURFACE_SIZE[0] - 8 - self.scoreText.get_rect().w, ((SURFACE_SIZE[1] - (GAME_SIZE[1] + 4)) / 2) + (GAME_SIZE[1] + 4) - (self.timerText.get_rect().h / 2))))

class Menu:
	counter = 0
	remove  = False

	def __init__(self):
		self.font = pygame.font.Font("./assets/m5x7.ttf", 12)
		self.logo = pygame.image.load("./assets/logo.png")
		#self.bg   = pygame.image.load("./assets/bg.png")

		if "highScore" not in saveFile:
			saveFile["highScore"] = 0
	
	def update(self, eventList):
		for event in eventList:
			if event.type == pygame.KEYDOWN:
				hierarchy.append(Arcade())
		
		#self.testString = self.font.render(f"HIGH SCORE: {tmpSave['highScore']}", True, (255, 255, 255))
		if int(self.counter / 30) % 2 == 0:
			self.enterStringTxt = self.font.render("press any key to start", True, (255, 255, 255))
			self.enterString = pygame.Surface((self.enterStringTxt.get_rect().w + 8, self.enterStringTxt.get_rect().h + 8))
			self.enterString.blit(self.enterStringTxt, (4, 4))
		else:
			self.enterString = self.font.render("", True, (255, 255, 255))

		self.counter += 1
	
	def draw(self, surface):
		#surface.blit(self.bg, (0, 0))

		surface.blit(self.logo, ((SURFACE_SIZE[0] / 2) - (self.logo.get_rect().w / 2), (SURFACE_SIZE[1] / 2) - (self.logo.get_rect().h / 2)))
		surface.blit(self.enterString, ((SURFACE_SIZE[0] / 2) - (self.enterString.get_rect().w / 2), (SURFACE_SIZE[1] / 2) - (self.enterString.get_rect().h / 2)))

class Game:
	surface = pygame.surface.Surface(SURFACE_SIZE)
	window  = pygame.display.set_mode(WINDOW_SIZE)
	active  = True

	fadeOpacity = 0
	fadeTimer   = 0
	
	pygame.display.set_caption("death race 76")

	def __init__(self):
		pygame.mixer.pre_init(44100, 16, 2, 4096)
		pygame.init()

		if len(hierarchy) < 1:
			hierarchy.append(Menu())
	
	def __del__(self):
		saveFile.close()
		pygame.quit()
	
	def update(self):
		eventList = pygame.event.get()

		for event in eventList:
			if event.type == pygame.QUIT:
				self.active = False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.active = False
				
				if event.key == pygame.K_q:
					self.fadeTimer = (60 * 3)
			
		# TODO: fade timer
		
		hierarchy[-1].update(eventList)
		if hierarchy[-1].remove:
			hierarchy.pop(-1)
	
	def draw(self):
		self.surface.fill((0, 0, 0))

		hierarchy[-1].draw(self.surface)

		fade = pygame.surface.Surface(SURFACE_SIZE)
		fade.fill((0, 0, 0))
		fade.set_alpha(self.fadeOpacity)
		self.surface.blit(fade, (0, 0))

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