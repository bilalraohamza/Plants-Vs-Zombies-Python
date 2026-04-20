🌱🧟 Plants vs. Zombies: Python Edition
A fully playable, modular clone of the classic game Plants vs. Zombies, built entirely in Python using the Pygame library.

This project goes beyond a simple arcade clone. It features a robust state-machine architecture, a JSON-driven level engine, and dynamic gameplay mechanics that recreate the authentic PvZ experience—including classic daytime survival, nighttime resource management, and fan-favorite mini-games.

✨ Key Features
JSON-Driven Level Engine: Levels are not hardcoded. The game reads json files to dynamically generate zombie spawn waves, timing, available seed packets, and background environments.

Player Profile & Save System: Includes a fully functional login system. Players can create new profiles, and the game automatically tracks and saves their level progression across sessions using local data storage.

Multiple Game Modes:

Standard Survival: Manage sun resources, plant defenses, and survive waves of increasingly difficult zombies (including Coneheads, Bucketheads, and Newspaper Zombies).

Conveyor Belt Mini-game: Survive with a randomized, continuous feed of seed packets sliding in from the left.

Wall-nut Bowling: A specialized mini-game level where players roll Wall-nuts to bounce and smash through hordes of zombies.

Dynamic Environments: Features multiple custom backgrounds (Day, Night, Pool, Roof) with environment-specific logic (e.g., Sun stops falling from the sky during Night levels).

Interactive Hint System: An integrated, timed pop-up tutorial system to guide new players through the mechanics of the first few levels.

Polished UI & Menus: Features a custom main menu, an interactive in-game pause screen, and smooth state transitions.
