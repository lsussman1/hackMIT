import arcade
import random
import os

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Mask UP!"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 200

MOVEMENT_SPEED = 10 * SPRITE_SCALING
GRAVITY = 0.9 * SPRITE_SCALING
JUMP_SPEED = 28 * SPRITE_SCALING
BULLET_SPEED = 5 * SPRITE_SCALING

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
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None

        # Set up the player
        self.player_sprite = None
        self.physics_engine = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite("sprite2.png",0.025)
        self.player_sprite.center_x = 25
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        #set up the enemys
        for i in range(15):
            enemy = arcade.Sprite("enemy1.png",0.025)
            enemy.center_x = random.randint(0,10000)
            enemy.center_y = 100
            self.enemy_list.append(enemy)

        for i in range(15):
            enemy = arcade.Sprite("enemy1.png",0.025)
            enemy.center_x = random.randint(0,10000)
            enemy.center_y = 325
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
        self.bullet_list.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_mouse_press(self):
        """Called whenever mouse button is clicked."""

        #Create a mask bullet
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING)

        #Mask bullet speed
        bullet.change_x = BULLET_SPEED

        #Position mask bullet
        bullet.center_x = self.player_sprite.center_x
        bullet.bottom = self.player_sprite.top

        #Add mask bullet to bullet list
        self.bullet_list.append(bullet)

    def on_update(self, delta_time):
        """ Movement and game logic """

        #Call update on bullet sprites
        self.bullet_list.update()
        
        #Call update on all sprites
        self.physics_engine.update()

        # -- manage germs propagating --
        for bullet in self.bullet_list:

            #Check if mask bullet hit germs
            enemy_hit_list = arcade.check_for_collision_with_list(self.player_list, self.enemy_list)

            if len(hit_list) > 2:
                bullet.remove_from_sprite_lists()

            for enemy in self.enemy_list:

                while True:
                    #have germs spewing from enemys not killed
                    if enemy in enemy_hit_list:
                        enemy.remove_from_sprites_lists()
                    #else: 
                    #lauren puts code here that manages virus icons spewing like bullets from the enemys still alive

            #If bullet goes off-screen, remove it
            if bullet.bottom > SCREEN WIDTH:
                bullet.remove_from_sprite_lists()
                    

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


