import pygame, math, os, random, eyed3, shelve, time

WINDOW_SIZE = (512, 384)
SURFACE_SIZE = (256, 192)
GAME_SIZE = (248, 152)

saveFile = shelve.open("savegame")
tmpSave = saveFile

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

		self.hum = pygame.mixer.Sound.play(pygame.mixer.Sound("./assets/sfx/car.wav"), loops = -1)

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
		if self.velocity.x != 0:
			self.hum.set_volume(1.0)
		else:
			self.hum.set_volume(0)

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
			surface.blit(self.blood, (self.pos.x - 3, self.pos.y - 2))
		surface.blit(self.image, self.pos)

class Arcade:
	counter = (60 * 60)
	score   = 0

	def __init__(self):
		self.car = Car()
		#self.enemy = Enemy()
		self.enemies = [Enemy(), Enemy((64, 64))]

		self.font = pygame.font.Font("./assets/m5x7.ttf", 24)

		self.scoreText = self.font.render(str(self.score), True, (255, 255, 255))
		self.timerText = self.font.render(str(self.counter), True, (255, 255, 255))
	
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
		if self.counter >= 0:
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
				self.car.speed = 50
			
			self.scoreText = self.font.render(str(self.score), True, (255, 255, 255))
			self.timerText = self.font.render(str(int(self.counter / 60)), True, (255, 255, 255))
		else:
			if self.counter > -(60 * 5):
				if self.score > tmpSave["highScore"]:
					tmpSave["highScore"] = self.score

			else:
				return "destroy"
		
		self.counter -= 1
	
	def draw(self, surface):
		pygame.draw.rect(surface, (255, 255, 255), (4, 4, GAME_SIZE[0], GAME_SIZE[1]), 1)
		
		for enemy in self.enemies:
			enemy.draw(surface)
		self.car.draw(surface)

		surface.blit(self.timerText, (8, ((SURFACE_SIZE[1] - (GAME_SIZE[1] + 4)) / 2) + (GAME_SIZE[1] + 4) - (self.timerText.get_rect().h / 2)))
		surface.blit(self.scoreText, ((SURFACE_SIZE[0] - 8 - self.scoreText.get_rect().w, ((SURFACE_SIZE[1] - (GAME_SIZE[1] + 4)) / 2) + (GAME_SIZE[1] + 4) - (self.timerText.get_rect().h / 2))))

class Menu:
	def __init__(self):
		self.font = pygame.font.Font("./assets/m5x7.ttf", 16)
		self.logo = pygame.image.load("./assets/logo.png")

		if "highScore" not in tmpSave:
			tmpSave["highScore"] = 0
	
	def update(self, eventList):
		for event in eventList:
			if event.type == pygame.KEYDOWN:
				return "arcade"
		
		#self.testString = self.font.render(f"HIGH SCORE: {tmpSave['highScore']}", True, (255, 255, 255))
		self.enterString = self.font.render("press any key to start", True, (255, 255, 255))
	
	def draw(self, surface):
		#surface.blit(self.testString, ((SURFACE_SIZE[0] / 2) - (self.testString.get_rect().w / 2), 24))
		surface.blit(self.logo, ((SURFACE_SIZE[0] / 2) - (self.logo.get_rect().w / 2), (SURFACE_SIZE[1] / 3) - (self.logo.get_rect().h / 2)))
		surface.blit(self.enterString, ((SURFACE_SIZE[0] / 2) - (self.enterString.get_rect().w / 2), (SURFACE_SIZE[1] / 3) + (SURFACE_SIZE[1] / 3) - (self.enterString.get_rect().h / 2)))

class Game:
	surface = pygame.surface.Surface(SURFACE_SIZE)
	window  = pygame.display.set_mode(WINDOW_SIZE)
	active  = True
	muted   = False
	
	musicTextAlpha = 0

	pygame.display.set_caption("death race 76")

	def __init__(self):
		pygame.mixer.pre_init(44100, 16, 2, 4096)
		pygame.init()
		self.splash()

		self.musicFont = pygame.font.Font("./assets/m5x7.ttf", 12)

		self.song = "./assets/music/" + random.choice(os.listdir("./assets/music/"))
		songMetadata = eyed3.load(self.song)

		pygame.mixer.music.load(self.song)
		pygame.mixer.music.play()
		pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

		self.musicText = self.musicFont.render(f"Now playing: {songMetadata.tag.artist} - {songMetadata.tag.title}", True, (255, 255, 255))
		self.musicTextSurface = pygame.Surface((self.musicText.get_rect().w, self.musicText.get_rect().h))
		self.musicTextSurface.blit(self.musicText, (0, 0))
		self.musicTextAlpha = 255

		self.hierarchy = [Menu()]
	
	def __del__(self):
		for i in tmpSave:
			saveFile[i] = tmpSave[i]
		saveFile.close()
		pygame.quit()

	def splash(self):
		self.surface.fill((0, 0, 0))
		self.surface.blit(pygame.image.load("./assets/splash.png"), (0, 0))
		self.window.blit(pygame.transform.scale(self.surface, WINDOW_SIZE), (0, 0))
		pygame.display.flip()

		time.sleep(1)
	
	def update(self):
		eventList = pygame.event.get()

		for event in eventList:
			if event.type == pygame.QUIT:
				self.active = False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.active = False
				
				if event.key == pygame.K_m:
					if self.muted:
						pygame.mixer.music.set_volume(127)
						self.muted = False
					else:
						pygame.mixer.music.set_volume(0)
						self.muted = True
		
			if event.type == pygame.USEREVENT + 1:
				while True:
					tmpSong = "./assets/music/" + random.choice(os.listdir("./assets/music/"))
					if tmpSong != self.song:
						self.song = tmpSong
						break
				songMetadata = eyed3.load(self.song)

				pygame.mixer.music.load(self.song)
				pygame.mixer.music.play()

				self.musicText = self.musicFont.render(f"Now playing: {songMetadata.tag.artist} - {songMetadata.tag.title}", True, (255, 255, 255))
				self.musicTextSurface = pygame.Surface((self.musicText.get_rect().w, self.musicText.get_rect().h))
				self.musicTextSurface.blit(self.musicText, (0, 0))
				self.musicTextAlpha = 255
		
		response = self.hierarchy[-1].update(eventList)

		if response == "arcade":
			self.hierarchy.append(Arcade())
		if response == "destroy":
			self.hierarchy.pop(-1)
		
		if self.musicTextAlpha >= 0:
			self.musicTextSurface.set_alpha(self.musicTextAlpha)
			self.musicTextAlpha -= 1
	
	def draw(self):
		self.surface.fill((0, 0, 0))

		self.hierarchy[-1].draw(self.surface)
		self.surface.blit(self.musicTextSurface, (SURFACE_SIZE[0] - self.musicText.get_rect().w - 8, 8))

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