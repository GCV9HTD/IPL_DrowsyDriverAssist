import pygame

pygame.mixer.init()
pygame.mixer.music.load("raid.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
print "End"
