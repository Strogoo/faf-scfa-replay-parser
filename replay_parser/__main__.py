from io import BytesIO, FileIO, StringIO
import os
import base64
import json
import zlib

from constants import CommandStates
from body import ReplayBody
from reader import ReplayReader
from replay import continuous_parse, parse

REPLAYS_DIR = "D:/replays"
replayIDs = {}

def get_scfa_replay_by_data(data: bytes):
    """
    FAF and Supreme Commander has 2 kind of formats:
    1. scfareplay - that is simple binary stuff
    2. fafreplay - it's zlib compressed scfareplay data with json header
    """
    try:
        stream = StringIO(data.decode())
        header = stream.readline().strip()

        if json.loads(header):
            body = stream.read().strip()
            return zlib.decompress(base64.b64decode(body)[4:])
    except:
        pass

    return data

def get_replays_in_dir():
    replays = []
    n = 1
    for file_name in os.listdir(REPLAYS_DIR):
        if file_name.endswith(".fafreplay"):
            replayIDs[n] = file_name
            n = n + 1
            file = open(os.path.join(REPLAYS_DIR, file_name), "rb").read()
            scfa = get_scfa_replay_by_data(file)
            replays.append(scfa)
    return replays

#file = open("D:/replays/test.fafreplay", "rb").read()

#scfa = get_scfa_replay_by_data(file)

replayNum = 1
for replay in get_replays_in_dir():
    data = parse(
        replay,
        True,
        parse_commands={
            CommandStates.Advance,
            CommandStates.SetCommandSource,
            CommandStates.CommandSourceTerminated,
            CommandStates.VerifyChecksum,
            CommandStates.LuaSimCallback,
            CommandStates.IssueCommand,
            CommandStates.ProcessInfoPair,
        }
    )
    players = {}
    for k in data['header']['armies'].keys():
        players[k] = data['header']['armies'][k]['PlayerName']
    print(players)
    #break
    lookForAbuse = False
    n = 1
    for bd in data['body']:
        if n < 100000:
            n = n + 1

            for key in bd.keys():
                playerCommands = bd[key]
                for com in playerCommands.keys():
                    if lookForAbuse and com == "ProcessInfoPair":
                        if playerCommands[com]["arg1"] == "ToggleScriptBit":
                            print(str(n) + " " + players[key] + " " + playerCommands[com]["arg1"] + " " + playerCommands[com]['arg2'])

                    if com == "IssueCommand":
                        # print(playerCommands[com].keys())

                        if playerCommands[com]['cmd_data']['blueprint_id'] == "xrb3301":
                            print(replayNum)
                            print("TICK:" + str(n))
                            print("PLAYER:" + players[key])
                            print(playerCommands[com]['cmd_data'])
                            lookForAbuse = True
                        # print("-------")
    replayNum = replayNum + 1

print(replayIDs)
    #print("------------------------------------------------------")