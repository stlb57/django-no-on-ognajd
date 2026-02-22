import asyncio
import websockets
import json
import random

from websockets.asyncio.server import serve

rooms = {
    "room1": {
        "players": {},
        "zombie": {"x": 100, "y": 100}
    }
}

WIDTH = 1600
HEIGHT = 600

async def game_loop():
    vx = 5
    vy = 5
    zx = 4
    zy = 2

    while True:
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


            state_message = json.dumps({
                "type": "state",
                "players": list(players.values()),
                "zombie": zombie_state
            })

            for ws in list(players.keys()):
                try:
                    await ws.send(state_message)
                except:
                    pass

            await asyncio.sleep(0.1)


async def handler(websocket):

    player_id = id(websocket)

    room = rooms["room1"]
    room["players"][websocket] = {
        "id": player_id,
        "x": random.randint(100, 500),
        "y": random.randint(100, 500),
        "health": 100,
        "input": {"W": False, "A": False, "S": False, "D": False}
    }


    await websocket.send(json.dumps({
        "type": "init",
        "id": player_id
    }))

    try:
        async for message in websocket:

            if message in room["players"][websocket]["input"]:
                room["players"][websocket]["input"][message] = True

            elif message.startswith("STOP_"):
                key = message.replace("STOP_", "")
                if key in room["players"][websocket]["input"]:
                    room["players"][websocket]["input"][key] = False

    finally:
        if websocket in room["players"]:
            del room["players"][websocket]


async def main():
    asyncio.create_task(game_loop())
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
