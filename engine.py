import json
rooms = {
        "room1": {
            "players": {},
            "zombie": {"x": 100, "y": 100}
        }
    }

WIDTH = 1600
HEIGHT = 600
def update_world():
    vx = 5
    vy = 5
    zx = 4
    zy = 2
    
    for room in rooms.values():

        players = room["players"]
        zombie_state = room["zombie"]
        for ws, player in list(players.items()):

            x = player["x"]
            y = player["y"]

            if player["health"] > 0:

                if player["input"]["W"]:
                    y -= vy
                if player["input"]["S"]:
                    y += vy
                if player["input"]["A"]:
                    x -= vx
                if player["input"]["D"]:
                    x += vx

            x = max(0, min(WIDTH, x))
            y = max(0, min(HEIGHT, y))

            player["x"] = x
            player["y"] = y

            # ----- COLLISION -----
            if (
                player["health"] > 0 and
                abs(x - zombie_state["x"]) < 30 and
                abs(y - zombie_state["y"]) < 30
            ):
                player["health"] -= 1

            if player["health"] <= 0:
                player["health"] = 0

        alive_players = [p for p in players.values() if p["health"] > 0]

        if alive_players:
            target = alive_players[0]

            dx = target["x"] - zombie_state["x"]
            dy = target["y"] - zombie_state["y"]

            if dx > 0:
                zombie_state["x"] += zx
            elif dx < 0:
                zombie_state["x"] -= zx

            if dy > 0:
                zombie_state["y"] += zy
            elif dy < 0:
                zombie_state["y"] -= zy
