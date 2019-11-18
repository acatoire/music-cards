#!/usr/bin/env python

#
# MUSIC CARD
# Application
#

# Python import
import subprocess
import time
import requests

# Bipbip Music import
from modules.rfid_reader.Reader import Reader
from modules.card_memory.CardMemory import CardMemory
from modules.cards_bdd.CardReader import CardBdd

import config as cfg    # Get config from file

# TODO check if bdd is automatically updated


def main():

    reader = Reader()
    bdd = CardBdd('https://bipbipzizik.firebaseio.com/', 'cards')

    # Previous card id memory
    try:
        # Get it from config
        previous_card = CardMemory(cfg.previousCardTimeout)
    except AttributeError:
        # Default value
        previous_card = CardMemory(30)

    # Create address path
    address = cfg.ip + ':' + cfg.port

    # Create command line
    if cfg.roomName == '':
        # Command for global playing
        command_with_room = address + '/'
    else:
        # Command for local playing
        command_with_room = address + '/' + cfg.roomName + '/'

    print('Ready: place a card on top of the reader')

    while True:
        read_id = reader.read_card()
        # Todo clear previous_card after some time (cfg.previousCardTimeout)

        try:
            print('Read card : ', read_id)

            # Find the card in bdd
            card = bdd.get_card(read_id)

            if card is not None:
                # Card execution
                mode = card.get_mode()
                command = card.get_command()

                print('Command : ', command)
                print('Modes : ', mode)

                if (previous_card.get() == read_id) and ("cancel" == cfg.multiReadMode) and (not card.has_mode("Command")):
                    # Cancel the read
                    print('Multi read : card canceled')
                else:
                    # Update the previous card memory
                    previous_card.set(read_id)

                    if card.has_mode("ClearQueue"):
                        command_line = "http://" + command_with_room + "clearqueue"
                        print(command_line)
                        response = requests.get(command_line)
                        print(response.text)

                    if command is not None:
                        command_line = "http://" + command_with_room + command
                        print(command_line)
                        response = requests.get(command_line)
                        print(response.text)

                    list(range(10000)) # some payload code
                    time.sleep(0.2)    # sane sleep time
            else:
                print('Failed to read card from bdd')

        except OSError as e:
            raise e
            print("Execution failed:")
            list(range(10000))       # some payload code                TODO needed??
            time.sleep(0.2)          # sane sleep time of 0.1 seconds   TODO needed??


if __name__ == "__main__":
    main()
