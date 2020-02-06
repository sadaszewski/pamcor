from pamcor.simulator import SimPlayer


class LearningPlayer(SimPlayer):
    def press_button(self, button):
        if button < 0 or button > 3:
            raise ValueError('Unrecognized button')

        move_dir_map = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        self.next_move_dir = move_dir_map[button]
