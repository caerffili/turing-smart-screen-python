import library.config as config
from library.display import display
from library.log import logger
from library.stats import *

import os
import keyboard
import paho.mqtt.client as paho


broker_address= "10.20.21.40"
port = 1883

class ButtonHandler:

    def go(self):
        logger.info("Starting Button Handler")

        client = paho.Client(paho.CallbackAPIVersion.VERSION1, "Turing Smart Screen")
        client.connect(broker_address, port=port)
        client.loop_start()

    
        # Get root menu  
        if "MENU" in config.THEME_DATA: 
            if "ROOT" in config.THEME_DATA['MENU']:   
                menu_data = config.THEME_DATA['MENU']['ROOT']

                # load menu
                for button in menu_data:
                    logger.info("Setting Up Button " + button + " - " + menu_data[button]['MENULABEL'])
                    display_themed_value(menu_data[button]['TEXT'], value=menu_data[button]['MENULABEL'])


                while True:
                    # Wait for the next event.
                    event = keyboard.read_event()
                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name >= '1' and event.name <= '9':
                            if 'B' + event.name in menu_data:
                                
                                if 'ACTION' in menu_data['B' + event.name]:
                                    actions = menu_data['B' + event.name]['ACTION']

                                    for actiontype, actiondefs in actions.items():

                                        if actiontype == "SUBMENU" or actiontype == "BRIGHTNESS_DECREASE" or actiontype == "BRIGHTNESS_INCREASE":

                                            if actiontype == "SUBMENU":
                                                if str(actiondefs) in config.THEME_DATA['MENU']:
                                                    menu_data = config.THEME_DATA['MENU'][str(actiondefs)]
                                                    print("Loading Menu " + str(actiondefs))
                                                    # load menu
                                                    for button in menu_data:
                                                        logger.info("Setting Up Button " + button + " - " + menu_data[button]['MENULABEL'])
                                                        display_themed_value(menu_data[button]['TEXT'], value=menu_data[button]['MENULABEL'])
                                                else:
                                                    logger.error("Cannot find menu " + str(actiondefs) + " in the theme configuration file") 

                                            if actiontype == "BRIGHTNESS_DECREASE":
                                                config.CONFIG_DATA["display"]["BRIGHTNESS"] = config.CONFIG_DATA["display"]["BRIGHTNESS"] - 10
                                                if config.CONFIG_DATA["display"]["BRIGHTNESS"] < 10:
                                                    config.CONFIG_DATA["display"]["BRIGHTNESS"] = 10
                                                display.lcd.SetBrightness(config.CONFIG_DATA["display"]["BRIGHTNESS"])

                                            if actiontype == "BRIGHTNESS_INCREASE":
                                                config.CONFIG_DATA["display"]["BRIGHTNESS"] = config.CONFIG_DATA["display"]["BRIGHTNESS"] + 10
                                                if config.CONFIG_DATA["display"]["BRIGHTNESS"] > 100:
                                                    config.CONFIG_DATA["display"]["BRIGHTNESS"] = 100
                                                display.lcd.SetBrightness(config.CONFIG_DATA["display"]["BRIGHTNESS"])

                                        else:
                                            for actiondef in actiondefs:

                                                if actiontype == "MQTT":
                                                    print("MQTT Publish " + actiondef['TOPIC'] + " - " +actiondef['PAYLOAD'])
                                                    client.publish(actiondef['TOPIC'], actiondef['PAYLOAD'])

                                                if actiontype =="SHOW_ELEMENT":
                                                    elementrefs = actiondef['ELEMENT'].split(',')
                                                    print("Showing Element " + " / ".join(elementrefs))
                                                    if len(elementrefs) == 4:
                                                        theme_data = config.THEME_DATA.get(elementrefs[0], {}).get(elementrefs[1], {}).get(elementrefs[2], {}).get(elementrefs[3], {})
                                                    if len(elementrefs) == 5:
                                                        theme_data = config.THEME_DATA.get(elementrefs[0], {}).get(elementrefs[1], {}).get(elementrefs[2], {}).get(elementrefs[3], {}).get(elementrefs[4], {})
                                                    #if 'SHOW' in theme_data.get('SHOW') = True  
                                                    theme_data.update({"SHOW": True})                        
                                
                                                if actiontype =="HIDE_ELEMENT":
                                                    elementrefs = actiondef['ELEMENT'].split(',')
                                                    print("Hiding Element " + " / ".join(elementrefs))
                                                    if len(elementrefs) == 4:
                                                        theme_data = config.THEME_DATA.get(elementrefs[0], {}).get(elementrefs[1], {}).get(elementrefs[2], {}).get(elementrefs[3], {})
                                                    if len(elementrefs) == 5:
                                                        theme_data = config.THEME_DATA.get(elementrefs[0], {}).get(elementrefs[1], {}).get(elementrefs[2], {}).get(elementrefs[3], {}).get(elementrefs[4], {})

                                                    #theme_data['SHOW'] =  False
                                                    theme_data.update({"SHOW": False})  
                                                # For now, hiding elements will not remove it from the display.
                                                # It relies on anoth element to be enabble to replace it
                                                # display.lcd.DisplayBitmap(get_theme_file_path(theme_data.get("BACKGROUND_IMAGE", None)), theme_data['X'], theme_data['Y'], theme_data['RADIUS'], theme_data['RADIUS'])



            else:
                logger.error("Cannot find ROOT menu in the theme configuration file")
        else:
            logger.error("Cannot find MENU in the theme configuration file")