import arcade
import random
import os

SPRITE_SCALING = 0.4

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Mask UP!"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 200

MOVEMENT_SPEED = 10 * SPRITE_SCALING
GRAVITY = 0.9 * SPRITE_SCALING
JUMP_SPEED = 28 * SPRITE_SCALING

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. 
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.wall_list = None
        self.player_list = None
        self.enemy_list = None
        self.virus_list = None
        self.mask_list = None

        # Set up the player
        self.player_sprite = None
        self.physics_engine = None
        self.health = 100
        self.health_text = None
        self.score = 0
        self.score_text = None
        self.game_over = False

        #set up physics engine for mask
        self.physics_engine_mask = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.virus_list = arcade.SpriteList()
        self.mask_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite("mask up player.png",0.005)
        self.score = 0
        self.health = 100
        self.player_sprite.center_x = 25
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        #set up initial mask
        self.mask = arcade.Sprite("mask up bullet.png", 0.005)

        #set up the enemys
        for i in range(15):
            enemy = arcade.Sprite("mask up enemy.png",0.007)
            enemy.center_x = random.randint(0,10000)
            enemy.center_y = 125
            self.enemy_list.append(enemy)

        for i in range(15):
            enemy = arcade.Sprite("mask up enemy.png",0.007)
            enemy.center_x = random.randint(0,10000)
            enemy.center_y = 340
            self.enemy_list.append(enemy)


        # -- Set up the floors

        # Create the ground floor
        for x in range(0, 10000, 64):
            wall = arcade.Sprite("block.png", 0.05)
            wall.center_x = x
            wall.center_y = 50

            #create random holes to fall through 10% of the time
            holeCoin = random.randint(1,10)
            if holeCoin != 1 or x == 0:
                self.wall_list.append(wall)

        # Create the second floor
        for x in range(500, 10000, 64):
            wall = arcade.Sprite("block.png", 0.05)
            wall.center_x = x
            wall.center_y = 250

            #create second story levels 30% of the time
            holeCoin = random.randint(1, 10)
            if holeCoin >= 7 or x == 0:
                self.wall_list.append(wall)


        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, gravity_constant = GRAVITY)
        self.physics_engine_mask = arcade.PhysicsEnginePlatformer(self.mask, self.wall_list, gravity_constant = GRAVITY)
            
        
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.virus_list.draw()
        self.mask_list.draw()

        output1 = f"SCORE: {self.score}"
        arcade.draw_text(output1, self.view_left + 10, self.view_bottom + 575, arcade.color.WHITE, 14)

        output2 = f"HEALTH: {self.health}"
        arcade.draw_text(output2, self.view_left + 10, self.view_bottom + 550, arcade.color.WHITE, 14)
        
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            #Create a mask mask
            mask = arcade.Sprite("mask up bullet.png", 0.005)
            self.physics_engine_mask = arcade.PhysicsEnginePlatformer(mask, self.wall_list, gravity_constant = GRAVITY)
            
            #Mask mask speed
            mask.change_x = 20

            #Position mask mask
            mask.center_x = self.player_sprite.center_x
            mask.bottom = self.player_sprite.top

            #Add mask mask to mask list
            self.mask_list.append(mask)


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        if not self.game_over:

            # Call update on all sprites
            self.physics_engine.update()
            self.physics_engine_mask.update()
            self.enemy_list.update()
            self.mask_list.update()
            self.virus_list.update()

            # -- manage germs propagating --
            for mask in self.mask_list:
                enemy_hit_list = arcade.check_for_collision_with_list(mask, self.enemy_list)
                if len(enemy_hit_list) > 0:
                    mask.remove_from_sprite_lists()

                # For every coin we hit, add to the score and remove the coin
                for enemy in enemy_hit_list:
                    enemy.remove_from_sprite_lists()
                    self.score += 1

            #spew a virus from a random enemy
            randomIndex = random.randint(0, len(self.enemy_list)-1)
            enemy = self.enemy_list[randomIndex]
            virus = arcade.Sprite("mask up germ.png", 0.005)
            virus.center_x = enemy.center_x
            virus.center_y = enemy.center_y
            virus.change_x = random.randint(-5,5)
            virus.change_y = random.randint(1,5)
            self.virus_list.append(virus)
            
            #decrement health with every virus hit taken
            virus_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.virus_list)
            self.health -= len(virus_hit_list)

            #game ends if health reaches 0
            if self.health == 0:
                self.game_over = True


        # --- Manage Scrolling ---

        # Keep track of if we changed the boundary. We don't want to call the
        # set_viewport command if we didn't change the view port.
        changed = False

        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        # Make sure our boundaries are integer values. While the view port does
        # support floating point numbers, for this application we want every pixel
        # in the view port to map directly onto a pixel on the screen. We don't want
        # any rounding errors.
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        # If we changed the boundary values, update the view port to match
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

