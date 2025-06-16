import pygame
import sys
import math  # Added for key animation
import random  # Added for random effects

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BLOCK_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Find the Key Game")
clock = pygame.time.Clock()

# Create a background pattern
def create_background():
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((240, 240, 240))  # Light gray base
    
    # Add a subtle grid pattern
    for x in range(0, SCREEN_WIDTH, 20):
        pygame.draw.line(background, (230, 230, 230), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 20):
        pygame.draw.line(background, (230, 230, 230), (0, y), (SCREEN_WIDTH, y))
    
    # Add some random dots for texture
    for _ in range(500):
        x = random.randint(0, SCREEN_WIDTH - 1)
        y = random.randint(0, SCREEN_HEIGHT - 1)
        color_var = random.randint(220, 235)
        pygame.draw.rect(background, (color_var, color_var, color_var), (x, y, 2, 2))
    
    return background

background = create_background()

# Game objects
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a more detailed player character
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Draw a more detailed character
        # Body
        pygame.draw.circle(self.image, BLUE, (15, 15), 12)
        pygame.draw.circle(self.image, (70, 130, 255), (15, 15), 10)
        
        # Face details
        pygame.draw.circle(self.image, WHITE, (11, 12), 3)  # Left eye
        pygame.draw.circle(self.image, WHITE, (19, 12), 3)  # Right eye
        pygame.draw.circle(self.image, BLACK, (11, 12), 1)  # Left pupil
        pygame.draw.circle(self.image, BLACK, (19, 12), 1)  # Right pupil
        
        # Smile
        pygame.draw.arc(self.image, BLACK, (10, 13, 10, 8), 0, 3.14, 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.has_key = False
        self.moves = 0  # Track number of moves
        
        # Animation variables
        self.animation_frame = 0
        self.direction = "right"
    
    def update(self, keys, walls, pushable_blocks):
        # Store original position to revert if collision occurs
        original_x = self.rect.x
        original_y = self.rect.y
        
        moved = False  # Track if player moved
        
        # Move horizontally
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
            moved = True
            self.direction = "left"
            self.animation_frame = (self.animation_frame + 0.2) % 4
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
            moved = True
            self.direction = "right"
            self.animation_frame = (self.animation_frame + 0.2) % 4
            
        # Check for horizontal collisions with walls
        wall_hit = pygame.sprite.spritecollide(self, walls, False)
        if wall_hit:
            self.rect.x = original_x
        
        # Check for horizontal collisions with blocks and try to push them
        block_hit_list = pygame.sprite.spritecollide(self, pushable_blocks, False)
        for block in block_hit_list:
            # Determine push direction
            if keys[pygame.K_RIGHT]:
                block.push('right', walls, pushable_blocks)
                # If block couldn't move, player can't move either
                if block.rect.left == self.rect.right:
                    self.rect.x = original_x
            elif keys[pygame.K_LEFT]:
                block.push('left', walls, pushable_blocks)
                # If block couldn't move, player can't move either
                if block.rect.right == self.rect.left:
                    self.rect.x = original_x
            
        # Move vertically
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
            moved = True
            self.animation_frame = (self.animation_frame + 0.2) % 4
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED
            moved = True
            self.animation_frame = (self.animation_frame + 0.2) % 4
            
        # Check for vertical collisions with walls
        wall_hit = pygame.sprite.spritecollide(self, walls, False)
        if wall_hit:
            self.rect.y = original_y
            moved = False
            
        # Check for vertical collisions with blocks and try to push them
        block_hit_list = pygame.sprite.spritecollide(self, pushable_blocks, False)
        for block in block_hit_list:
            # Determine push direction
            if keys[pygame.K_DOWN]:
                block.push('down', walls, pushable_blocks)
                # If block couldn't move, player can't move either
                if block.rect.top == self.rect.bottom:
                    self.rect.y = original_y
            elif keys[pygame.K_UP]:
                block.push('up', walls, pushable_blocks)
                # If block couldn't move, player can't move either
                if block.rect.bottom == self.rect.top:
                    self.rect.y = original_y
            
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            
        # Increment move counter if player actually moved
        if moved and (self.rect.x != original_x or self.rect.y != original_y):
            self.moves += 1
            
            # Update player appearance based on animation frame
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            
            # Draw the player body
            pygame.draw.circle(self.image, BLUE, (15, 15), 12)
            pygame.draw.circle(self.image, (70, 130, 255), (15, 15), 10)
            
            # Face details - adjust based on direction
            eye_offset = 1 if int(self.animation_frame) % 2 == 0 else 0
            
            if self.direction == "left":
                # Looking left
                pygame.draw.circle(self.image, WHITE, (10, 12 + eye_offset), 3)  # Left eye
                pygame.draw.circle(self.image, WHITE, (18, 12 + eye_offset), 3)  # Right eye
                pygame.draw.circle(self.image, BLACK, (9, 12 + eye_offset), 1)   # Left pupil
                pygame.draw.circle(self.image, BLACK, (17, 12 + eye_offset), 1)  # Right pupil
            else:
                # Looking right
                pygame.draw.circle(self.image, WHITE, (12, 12 + eye_offset), 3)  # Left eye
                pygame.draw.circle(self.image, WHITE, (20, 12 + eye_offset), 3)  # Right eye
                pygame.draw.circle(self.image, BLACK, (13, 12 + eye_offset), 1)  # Left pupil
                pygame.draw.circle(self.image, BLACK, (21, 12 + eye_offset), 1)  # Right pupil
            
            # Mouth - changes slightly during animation
            mouth_y = 17 + (1 if int(self.animation_frame) % 2 == 0 else 0)
            pygame.draw.arc(self.image, BLACK, (10, mouth_y, 10, 8), 0, 3.14, 1)

class PushableBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Create a more detailed block with 3D effect
        # Main block face
        pygame.draw.rect(self.image, ORANGE, (0, 0, 40, 40))
        
        # Highlight (top and left edges)
        pygame.draw.polygon(self.image, (255, 200, 100), [(0, 0), (40, 0), (35, 5), (5, 5), (5, 35), (0, 40)])
        
        # Shadow (bottom and right edges)
        pygame.draw.polygon(self.image, (200, 100, 0), [(40, 0), (40, 40), (0, 40), (5, 35), (35, 35), (35, 5)])
        
        # Wood grain pattern
        for i in range(3):
            y_pos = 10 + i * 10
            pygame.draw.line(self.image, (220, 120, 20), (5, y_pos), (35, y_pos), 1)
        
        # Crate markings
        pygame.draw.line(self.image, (180, 100, 20), (10, 5), (10, 35), 2)
        pygame.draw.line(self.image, (180, 100, 20), (30, 5), (30, 35), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def push(self, direction, walls, pushable_blocks):
        # Store original position
        original_x = self.rect.x
        original_y = self.rect.y
        
        # Move block based on direction
        if direction == 'right':
            self.rect.x += BLOCK_SPEED
        elif direction == 'left':
            self.rect.x -= BLOCK_SPEED
        elif direction == 'up':
            self.rect.y -= BLOCK_SPEED
        elif direction == 'down':
            self.rect.y += BLOCK_SPEED
        
        # Check for collisions with walls
        wall_hit = pygame.sprite.spritecollide(self, walls, False)
        
        # Check for collisions with other blocks
        # Create a temporary group without this block
        other_blocks = pygame.sprite.Group([b for b in pushable_blocks if b != self])
        block_hit = pygame.sprite.spritecollide(self, other_blocks, False)
        
        # If collision occurred, revert position
        if wall_hit or block_hit:
            self.rect.x = original_x
            self.rect.y = original_y
            return False
        
        # Keep block on screen
        if self.rect.left < 0:
            self.rect.left = 0
            return False
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            return False
        if self.rect.top < 0:
            self.rect.top = 0
            return False
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            return False
            
        return True

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, target_door):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Create a more detailed button
        # Button base
        pygame.draw.rect(self.image, (100, 0, 100), (0, 0, 40, 40))  # Purple base
        pygame.draw.rect(self.image, (120, 20, 120), (2, 2, 36, 36))  # Inner color
        
        # Button top
        pygame.draw.circle(self.image, PURPLE, (20, 20), 15)  # Button top
        pygame.draw.circle(self.image, (180, 100, 180), (20, 20), 15, 2)  # Button outline
        
        # Button center
        pygame.draw.circle(self.image, (200, 120, 200), (20, 20), 8)  # Button center
        pygame.draw.circle(self.image, (220, 140, 220), (17, 17), 3)  # Highlight
        
        # Button markings
        for i in range(4):
            angle = i * math.pi / 2
            x1 = 20 + 12 * math.cos(angle)
            y1 = 20 + 12 * math.sin(angle)
            x2 = 20 + 7 * math.cos(angle)
            y2 = 20 + 7 * math.sin(angle)
            pygame.draw.line(self.image, (80, 0, 80), (x1, y1), (x2, y2), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False
        self.target_door = target_door
        self.animation_frame = 0
    
    def update(self, pushable_blocks):
        # Check if any block is on the button
        block_on_button = False
        for block in pushable_blocks:
            if self.rect.colliderect(block.rect):
                block_on_button = True
                break
        
        # Update button state
        if block_on_button and not self.pressed:
            self.pressed = True
            self.animation_frame = 0
            
            # Pressed button appearance
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            
            # Button base - darker when pressed
            pygame.draw.rect(self.image, (80, 0, 80), (0, 0, 40, 40))  # Darker base
            pygame.draw.rect(self.image, (100, 10, 100), (2, 2, 36, 36))  # Inner color
            
            # Button top - pressed down
            pygame.draw.circle(self.image, CYAN, (20, 23), 15)  # Button top moved down
            pygame.draw.circle(self.image, (0, 180, 180), (20, 23), 15, 2)  # Button outline
            
            # Button center - glowing
            pygame.draw.circle(self.image, (100, 255, 255), (20, 23), 8)  # Button center
            pygame.draw.circle(self.image, WHITE, (17, 20), 3)  # Highlight
            
            # Activation rings
            pygame.draw.circle(self.image, WHITE, (20, 23), 12, 1)  # Inner ring
            pygame.draw.circle(self.image, (150, 255, 255), (20, 23), 10, 1)  # Middle ring
            
            self.target_door.open()  # Open the target door
            
        elif not block_on_button and self.pressed:
            self.pressed = False
            
            # Reset to unpressed appearance
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            
            # Button base
            pygame.draw.rect(self.image, (100, 0, 100), (0, 0, 40, 40))  # Purple base
            pygame.draw.rect(self.image, (120, 20, 120), (2, 2, 36, 36))  # Inner color
            
            # Button top
            pygame.draw.circle(self.image, PURPLE, (20, 20), 15)  # Button top
            pygame.draw.circle(self.image, (180, 100, 180), (20, 20), 15, 2)  # Button outline
            
            # Button center
            pygame.draw.circle(self.image, (200, 120, 200), (20, 20), 8)  # Button center
            pygame.draw.circle(self.image, (220, 140, 220), (17, 17), 3)  # Highlight
            
            # Button markings
            for i in range(4):
                angle = i * math.pi / 2
                x1 = 20 + 12 * math.cos(angle)
                y1 = 20 + 12 * math.sin(angle)
                x2 = 20 + 7 * math.cos(angle)
                y2 = 20 + 7 * math.sin(angle)
                pygame.draw.line(self.image, (80, 0, 80), (x1, y1), (x2, y2), 2)
            
            self.target_door.close()  # Close the target door
        
        # Animate the pressed button
        elif self.pressed:
            self.animation_frame += 1
            if self.animation_frame % 10 == 0:
                # Update the glow effect
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
                
                # Button base - darker when pressed
                pygame.draw.rect(self.image, (80, 0, 80), (0, 0, 40, 40))  # Darker base
                pygame.draw.rect(self.image, (100, 10, 100), (2, 2, 36, 36))  # Inner color
                
                # Button top - pressed down
                pygame.draw.circle(self.image, CYAN, (20, 23), 15)  # Button top moved down
                pygame.draw.circle(self.image, (0, 180, 180), (20, 23), 15, 2)  # Button outline
                
                # Button center - glowing
                pygame.draw.circle(self.image, (100, 255, 255), (20, 23), 8)  # Button center
                pygame.draw.circle(self.image, WHITE, (17, 20), 3)  # Highlight
                
                # Activation rings - animated
                ring_size = 10 + (self.animation_frame % 5)
                pygame.draw.circle(self.image, WHITE, (20, 23), ring_size, 1)  # Animated ring
                pygame.draw.circle(self.image, (150, 255, 255), (20, 23), ring_size - 2, 1)  # Inner animated ring

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        # Create a more detailed key
        # Key head (circle)
        pygame.draw.circle(self.image, YELLOW, (10, 7), 5)
        pygame.draw.circle(self.image, (255, 255, 150), (8, 5), 2)  # Highlight
        pygame.draw.circle(self.image, (200, 200, 0), (10, 7), 5, 1)  # Outline
        
        # Key shaft
        pygame.draw.rect(self.image, YELLOW, (8, 7, 4, 10))
        pygame.draw.rect(self.image, (200, 200, 0), (8, 7, 4, 10), 1)  # Outline
        
        # Key teeth
        pygame.draw.rect(self.image, YELLOW, (6, 14, 8, 3))
        pygame.draw.rect(self.image, (200, 200, 0), (6, 14, 8, 3), 1)  # Outline
        pygame.draw.rect(self.image, YELLOW, (6, 11, 3, 2))
        pygame.draw.rect(self.image, (200, 200, 0), (6, 11, 3, 2), 1)  # Outline
        
        # Sparkle effect
        pygame.draw.line(self.image, WHITE, (13, 4), (15, 2), 1)
        pygame.draw.line(self.image, WHITE, (13, 2), (15, 4), 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Add animation
        self.animation_timer = 0
        self.floating_offset = 0
        self.sparkle_timer = 0

    def update(self):
        # Make the key float up and down slightly
        self.animation_timer += 1
        old_y = self.rect.y
        self.floating_offset = math.sin(self.animation_timer / 10) * 3
        self.rect.y = old_y - self.floating_offset
        
        # Update sparkle effect
        self.sparkle_timer += 1
        if self.sparkle_timer % 30 < 15:  # Sparkle every half second
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            
            # Redraw key
            pygame.draw.circle(self.image, YELLOW, (10, 7), 5)
            pygame.draw.circle(self.image, (255, 255, 150), (8, 5), 2)  # Highlight
            pygame.draw.circle(self.image, (200, 200, 0), (10, 7), 5, 1)  # Outline
            pygame.draw.rect(self.image, YELLOW, (8, 7, 4, 10))
            pygame.draw.rect(self.image, (200, 200, 0), (8, 7, 4, 10), 1)
            pygame.draw.rect(self.image, YELLOW, (6, 14, 8, 3))
            pygame.draw.rect(self.image, (200, 200, 0), (6, 14, 8, 3), 1)
            pygame.draw.rect(self.image, YELLOW, (6, 11, 3, 2))
            pygame.draw.rect(self.image, (200, 200, 0), (6, 11, 3, 2), 1)
            
            # Add sparkle at different positions
            sparkle_pos = [(13, 4), (7, 6), (10, 3), (14, 7)]
            pos = sparkle_pos[int(self.sparkle_timer / 15) % 4]
            
            pygame.draw.line(self.image, WHITE, pos, (pos[0] + 2, pos[1] - 2), 1)
            pygame.draw.line(self.image, WHITE, (pos[0], pos[1] - 2), (pos[0] + 2, pos[1]), 1)


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, is_final=False):
        super().__init__()
        self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
        
        # Create a more detailed door
        # Door frame
        pygame.draw.rect(self.image, (139, 69, 19), (0, 0, 50, 80))  # Brown door
        
        # Door panels
        pygame.draw.rect(self.image, (160, 82, 45), (5, 5, 40, 35))  # Upper panel
        pygame.draw.rect(self.image, (160, 82, 45), (5, 45, 40, 30))  # Lower panel
        
        # Door handle
        pygame.draw.circle(self.image, YELLOW, (40, 40), 5)  # Handle
        pygame.draw.circle(self.image, (255, 255, 150), (38, 38), 2)  # Highlight
        
        # Door frame details
        pygame.draw.rect(self.image, (120, 60, 30), (0, 0, 50, 80), 3)  # Outer frame
        pygame.draw.line(self.image, (120, 60, 30), (5, 5), (45, 5), 2)  # Top inner frame
        pygame.draw.line(self.image, (120, 60, 30), (5, 75), (45, 75), 2)  # Bottom inner frame
        pygame.draw.line(self.image, (120, 60, 30), (5, 5), (5, 75), 2)  # Left inner frame
        pygame.draw.line(self.image, (120, 60, 30), (45, 5), (45, 75), 2)  # Right inner frame
        
        # Lock
        if is_final:
            pygame.draw.rect(self.image, RED, (35, 35, 10, 10))
            pygame.draw.circle(self.image, BLACK, (40, 40), 3, 1)  # Keyhole
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_open = False
        self.is_final = is_final  # Is this the final door that needs a key?
        self.animation_frame = 0
    
    def open(self):
        self.is_open = True
        self.animation_frame = 0
        
        if self.is_final:
            # Create an animated opening effect for the final door
            self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
            
            # Green glowing door
            pygame.draw.rect(self.image, GREEN, (0, 0, 50, 80))
            
            # Door panels with green glow
            pygame.draw.rect(self.image, (100, 255, 100), (5, 5, 40, 35))  # Upper panel
            pygame.draw.rect(self.image, (100, 255, 100), (5, 45, 40, 30))  # Lower panel
            
            # Door handle - gold
            pygame.draw.circle(self.image, YELLOW, (40, 40), 5)  # Handle
            pygame.draw.circle(self.image, WHITE, (38, 38), 2)  # Highlight
            
            # Door frame details
            pygame.draw.rect(self.image, (0, 180, 0), (0, 0, 50, 80), 3)  # Outer frame
            
            # Light beams
            pygame.draw.line(self.image, YELLOW, (25, 0), (25, 80), 3)  # Center beam
            pygame.draw.line(self.image, WHITE, (25, 0), (25, 80), 1)  # Center highlight
            
            # Sparkles
            for i in range(5):
                x = random.randint(10, 40)
                y = random.randint(10, 70)
                pygame.draw.line(self.image, WHITE, (x, y), (x+3, y-3), 1)
                pygame.draw.line(self.image, WHITE, (x, y-3), (x+3, y), 1)
        else:
            # Regular door opening animation
            self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
            
            # Door ajar effect
            pygame.draw.rect(self.image, (200, 200, 200), (0, 0, 50, 80))  # Light gray background
            pygame.draw.polygon(self.image, (139, 69, 19), [(10, 0), (50, 0), (50, 80), (10, 80)])  # Door ajar
            
            # Door handle
            pygame.draw.circle(self.image, YELLOW, (45, 40), 5)  # Handle moved to edge
            
            # Door frame
            pygame.draw.rect(self.image, (120, 60, 30), (0, 0, 50, 80), 3)  # Frame
    
    def close(self):
        if not self.is_final:  # Only non-final doors can be closed
            self.is_open = False
            
            # Reset to closed door appearance
            self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
            
            # Door frame
            pygame.draw.rect(self.image, (139, 69, 19), (0, 0, 50, 80))  # Brown door
            
            # Door panels
            pygame.draw.rect(self.image, (160, 82, 45), (5, 5, 40, 35))  # Upper panel
            pygame.draw.rect(self.image, (160, 82, 45), (5, 45, 40, 30))  # Lower panel
            
            # Door handle
            pygame.draw.circle(self.image, YELLOW, (40, 40), 5)  # Handle
            pygame.draw.circle(self.image, (255, 255, 150), (38, 38), 2)  # Highlight
            
            # Door frame details
            pygame.draw.rect(self.image, (120, 60, 30), (0, 0, 50, 80), 3)  # Outer frame
            pygame.draw.line(self.image, (120, 60, 30), (5, 5), (45, 5), 2)  # Top inner frame
            pygame.draw.line(self.image, (120, 60, 30), (5, 75), (45, 75), 2)  # Bottom inner frame
            pygame.draw.line(self.image, (120, 60, 30), (5, 5), (5, 75), 2)  # Left inner frame
            pygame.draw.line(self.image, (120, 60, 30), (45, 5), (45, 75), 2)  # Right inner frame
    
    def update(self):
        # Animate the door if it's open
        if self.is_open:
            self.animation_frame += 1
            
            if self.is_final and self.animation_frame % 10 == 0:
                # Update sparkles on final door
                self.open()  # Redraw with new random sparkles

class MiniDoor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
        
        # Create a more detailed mini door
        # Door frame
        pygame.draw.rect(self.image, RED, (0, 0, 50, 80))
        
        # Door panels
        pygame.draw.rect(self.image, (220, 20, 20), (5, 5, 40, 35))  # Upper panel
        pygame.draw.rect(self.image, (220, 20, 20), (5, 45, 40, 30))  # Lower panel
        
        # Door handle
        pygame.draw.circle(self.image, YELLOW, (40, 40), 5)  # Handle
        pygame.draw.circle(self.image, (255, 255, 150), (38, 38), 2)  # Highlight
        
        # Door frame details
        pygame.draw.rect(self.image, (150, 0, 0), (0, 0, 50, 80), 3)  # Outer frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 5), (45, 5), 2)  # Top inner frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 75), (45, 75), 2)  # Bottom inner frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 5), (5, 75), 2)  # Left inner frame
        pygame.draw.line(self.image, (150, 0, 0), (45, 5), (45, 75), 2)  # Right inner frame
        
        # Warning pattern
        for i in range(4):
            y_pos = 10 + i * 20
            pygame.draw.line(self.image, YELLOW, (10, y_pos), (40, y_pos), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_open = False
        self.animation_frame = 0
    
    def open(self):
        self.is_open = True
        self.animation_frame = 0
        
        # Create an opening animation
        self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
        
        # Door ajar effect
        pygame.draw.rect(self.image, (200, 200, 200), (0, 0, 50, 80))  # Light gray background
        pygame.draw.polygon(self.image, (220, 20, 20), [(10, 0), (50, 0), (50, 80), (10, 80)])  # Door ajar
        
        # Door handle
        pygame.draw.circle(self.image, YELLOW, (45, 40), 5)  # Handle moved to edge
        
        # Door frame
        pygame.draw.rect(self.image, (150, 0, 0), (0, 0, 50, 80), 3)  # Frame
        
        # Light effect
        pygame.draw.polygon(self.image, (255, 255, 200, 100), [(0, 0), (10, 0), (10, 80), (0, 80)])  # Light beam
    
    def close(self):
        self.is_open = False
        
        # Reset to closed door appearance
        self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
        
        # Door frame
        pygame.draw.rect(self.image, RED, (0, 0, 50, 80))
        
        # Door panels
        pygame.draw.rect(self.image, (220, 20, 20), (5, 5, 40, 35))  # Upper panel
        pygame.draw.rect(self.image, (220, 20, 20), (5, 45, 40, 30))  # Lower panel
        
        # Door handle
        pygame.draw.circle(self.image, YELLOW, (40, 40), 5)  # Handle
        pygame.draw.circle(self.image, (255, 255, 150), (38, 38), 2)  # Highlight
        
        # Door frame details
        pygame.draw.rect(self.image, (150, 0, 0), (0, 0, 50, 80), 3)  # Outer frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 5), (45, 5), 2)  # Top inner frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 75), (45, 75), 2)  # Bottom inner frame
        pygame.draw.line(self.image, (150, 0, 0), (5, 5), (5, 75), 2)  # Left inner frame
        pygame.draw.line(self.image, (150, 0, 0), (45, 5), (45, 75), 2)  # Right inner frame
        
        # Warning pattern
        for i in range(4):
            y_pos = 10 + i * 20
            pygame.draw.line(self.image, YELLOW, (10, y_pos), (40, y_pos), 2)
    
    def update(self):
        # Animate the door if it's open
        if self.is_open:
            self.animation_frame += 1
            if self.animation_frame % 20 == 0:
                # Update light effect
                self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
                
                # Door ajar effect
                pygame.draw.rect(self.image, (200, 200, 200), (0, 0, 50, 80))  # Light gray background
                pygame.draw.polygon(self.image, (220, 20, 20), [(10, 0), (50, 0), (50, 80), (10, 80)])  # Door ajar
                
                # Door handle
                pygame.draw.circle(self.image, YELLOW, (45, 40), 5)  # Handle moved to edge
                
                # Door frame
                pygame.draw.rect(self.image, (150, 0, 0), (0, 0, 50, 80), 3)  # Frame
                
                # Light effect - pulsing
                alpha = 100 + 50 * math.sin(self.animation_frame / 10)
                pygame.draw.polygon(self.image, (255, 255, 200, alpha), [(0, 0), (10, 0), (10, 80), (0, 80)])  # Light beam

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create a more detailed wall with brick pattern
        # Base color
        pygame.draw.rect(self.image, (139, 69, 19), (0, 0, width, height))
        
        # Brick pattern
        brick_height = 10
        brick_width = 20
        mortar_color = (160, 82, 45)
        
        for y_pos in range(0, height, brick_height):
            offset = 0 if (y_pos // brick_height) % 2 == 0 else brick_width // 2
            for x_pos in range(-offset, width, brick_width):
                # Draw brick
                if x_pos + brick_width > 0 and x_pos < width and y_pos + brick_height <= height:
                    brick_w = min(brick_width, width - x_pos) if x_pos >= 0 else brick_width + x_pos
                    brick_h = min(brick_height, height - y_pos)
                    
                    if x_pos < 0:
                        pygame.draw.rect(self.image, BROWN, (0, y_pos, brick_w, brick_h))
                    else:
                        pygame.draw.rect(self.image, BROWN, (x_pos, y_pos, brick_w, brick_h))
                    
                    # Draw mortar lines
                    if y_pos > 0:
                        pygame.draw.line(self.image, mortar_color, (max(0, x_pos), y_pos), 
                                        (min(width, x_pos + brick_width), y_pos), 1)
                    
                    if x_pos >= 0 and x_pos < width:
                        pygame.draw.line(self.image, mortar_color, (x_pos, max(0, y_pos)), 
                                        (x_pos, min(height, y_pos + brick_height)), 1)
        
        # Add some texture variation
        for _ in range(width * height // 50):
            x_pos = random.randint(0, width - 1)
            y_pos = random.randint(0, height - 1)
            color_var = random.randint(-20, 20)
            r = max(0, min(255, 139 + color_var))
            g = max(0, min(255, 69 + color_var))
            b = max(0, min(255, 19 + color_var))
            pygame.draw.rect(self.image, (r, g, b), (x_pos, y_pos, 2, 2))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create a more detailed obstacle with metal/stone appearance
        # Base color
        pygame.draw.rect(self.image, GRAY, (0, 0, width, height))
        
        # Metallic effect
        for i in range(width):
            for j in range(height):
                if (i + j) % 4 == 0:
                    pygame.draw.rect(self.image, (150, 150, 150), (i, j, 1, 1))
                elif (i + j) % 4 == 2:
                    pygame.draw.rect(self.image, (100, 100, 100), (i, j, 1, 1))
        
        # Rivets in corners
        rivet_radius = min(4, min(width, height) // 4)
        margin = rivet_radius + 1
        
        # Top-left rivet
        pygame.draw.circle(self.image, (80, 80, 80), (margin, margin), rivet_radius)
        pygame.draw.circle(self.image, (200, 200, 200), (margin-1, margin-1), rivet_radius//2)
        
        # Top-right rivet
        pygame.draw.circle(self.image, (80, 80, 80), (width-margin, margin), rivet_radius)
        pygame.draw.circle(self.image, (200, 200, 200), (width-margin-1, margin-1), rivet_radius//2)
        
        # Bottom-left rivet
        pygame.draw.circle(self.image, (80, 80, 80), (margin, height-margin), rivet_radius)
        pygame.draw.circle(self.image, (200, 200, 200), (margin-1, height-margin-1), rivet_radius//2)
        
        # Bottom-right rivet
        pygame.draw.circle(self.image, (80, 80, 80), (width-margin, height-margin), rivet_radius)
        pygame.draw.circle(self.image, (200, 200, 200), (width-margin-1, height-margin-1), rivet_radius//2)
        
        # Border
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, width, height), 2)
        
        # Hazard stripes if large enough
        if width >= 20 and height >= 20:
            stripe_width = width // 5
            for i in range(0, width, stripe_width * 2):
                if i + stripe_width <= width:
                    pygame.draw.rect(self.image, (200, 200, 0), (i, 0, stripe_width, 5))
                    pygame.draw.rect(self.image, (200, 200, 0), (i, height-5, stripe_width, 5))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Level class to manage different levels
class Level:
    def __init__(self, player_pos, key_pos, door_pos, walls_data, obstacles_data=None, 
                 blocks_data=None, buttons_data=None, mini_doors_data=None):
        self.player_pos = player_pos
        self.key_pos = key_pos
        self.door_pos = door_pos
        self.walls_data = walls_data
        self.obstacles_data = obstacles_data or []
        self.blocks_data = blocks_data or []
        self.buttons_data = buttons_data or []
        self.mini_doors_data = mini_doors_data or []
        
    def setup(self, all_sprites, walls, pushable_blocks, buttons, mini_doors):
        # Clear existing sprites
        all_sprites.empty()
        walls.empty()
        pushable_blocks.empty()
        buttons.empty()
        mini_doors.empty()
        
        # Create player
        player = Player(self.player_pos[0], self.player_pos[1])
        all_sprites.add(player)
        
        # Create mini doors first (so buttons can reference them)
        door_dict = {}  # To store doors by their ID for button references
        for i, door_data in enumerate(self.mini_doors_data):
            x, y = door_data
            mini_door = MiniDoor(x, y)
            all_sprites.add(mini_door)
            mini_doors.add(mini_door)
            walls.add(mini_door)  # Closed doors act as walls
            door_dict[i] = mini_door
        
        # Create buttons
        for button_data in self.buttons_data:
            x, y, target_door_id = button_data
            if target_door_id in door_dict:
                button = Button(x, y, door_dict[target_door_id])
                all_sprites.add(button)
                buttons.add(button)
        
        # Create key
        key = Key(self.key_pos[0], self.key_pos[1])
        all_sprites.add(key)
        
        # Create final door
        door = Door(self.door_pos[0], self.door_pos[1], is_final=True)
        all_sprites.add(door)
        
        # Create walls
        for wall_data in self.walls_data:
            x, y, width, height = wall_data
            wall = Wall(x, y, width, height)
            all_sprites.add(wall)
            walls.add(wall)
            
        # Create obstacles
        for obstacle_data in self.obstacles_data:
            x, y, width, height = obstacle_data
            obstacle = Obstacle(x, y, width, height)
            all_sprites.add(obstacle)
            walls.add(obstacle)  # Obstacles act as walls for collision
        
        # Create pushable blocks
        for block_data in self.blocks_data:
            x, y = block_data
            block = PushableBlock(x, y)
            all_sprites.add(block)
            pushable_blocks.add(block)
            
        return player, key, door

# Define levels
def create_levels():
    levels = []
    
    # Level 1 - Based on user's ASCII diagram with vertical mini door in wall
    level1 = Level(
        player_pos=(150, 150),     # O position (left side)
        key_pos=(650, 450),        # K position (far bottom-right)
        door_pos=(300, 150),       # D position (top-middle)
        walls_data=[
            # Room boundaries
            (100, 100, 600, 20),   # Top wall
            (100, 500, 600, 20),   # Bottom wall
            (100, 120, 20, 380),   # Left wall
            (700, 120, 20, 380),   # Right wall
            # Vertical wall with gap for mini door
            (500, 120, 20, 180),   # Top part of vertical wall
            (500, 380, 20, 120),   # Bottom part of vertical wall
        ],
        obstacles_data=[],
        blocks_data=[
            (150, 400),            # X position (bottom-left)
            (350, 250),            # Additional block for more challenge
        ],
        buttons_data=[
            (400, 400, 0),         # Button position (middle-bottom)
        ],
        mini_doors_data=[
            (500, 300),            # M position (middle of vertical wall)
        ]
    )
    levels.append(level1)
    
    # Level 2 - More complex with multiple blocks and buttons
    level2 = Level(
        player_pos=(150, 150),
        key_pos=(600, 400),
        door_pos=(200, 150),
        walls_data=[
            # Room boundaries
            (100, 100, 600, 20),   # Top wall
            (100, 500, 600, 20),   # Bottom wall
            (100, 120, 20, 380),   # Left wall
            (700, 120, 20, 380),   # Right wall
            # Inner walls
            (300, 200, 20, 150),   # Vertical divider (shortened to make room for mini door)
            (300, 400, 20, 100),   # Bottom part of vertical divider
            (300, 200, 300, 20),   # Horizontal divider top
            (500, 430, 20, 200),   # Vertical divider for key room(Change 2 later 300)
            (500, 300, 200, 20),   # Horizontal divider for key room
            # Additional maze elements
   #         (400, 350, 100, 20),   # Extra horizontal wall(removed DO nOT DELETE)
            (200, 300, 20, 100),   # Extra vertical wall
            # Removed wall that was blocking mini door
        ],
        obstacles_data=[
            (200, 300, 40, 40),    # Obstacle
            (450, 150, 30, 30),    # Additional obstacle
        ],
        blocks_data=[
            (150, 250),            # Pushable block 1
            # Removed block from top area (400, 150)
            (400, 250),            # Pushable block 3
            (250, 400),            # Additional block 4
        ],
        buttons_data=[
            (200, 400, 0),         # Button that opens mini door 0
            (400, 400, 1),         # Button that opens mini door 1
            (350, 350, 2),         # Additional button for new door
        ],
        mini_doors_data=[
            (300, 350),            # Mini door 0 - access to right section (moved to avoid wall)
            (500, 350),            # Mini door 1 - blocks access to key (moved to be accessible)
            (400, 300),            # Mini door 2 - new door for additional challenge
        ]
    )
    levels.append(level2)
    
    # Level 3 - Complex puzzle with multiple rooms
    level3 = Level(
        player_pos=(150, 150),
        key_pos=(600, 400),
        door_pos=(200, 150),
        walls_data=[
            # Room boundaries
            (100, 100, 600, 20),   # Top wall
            (100, 500, 600, 20),   # Bottom wall
            (100, 120, 20, 380),   # Left wall
            (700, 120, 20, 380),   # Right wall
            # Inner walls - creating rooms
            (300, 120, 20, 130),   # Left vertical divider top (shortened)
            (300, 300, 20, 200),   # Left vertical divider bottom (moved down to create gap)
            (500, 200, 20, 100),   # Right vertical divider top (shortened)
            (500, 350, 20, 150),   # Right vertical divider bottom (moved down to create gap)
            (300, 200, 200, 20),   # Top horizontal divider
            (300, 350, 200, 20),   # Bottom horizontal divider
            (500, 300, 200, 20),   # Key room horizontal divider
            # Additional maze elements
            (400, 250, 20, 50),    # Center vertical divider (shortened)
            (200, 300, 100, 20),   # Left room divider (moved to avoid conflict with mini door)
        ],
        obstacles_data=[
            (200, 350, 30, 30),    # Obstacle (moved to avoid blocking paths)
            (450, 150, 30, 30),    # Additional obstacle
            (600, 250, 30, 30),    # Obstacle near key (moved to avoid blocking paths)
        ],
        blocks_data=[
            (150, 250),            # Pushable block 1
            (400, 150),            # Pushable block 2
            (350, 250),            # Pushable block 3 (moved to avoid being trapped)
            (200, 450),            # Pushable block 4 (moved to be more accessible)
            (350, 400),            # Additional block 5 (moved to be more accessible)
            (550, 400),            # Block near key (moved to be more accessible)
        ],
        buttons_data=[
            (200, 400, 0),         # Button that opens mini door 0
            (400, 400, 1),         # Button that opens mini door 1
            (600, 350, 2),         # Button that opens mini door 2 (moved to be more accessible)
            (150, 350, 3),         # Additional button
        ],
        mini_doors_data=[
            (300, 250),            # Mini door 0 - middle section (moved to be accessible)
       #     (500, 300),            # Mini door 1 - upper right section (moved to be accessible)
  #          (500, 450),            # Mini door 2 - blocks access to key (moved to be accessible)
            (200, 250),            # Mini door 3 - additional door (moved to be accessible)
        ]
    )
    levels.append(level3)
    
    # Level 4 - Advanced maze with multiple paths
    level4 = Level(
        player_pos=(150, 150),
        key_pos=(650, 450),
        door_pos=(650, 150),
        walls_data=[
            # Room boundaries
            (100, 100, 600, 20),   # Top wall
            (100, 500, 600, 20),   # Bottom wall
            (100, 120, 20, 380),   # Left wall
            (700, 120, 20, 380),   # Right wall
            # Maze structure
            (200, 120, 20, 300),   # Vertical wall 1
            (300, 200, 20, 300),   # Vertical wall 2
            (400, 120, 20, 300),   # Vertical wall 3
            (500, 200, 20, 300),   # Vertical wall 4
            (600, 120, 20, 300),   # Vertical wall 5
            #(200, 200, 100, 20),   # Horizontal wall 1
            #(400, 300, 100, 20),   # Horizontal wall 2
            #(200, 400, 100, 20),   # Horizontal wall 3
            #(400, 200, 100, 20),   # Horizontal wall 4
            #(600, 300, 100, 20),   # Horizontal wall 5
        ],
        obstacles_data=[
            (250, 250, 30, 30),    # Obstacle 1
            (450, 350, 30, 30),    # Obstacle 2
            (550, 250, 30, 30),    # Obstacle 3
        ],
        blocks_data=[
            (150, 250),            # Block 1
            (350, 150),            # Block 2
            (450, 250),            # Block 3
            (250, 350),            # Block 4
            (550, 350),            # Block 5
        ],
        buttons_data=[
            (150, 450, 0),         # Button 1
            (350, 250, 1),         # Button 2
            (450, 450, 2),         # Button 3
            (550, 150, 3),         # Button 4
        ],
        mini_doors_data=[
            (200, 350),            # Door 1
            (400, 250),            # Door 2
            (500, 350),            # Door 3
            (600, 250),            # Door 4
        ]
    )
    levels.append(level4)
    
    # Level 5 - Puzzle with sequential button presses
    level5 = Level(
        player_pos=(150, 150),
        key_pos=(650, 450),
        door_pos=(150, 450),
        walls_data=[
            # Room boundaries
            (100, 100, 600, 20),   # Top wall
            (100, 500, 600, 20),   # Bottom wall
            (100, 120, 20, 380),   # Left wall
            (700, 120, 20, 380),   # Right wall
            # Inner structure
            (250, 120, 20, 280),   # Left vertical wall
            (250, 400, 20, 100),   # Left vertical wall bottom
            (450, 120, 20, 100),   # Right vertical wall top
            (450, 220, 20, 280),   # Right vertical wall bottom
            (250, 220, 200, 20),   # Top horizontal connector
            (250, 400, 200, 20),   # Bottom horizontal connector
            (550, 220, 20, 200),   # Far right vertical wall
        ],
        obstacles_data=[
            (300, 150, 40, 40),    # Obstacle 1
            (400, 350, 40, 40),    # Obstacle 2
            (600, 300, 40, 40),    # Obstacle 3
        ],
        blocks_data=[
            (150, 300),            # Block 1
            (350, 150),            # Block 2
            (350, 350),            # Block 3
            (500, 250),            # Block 4
            (600, 450),            # Block 5
        ],
        buttons_data=[
            (200, 200, 0),         # Button 1
            (350, 300, 1),         # Button 2
            (500, 400, 2),         # Button 3
            (600, 200, 3),         # Button 4
        ],
        mini_doors_data=[
            (250, 350),            # Door 1
            (450, 200),            # Door 2
            (550, 350),            # Door 3
            (450, 450),            # Door 4
        ]
    )
    return levels

# Create sprite groups
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
pushable_blocks = pygame.sprite.Group()
buttons = pygame.sprite.Group()
mini_doors = pygame.sprite.Group()

# Initialize levels
levels = create_levels()
current_level = 0
player, key, door = levels[current_level].setup(all_sprites, walls, pushable_blocks, buttons, mini_doors)

# Game loop
running = True
font = pygame.font.SysFont(None, 36)
game_won = False
start_time = pygame.time.get_ticks()  # Track game start time

while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset current level
                player, key, door = levels[current_level].setup(all_sprites, walls, pushable_blocks, buttons, mini_doors)
                player.has_key = False
                player.moves = 0  # Reset move counter
                start_time = pygame.time.get_ticks()  # Reset timer
    
    # Update
    if not game_won:
        keys = pygame.key.get_pressed()
        player.update(keys, walls, pushable_blocks)
        
        # Update buttons
        for button in buttons:
            button.update(pushable_blocks)
            
        # Update key animation if it exists
        if 'key' in locals() and key in all_sprites:
            key.update()
            
        # Update door animations
        if door in all_sprites:
            door.update()
            
        # Update mini door animations
        for mini_door in mini_doors:
            mini_door.update()
            
        # Update mini doors in walls group
        for mini_door in mini_doors:
            if mini_door.is_open:
                walls.remove(mini_door)
            else:
                if mini_door not in walls:
                    walls.add(mini_door)
        
        # Check if player collects the key
        if pygame.sprite.collide_rect(player, key) and not player.has_key:
            player.has_key = True
            all_sprites.remove(key)
        
        # Check if player opens the door with the key
        if pygame.sprite.collide_rect(player, door) and player.has_key and not door.is_open:
            door.open()
            
            # Check if there are more levels
            if current_level < len(levels) - 1:
                # Wait a bit before loading next level
                pygame.time.delay(1000)
                current_level += 1
                player, key, door = levels[current_level].setup(all_sprites, walls, pushable_blocks, buttons, mini_doors)
                player.has_key = False
                player.moves = 0  # Reset move counter for new level
                start_time = pygame.time.get_ticks()  # Reset timer for new level
            else:
                game_won = True
    
    # Draw
    screen.blit(background, (0, 0))  # Draw the background
    all_sprites.draw(screen)
    
    # Display status with better UI
    # Create a semi-transparent UI panel
    ui_panel = pygame.Surface((200, 150), pygame.SRCALPHA)
    ui_panel.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(ui_panel, (5, 5))
    
    # Add panel border
    pygame.draw.rect(screen, WHITE, (5, 5, 200, 150), 2)
    
    if player.has_key:
        key_text = font.render("Key: Collected", True, (255, 255, 100))
    else:
        key_text = font.render("Key: Not Found", True, WHITE)
    screen.blit(key_text, (15, 15))
    
    level_text = font.render(f"Level: {current_level + 1}/{len(levels)}", True, WHITE)
    screen.blit(level_text, (15, 55))
    
    # Display moves and time
    moves_text = font.render(f"Moves: {player.moves}", True, WHITE)
    screen.blit(moves_text, (15, 95))
    
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Convert to seconds
    time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
    screen.blit(time_text, (15, 135))
    
    # Instructions in a separate panel
    instruction_panel = pygame.Surface((400, 40), pygame.SRCALPHA)
    instruction_panel.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(instruction_panel, (SCREEN_WIDTH // 2 - 200, 5))
    
    # Add panel border
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 200, 5, 400, 40), 2)
    
    instructions = font.render("Arrow Keys: Move | R: Reset Level", True, WHITE)
    screen.blit(instructions, (SCREEN_WIDTH // 2 - 190, 15))
    
    if door.is_open and not game_won:
        # Create a glowing effect around the door
        glow_surface = pygame.Surface((70, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, (0, 255, 0, 100), (0, 0, 70, 100))
        screen.blit(glow_surface, (door.rect.x - 10, door.rect.y - 10))
        
        door_text = font.render("Door Opened!", True, GREEN)
        screen.blit(door_text, (SCREEN_WIDTH // 2 - 80, 50))
    
    if game_won:
        # Create a victory overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Victory panel
        victory_panel = pygame.Surface((500, 200), pygame.SRCALPHA)
        victory_panel.fill((0, 50, 0, 200))  # Dark green semi-transparent
        pygame.draw.rect(victory_panel, GREEN, (0, 0, 500, 200), 4)  # Green border
        
        # Add some decorative elements
        for i in range(20):
            x = random.randint(10, 490)
            y = random.randint(10, 190)
            size = random.randint(2, 5)
            pygame.draw.rect(victory_panel, (100, 255, 100, 150), (x, y, size, size))
        
        screen.blit(victory_panel, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100))
        
        # Victory text
        large_font = pygame.font.SysFont(None, 48)
        win_text = large_font.render("Congratulations!", True, WHITE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 70))
        
        complete_text = font.render("You completed all levels!", True, WHITE)
        screen.blit(complete_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 20))
        
        total_time = (pygame.time.get_ticks() - start_time) // 1000
        time_text = font.render(f"Total Time: {total_time}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))
        
        restart_text = font.render("Press R to restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 60))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
