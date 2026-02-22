import asyncio
import websockets
import json
import engine
from websockets.asyncio.server import serve


async def game_loop():
    while True:
        engine.update_world()

        for room in engine.rooms.values():
            players = room["players"]
            zombie = room["zombie"]

            state_message = json.dumps({
                "type": "state",
                "players": list(players.values()),
                "zombie": zombie
            })

            for ws in list(players.keys()):
                try:
                    await ws.send(state_message)
                except:
                    pass

        await asyncio.sleep(0.1)


async def handler(websocket):
    path = websocket.path

    room_name = "default"

    if "room=" in path:
        room_name = path.split("room=")[1]

    if room_name not in engine.rooms:
        engine.rooms[room_name] = {
            "players": {},
            "zombie": {"x": 100, "y": 100}
        }

    player_id = id(websocket)

    room = engine.rooms[room_name]

    room["players"][websocket] = {
        "id": player_id,
        "x": 400,
        "y": 300,
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