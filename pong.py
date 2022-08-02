from time import sleep
import pygame
import socket
from threading import Thread
import time
     
pygame.init()
pygame.display.set_caption("PONG")
clock = pygame.time.Clock()

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.mouse.set_visible(False)
enemyPos = [0,0]
playerPos = [0,0]


closing = False
connection = False
def networking():
    global enemyPos, connection

    #host or join
    join_option = input("OPTIONS:\nTo Join A Game, Enter 'Join'\nTo Host A Game, Enter 'Host'\n~")

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print(f"Host Name: {hostname}")
    print(f"Host IPv4: {IPAddr}")
    PORT = 9004

    nsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comm_socket = None

    if (join_option.lower() == "join"):
        IPAddr = input("Enter Host IPv4 Address: ")
        IPAddr = IPAddr.strip()
        #IPAddr is the game host
        nsocket.connect((IPAddr, PORT))
        comm_socket = nsocket
    elif (join_option.lower() == "host"):
        nsocket.bind((IPAddr, PORT))
        nsocket.listen(5)
        comm_socket, addr = nsocket.accept()
    else:
        print("Error: invalid response.")
        nsocket.close()

    if(join_option.lower() == "join"):
        while True:
            comm_socket.send(f"{playerPos[0]},{playerPos[1]}".encode('ascii'))

            resp = comm_socket.recv(1024).decode('ascii')
            print(f"package: {resp}")

            resp_arr = resp.split(',')
            resp_arr[0] = int(resp_arr[0].split('.')[0])
            resp_arr[1] = int(resp_arr[1].split('.')[0])
            enemyPos = [resp_arr[0], resp_arr[1]]
            sleep(0.01)
            connection = True

            if (closing):
                comm_socket.close()
                break

    if(join_option.lower() == "host"):
        while True:
            comm_socket.send(f"{playerPos[0]},{playerPos[1]}".encode('ascii'))

            resp = comm_socket.recv(1024).decode('ascii')
            print(f"package: {resp}")

            resp_arr = resp.split(',')
            resp_arr[0] = int(resp_arr[0].split('.')[0])
            resp_arr[1] = int(resp_arr[1].split('.')[0])
            enemyPos = [resp_arr[0], resp_arr[1]]
            sleep(0.01)
            connection = True

            if (closing):
                comm_socket.close()
                break
    

network_thread = Thread(target=networking)
network_thread.start()


class Player:
    playerWidth, playerHeight = (10, 70)
    rect_offset = (-playerWidth/2, -playerHeight/2)

    def __init__(self, isEnemy):
        self.x_pos, self.y_pos = pygame.mouse.get_pos()
        self.x_pos = SCREEN_WIDTH - 100
        self.rect = pygame.Rect(1, 1, self.playerWidth, self.playerHeight)
        self.isEnemy = isEnemy

    def update(self):
        global playerPos
        if (self.isEnemy == False):
            #update(left, top, width, height)
            #self.x_pos, self.y_pos = tuple(map(sum, zip(pygame.mouse.get_pos(), self.rect_offset)))
            self.y_pos = pygame.mouse.get_pos()[1] + self.rect_offset[1]
            if(self.x_pos < SCREEN_WIDTH/2):
                pygame.mouse.set_pos([SCREEN_WIDTH/2, pygame.mouse.get_pos()[1]])
                self.x_pos = SCREEN_WIDTH/2
            playerPos[0] = self.x_pos
            playerPos[1] = self.y_pos
            self.rect.update(self.x_pos, self.y_pos, self.playerWidth, self.playerHeight)
            pygame.draw.rect(screen, (255, 255, 255), self.rect)
        
        else:
            self.x_pos = SCREEN_WIDTH - enemyPos[0]
            self.y_pos = enemyPos[1]
            self.rect.update(self.x_pos, self.y_pos, self.playerWidth, self.playerHeight)
            pygame.draw.rect(screen, (255, 0, 0), self.rect)


class Ball():
    def __init__(self):
        self.x_pos, self.y_pos = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.radius = 5
        self.speed_x, self.speed_y = (0.8, -0.1)
        self.delta_t = 0.03
        self.lastTime = time.time()
    
    def update(self):
        if (time.time() - self.lastTime >= self.delta_t):
            self.x_pos += self.speed_x
            self.y_pos += self.speed_y
            self.lastTime = time.time()
        pygame.draw.circle(screen, (255, 255, 255), (self.x_pos, self.y_pos), self.radius)


player = Player(False)
enemyPlayer = Player(True)
ball = Ball()

running = True
while running:
    clock.tick(60)

    player.update()
    enemyPlayer.update()
    if (connection == True):
        ball.update()
    
    pygame.display.update()

    screen.fill((0,0,0))

    # event handling, gets all event from the event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closing = True
            running = False
