import pygame

def draw_text(screen, text, pos, font, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def main_menu(screen, clock, FPS):
    font = pygame.font.Font(None, 74)
    running = True
    while running:
        screen.fill((0, 0, 0))

        draw_text(screen, "Launch", (100, 200), font, (255, 255, 255))
        draw_text(screen, "End playtest", (100, 300), font, (255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if 100 < mouse_pos[0] < 300 and 200 < mouse_pos[1] < 250:
                    print("launching playtest...")
                    return "launch_game"
                if 100 < mouse_pos[0] < 400 and 300 < mouse_pos[1] < 350:
                    print("ending game")
                    running = False

        pygame.display.flip()
        clock.tick(FPS)