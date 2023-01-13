import tcod.event
import tcod.sdl.render


def is_in_box(all_boxes, x, y):
    for box in all_boxes:
        if x in range(box.x, box.x + box.width) and y in range(
            box.y, box.y + box.height
        ):
            return box
    return None


class InventoryBox:
    def __init__(self, x, y, width, height, item=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.item = item
        self.item_path = "assets\\items\\{}.png".format(self.item.name)

    def render(self, window):
        window.console.print_box(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            string=self.item.name,
        )
        window.show_image(self.item_path, self.x, self.y + 4, self.width, self.height)


def inventory_state(engine, window):
    x_offset = 3
    y_offset = 4
    box_width = 13
    box_height = 20
    max_items_per_page = (
        window.width // (box_width + 1) * (window.height // (box_height + 1))
    )
    player_items = engine.player.inventory.items
    if len(player_items) != 0:
        num_pages = len(player_items) // max_items_per_page
        all_page_items = [[] for _ in range(num_pages + 1)]
        i = 0
        for item in player_items:
            if len(all_page_items[i]) == max_items_per_page:
                i += 1
                y_offset = 4
                x_offset = 3
            elif x_offset + 8 > window.width:
                x_offset = 3
                y_offset += box_height + 1
            new_box = InventoryBox(x_offset, y_offset, box_width, box_height, item)
            all_page_items[i].append(new_box)
            x_offset += box_width + 1
        current_page = 0
    while True:
        window.console.clear()

        window.console.draw_frame(
            0,
            0,
            window.width,
            window.height,
            title="Inventory",
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            clear=True,
        )

        if len(player_items) == 0:
            window.console.print(
                window.width // 2,
                window.height // 2,
                "Inventory is empty",
                fg=(255, 255, 255),
                alignment=tcod.CENTER,
            )
        else:
            for inventory_box in all_page_items[current_page]:
                inventory_box.render(window)

        window.context.present(window.console)

        events = tcod.event.wait()

        event = engine.handle_inventory_events(events)

        if event == "close":
            engine.inventory_open = False
            return
        elif event == "next_page":
            if current_page < num_pages:
                current_page += 1
        elif event == "previous_page":
            if current_page > 0:
                current_page -= 1
        elif isinstance(event, tuple):
            mouse_x, mouse_y = event
            hit_box = is_in_box(all_page_items[current_page], mouse_x, mouse_y)
            if hit_box != None:
                hit_box.item.use(engine, engine.player)
                engine.inventory_open = False
                return


stat_description = {
    "Max_HP": "The maximum amount of health your character can have",
    "Strength": "How much damage your character can do",
    "Perception": "Your character's ability to hit enemies as well as how far your character can see",
    "Agility": "Your character's ability to dodge attacks as well as traps",
    "Intelligence": "The amount of skill points your character has to spend each level",
}

all_stat_names = ["Max_HP", "Strength", "Perception", "Agility", "Intelligence"]
all_stats = {
    "Max_HP": 10,
    "Strength": 10,
    "Perception": 10,
    "Agility": 10,
    "Intelligence": 10,
}
all_stat_colors = {
    "Max_HP": (255, 0, 0),
    "Strength": (0, 0, 255),
    "Perception": (255, 128, 0),
    "Agility": (0, 255, 255),
    "Intelligence": (255, 0, 255),
}


class StatBox:
    def __init__(self, x, y, width, height, stat_name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stat_name = stat_name
        self.stat_value = all_stats[stat_name]
        self.stat_description = stat_description[stat_name]
        self.stat_color = all_stat_colors[stat_name]

    def render(self, window):
        window.console.draw_frame(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            title=self.stat_name,
            fg=self.stat_color,
            bg=(0, 0, 0),
        )
        window.console.print_box(
            x=self.x + 3,
            y=self.y + 3,
            width=self.width - 5,
            height=self.height + self.y,
            string=self.stat_description,
        )
        window.console.print(
            x=self.x + self.width // 2,
            y=self.y + self.width // 2,
            string=str(all_stats[self.stat_name]),
            fg=(0, 255, 0),
        )


def main_menu(engine, window):

    while True:
        events = tcod.event.wait()
        if engine.handle_main_menu_events(events) == "new_game":
            return "playing"
        window.console.clear(bg=(0, 0, 0))

        window.console.draw_frame(
            0,
            0,
            window.width,
            window.height,
            title="Main menu",
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            clear=False,
        )

        window.context.present(window.console)


def stats_screen(engine, window):
    x_offset = 5
    y_offset = 3
    box_width = 26
    box_height = 20
    all_boxes = []
    temp_stats = {
        "Max_HP": engine.player.max_hp,
        "Strength": engine.player.strength,
        "Perception": engine.player.perception,
        "Intelligence": engine.player.intelligence,
        "Agility": engine.player.agility,
    }

    for i, stat in enumerate(all_stat_names):
        if y_offset + box_height >= window.height:
            y_offset = 3
            x_offset += box_width + 1
        new_box = StatBox(
            x_offset,
            y_offset,
            box_width,
            box_height,
            stat,
        )
        all_boxes.append(new_box)
        y_offset += box_height + 1
    original_points = engine.player.intelligence // 2 + 5
    available_points = original_points
    while available_points > 0:
        events = tcod.event.wait()
        event = engine.handle_main_menu_events(events)
        if isinstance(event, tuple):
            mouse_x, mouse_y = event
            hit_stat = is_in_box(all_boxes, mouse_x, mouse_y)
            if hit_stat != None:
                hit_stat.stat_value += 1
                all_stats[hit_stat.stat_name] += 1
                available_points -= 1
        elif event == "reset":
            for stat_box in all_boxes:
                stat_box.stat_value = temp_stats[stat_box.stat_name]
                all_stats[stat_box.stat_name] = stat_box.stat_value
            available_points = original_points
            available_points = original_points
        window.console.clear(bg=(0, 0, 0))

        for box in all_boxes:
            box.render(window)

        window.console.draw_frame(
            0,
            0,
            window.width,
            window.height,
            title="Player Sheet",
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            clear=False,
        )

        window.console.print(
            x=window.width // 2 + 5,
            y=window.height - 14,
            string=f"(Available points: {available_points})",
            fg=(255, 0, 255),
            bg=(0, 0, 0),
            alignment=tcod.CENTER,
        )

        window.console.print_box(
            x=window.width - 21,
            y=5,
            width=21,
            height=window.height - 5,
            string="Controls: \n\n\nMove: Arrow keys / WASD \n\n\nGo up stairs: < \n\n\nInventory: i \n\n\n Open Chest: e \n\n\nExit: Escape \n\n\nTo attack an enemy simply walk into them!",
        )

        window.console.print(
            x=window.width // 2 - 8,
            y=window.height // 2 + 15,
            string="Choose your stats wisely!",
            fg=(255, 255, 0),
        )

        window.show_image("assets\\main_character.png", window.width - 20, 48)

        window.console.print(
            x=window.width - 20, y=window.height // 2 + 10, string="Your character:"
        )

        window.console.print(
            x=window.width // 2 + 5,
            y=window.height - 10,
            string="Press r to reset",
            fg=(255, 0, 0),
            bg=(0, 0, 0),
            alignment=tcod.CENTER,
        )
        window.context.present(window.console)
    return list(all_stats.values())


def death_state(engine, window):
    window.console.clear(bg=(0, 0, 0))
    while True:
        events = tcod.event.wait()
        engine.handle_death_events(events)
        window.console.print_box(
            window.width // 2 - 5,
            window.height // 2,
            100,
            200,
            "You died!",
            fg=(255, 0, 0),
        )
        window.console.print_box(
            window.width // 2 - 10,
            window.height - 5,
            20,
            5,
            "Press esc to to quit",
            fg=(255, 255, 255),
        )
        window.context.present(window.console)
