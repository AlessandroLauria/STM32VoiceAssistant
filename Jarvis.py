from gtts import gTTS
import speech_recognition as sr
import keyboard
import os
import time
import urllib3
from wireless import Wireless
from threading import Thread, Lock

from SerialComm import SerialComm

threadLock = Lock()
#stm32_uart = SerialComm('/dev/ttyACM0', 115200)
stm32_uart = SerialComm('/dev/tty.usbmodem14103', 115200)
name = "Jarvis"

name_setted = 0
#wifi_setted = 0
stm32_ready = 0

ssid = ""
seckey = ""

class Listener(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.speech_reco = sr.Recognizer()
        
    def speak(self, txt, file_name="./message_voice.mp3"):
        try:
            #tts = gTTS(text=txt, lang='it')
            #tts.save(file_name)
            #os.system("mpg123 " + file_name)
            print(txt)
        except Exception as e:
            print("[SPEAK ERROR] ", e)

    def run(self):
        global stm32_ready

        with sr.Microphone() as source:
            while True:
                if stm32_ready:
                    try:
                        threadLock.acquire()
                        #global wifi_setted
                        global name
                        nm = name
                        #ws = wifi_setted
                        threadLock.release()

                        #if ws:
                        
                        self.speech_reco.adjust_for_ambient_noise(source)
                        print("[LISTENER] I'm listening")
                        audio = self.speech_reco.listen(source)

                        print("[LISTENER] Something recognized")
                        txt =  self.speech_reco.recognize_google(audio, language="it-IT")
                        print("[LISTENER] Command available: ", txt)
                        keywd = txt.lower().find(nm.lower())

                        if keywd != -1:
                            filename = "bip.mp3"
                            os.system("mpg123 " + filename)

                            '''if txt[keywd+len(nm):].find("spegniti")!=-1:
                                self.speak("Mi sto spegnendo")
                                os.system("sudo shutdown now")
                                continue'''
                            
                            print("[LISTENER] Command detected : ", txt[keywd+len(nm):])
                            threadLock.acquire()
                            stm32_uart.send(txt[keywd+len(nm):] + "+")
                            threadLock.release()

                    except Exception as e:
                        print("[LISTENER ERROR] ",e)



class Talker(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        
        self.check_resources()
        
        
        
    def speak(self, txt, file_name="./message_voice.mp3"):
        try:
            tts = gTTS(text=txt, lang='it')
            tts.save(file_name)
            os.system("mpg123 " + file_name)
        except Exception as e:
            print("[SPEAK ERROR] ", e)
            
    '''def listen(self):
        try:
            with sr.Microphone() as source:
                self.speech_reco.adjust_for_ambient_noise(source)
                audio = self.speech_reco.listen(source)
                
                try:
                    return self.speech_reco.recognize_google(audio, language="it-IT")
                except Exception as e:
                    print("[RECO ERROR] ",e)
        except Exception as e:
            print("[LISTEN ERROR] ", e)'''

    def exchange_init_data_with_stm32(self, txt):
        global name_setted

        #global ssid
        #global seckey

        '''
        threadLock.acquire()
        global wifi_setted
        ws = wifi_setted
        threadLock.release()
        '''
        if txt.find("Connected to network with SSID") != -1:
            global stm32_ready
            stm32_ready = 1
            self.speak("Mi sono connesso alla rete con successo", "/message_voice.mp3")


        if txt.find("no Wi-Fi module detected") != -1:
            self.speak("Modulo WiFi non trovato", "/message_voice.mp3")

        if not name_setted:

            if(txt.find("[NAME]")!=-1 and txt.find("[END NAME]")!=-1):
                start_speak = txt.find("[NAME]") + 7
                end_speak = txt.find("[END NAME]") - 1

                #threadLock.acquire()
                global name
                name = txt[start_speak:end_speak]
                nm = name
                #threadLock.release()

                name_setted = 1

                self.speak("Ciao, mi sono avviato", "/start_message_voice.mp3")


            threadLock.acquire()
            stm32_uart.send("[NAME] send name [END NAME]+")
            stm32_ready = 1
            threadLock.release()

            name_request_send = 1

        '''
        if not ws:
            if txt.find("[SSID]")!=-1 and txt.find("[END SSID]")!=-1:
                start_speak = txt.find("[SSID]") + 7
                end_speak = txt.find("[END SSID]") - 1

                ssid = txt[start_speak:end_speak]

            if (ssid != "") and (txt.find("[PASS]")!=-1 and txt.find("[END PASS]")!=-1):
                start_speak = txt.find("[PASS]") + 7
                end_speak = txt.find("[END PASS]") - 1

                seckey = txt[start_speak:end_speak]

                wireless = Wireless()
                print("ssid: -", ssid,"-")
                print("pwd: -", seckey,"-")
                if wireless.connect(ssid=ssid, password=seckey):
                    self.speak("Ciao, mi sono avviato", "/start_message_voice.mp3")
                    threadLock.acquire()
                    wifi_setted = 1
                    threadLock.release()
                else:
                    print("[WIFI ERROR]")
        '''




    def check_resources(self):
        mic = False
        wifi = False

        print("[CHECK MICROPHONE]", end='')
        while not mic:
            try:
                sr.Microphone()
                mic = True
            except:
                print(".", end='')
                time.sleep(1)
        print("OK")
        
        print("[CHECK WIFI]", end='')
        http = urllib3.PoolManager()
        while not wifi:
            try:
                http.request('GET','http://216.58.192.142')
                wifi = True
            except:
                print(".", end='')
                time.sleep(1)
        print("OK")
        


    def parse_speak_message(self, txt):
        txt = str(txt)
        if(txt.find("[SPEAK]")!=-1 and txt.find("[END SPEAK]")!=-1):
            start_speak = txt.find("[SPEAK]") + 6
            end_speak = txt.find("[END SPEAK]")
            return txt[start_speak:end_speak]
        return -1

    def run(self):

        while True:
            #threadLock.acquire()
            txt = stm32_uart.read()
            #threadLock.release()

            self.exchange_init_data_with_stm32(txt)

            if txt: print("[STM32] ", txt)

            if self.parse_speak_message(txt) != -1:
                self.speak(self.parse_speak_message(txt))


                
talker = Talker()
listener = Listener()

talker.start()
listener.start()
