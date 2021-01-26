# assets

# grass - https://latenighcoffe.itch.io/grass-and-plants-for-25d-or-topview-games
# car - https://brad-gilbertson.itch.io/16bit-race-car-set
# coin - https://havran.itch.io/coin-with-rune

# imports #

import pygame
# constants #

WINDOW_SIZE = (512, 512) # the size for the actual window
SURFACE_SIZE = (64, 64)  # the surface size (where everything will get drawn)

clock = pygame.time.Clock()

class Car():
	acceleration = 0
	speed = 1
	keyPress = [False, False, False, False] # left, right, up, down
	keyUp = [False, False, False, False] # left, right, up, down
	rotation = 0
	playerPos = [0, 0]

	def __init__(self):
		self.image = pygame.transform.scale(pygame.image.load('./assets/car.png'), (6, 8))
	
	def update(self, eventList):
		for event in eventList:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT or event.key == pygame.K_a:
					self.keyPress[0] = True
				if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					self.keyPress[1] = True
					self.playerPos[0] += 1
				if event.key == pygame.K_UP or event.key == pygame.K_w:
					self.keyPress[2] = True
					self.playerPos[1] += 1
				if event.key == pygame.K_DOWN or event.key == pygame.K_s:
					self.keyPress[3] = True
					self.playerPos[1] -= 1

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_a:
					self.keyPress[0] = False
					self.keyUp[0] = True
				if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					self.keyPress[1] = False
					self.keyUp[1] = True
				if event.key == pygame.K_UP or event.key == pygame.K_w:
					self.keyPress[2] = False
					self.keyUp[2] = True
				if event.key == pygame.K_DOWN or event.key == pygame.K_s:
					self.keyPress[3] = False
					self.keyUp[3] = True
		
		if any(self.keyPress) and not self.acceleration > 1:
			self.keyUp = [False for k in self.keyUp]
			
			if self.acceleration <= 0.8:
				self.acceleration += 0.2
			else:
				self.acceleration = 1
			
		else:
			if self.acceleration >= 0.2:
				self.acceleration -= 0.2
			else:
				self.acceleration = 0
		
		if (self.keyPress[0] != self.keyPress[1]) or (not any(self.keyPress) and (self.keyUp[0] or self.keyUp[1])):
			if self.keyPress[0] or self.keyUp[0]:
				self.rotation = 180

				if self.keyPress[2] or self.keyUp[2] or self.keyPress[3] or self.keyUp[3]:
					if self.keyPress[2] or self.keyUp[2]:
						self.rotation -= 45
						#self.position[1] -= (self.acceleration * self.speed)
						self.playerPos[1] += (self.acceleration * self.speed)

					if self.keyPress[3] or self.keyUp[3]:
						self.rotation += 45
						#self.position[1] += (self.acceleration * self.speed)
						self.playerPos[1] -= (self.acceleration * self.speed)

				#self.position[0] -= (self.acceleration * self.speed)
				self.playerPos[0] += (self.acceleration * self.speed)
			
			if self.keyPress[1] or self.keyUp[1]:
				self.rotation = 0

				if self.keyPress[2] or self.keyUp[2] or self.keyPress[3] or self.keyUp[3]:
					if self.keyPress[2] or self.keyUp[2]:
						self.rotation += 45
						#self.position[1] -= (self.acceleration * self.speed)
						self.playerPos[1] += (self.acceleration * self.speed)

					if self.keyPress[3] or self.keyUp[3]:
						self.rotation -= 45
						if not self.keyPress[0] or self.keyUp[0]:
							#self.position[1] += (self.acceleration * self.speed)
							self.playerPos[1] -= (self.acceleration * self.speed)

				#self.position[0] += (self.acceleration * self.speed)
				self.playerPos[0] -= (self.acceleration * self.speed)

		else:
			if self.keyPress[2] or self.keyUp[2]:
				self.playerPos[1] += (self.acceleration * self.speed)
				self.rotation = 90

			if self.keyPress[3] or self.keyUp[3]:
				self.playerPos[1] -= (self.acceleration * self.speed)
				self.rotation = 270
					
		#pygame.mixer.music.set_volume(float(self.energy / 100))

	def draw(self, surface):
		surface.blit(pygame.transform.rotate(self.image, self.rotation), self.playerPos)

# main #

class Game:
	# variables
	surface = pygame.surface.Surface(SURFACE_SIZE)
	window = pygame.display.set_mode(WINDOW_SIZE)
	pygame.display.set_caption("SPARKPLUG")
	#pygame.display.set_icon(pygame.image.load(os.getcwd() + "\\resources\\Icon.png"))

	def __init__(self):
		# initialising pygame and window
		#pygame.mixer.pre_init(44100, 16, 2, 4096)
		pygame.init()

		self.car = Car()
		
		#pygame.mixer.music.load("./resources/sounds/music/" + random.choice(os.listdir("./resources/sounds/music/")))
		#pygame.mixer.music.set_volume(0)
		#pygame.mixer.music.play()

		self.timer = 0
	
	def update(self):
		# cycling through events just for now
		eventList = pygame.event.get()

		for event in eventList:
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					quit()
		
		self.car.update(eventList)

	def draw(self):
		self.surface.fill((0, 0, 0))
		# if self.mission.InUse:
		#     self.mission.draw(self.surface)
		self.car.draw(self.surface)

		# blits the surface (where we've been drawing everything) to the window, making it bigger
		self.window.blit(pygame.transform.scale(self.surface, WINDOW_SIZE), (0, 0))
		pygame.display.flip()

	def main(self):
		while True:
			self.update()
			self.draw()
			
			clock.tick(60)

game = Game()
game.main()