import pygame

from piece import Piece


def main() -> None:
    width, height = 800, 800
    fps = 60

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

        clock.tick(fps)

        screen.fill((0, 0, 0))

        pygame.display.flip()


if __name__ == '__main__':
    main()
