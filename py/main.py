import pygame, math

WINDOW_SIZE = (512, 512)
SURFACE_SIZE = (128, 128)

clock = pygame.time.Clock()

class Car:
	# this code stolen from https://rmgi.blog/pygame-2d-car-tutorial.html

	playerPos = pygame.math.Vector2(32, 32)
	velocity = pygame.math.Vector2(0, 0)
	angle = 0
	length = 4
	steering = 0

	def __init__(self):
		# load image, rotated 270 to face right direction
		self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./assets/car.png"), (6, 8)), 270)
	
	def update(self):
		dt = clock.get_time() / 1000

		# velocity for car, accounting 4 rotation
		if self.steering:
			turningRadius = self.length / math.sin(math.radians(self.steering))
			angularVelocity = self.velocity.x / turningRadius
		else:
			angularVelocity = 0
		
		self.playerPos += self.velocity.rotate(-self.angle) * dt
		self.angle += math.degrees(angularVelocity) * dt

		# input
		keys = pygame.key.get_pressed()
		
		if keys[pygame.K_z]:
			self.velocity.x = 50
		elif keys[pygame.K_x]:
			self.velocity.x = -30
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
		surface.blit(pygame.transform.rotate(self.image, self.angle), self.playerPos)

class Game:
	surface = pygame.surface.Surface(SURFACE_SIZE)
	window  = pygame.display.set_mode(WINDOW_SIZE)
	active  = True

	pygame.display.set_caption("death race 76")

	def __init__(self):
		pygame.init()
		self.car = Car()
	
	def __del__(self):
		pygame.quit()

	def update(self):
		eventList = pygame.event.get()

		for event in eventList:
			if event.type == pygame.QUIT:
				self.active = False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.active = False
		
		self.car.update()
	
	def draw(self):
		self.surface.fill((0, 0, 0))
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