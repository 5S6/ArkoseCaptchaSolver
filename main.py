import time
import requests
import json
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from browsermobproxy import Server

##################################################
#                                                #
#           Based on ReCAPTCHA Solver            #
# https://github.com/notverdict/ReCAPTCHA-Solver #
#                                                #
##################################################


### CONFIG ###
apikey = ''

server = Server('browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat')
server.start()

chrome_options = webdriver.ChromeOptions()

proxy = server.create_proxy()
chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--mute-audio")
driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
### CONFIG ###

class FinishRecognize(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        print(' [!] Results: ' + data['results'][0]['alternatives'][0]['transcript'])
        driver.find_element_by_id("audio_response_field").send_keys(data['results'][0]['alternatives'][0]['transcript'].replace('%HESITATION', '')
            .replace('one', '1')
            .replace('two', '2')
            .replace('three', '3')
            .replace('four', '4')
            .replace('five', '5')
            .replace('six', '6')
            .replace('seven', '7')
            .replace('eight', '8')
            .replace('nine', '9')
            .replace('zero', '0')
            .replace(' ', ''))

        driver.find_element_by_id("audio_submit").click()
        print(' [!] Done.')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

class Arkose:
    def RecognizeAudio(self):
        RecognizeCallback = FinishRecognize()
        authenticator = IAMAuthenticator(apikey)
        speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )
        speech_to_text.set_service_url ('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/edf44363-198b-489f-9aa8-a320cd094d65')
        with open('payload.wav', 'rb') as audio:
            audio_source = AudioSource(audio)
            speech_to_text.recognize_using_websocket(
                audio=audio_source,
                content_type='audio/wav',
                recognize_callback=RecognizeCallback,
                model='en-US_NarrowbandModel',
                keywords=['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero'],
                keywords_threshold=1,
                max_alternatives=3)

    def start(self):
        proxy.new_har()
        driver.get('https://client-demo.arkoselabs.com/solo-animals')

        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src^='https://client-api.arkoselabs.com/fc/gc/']")))

        time.sleep(2)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "span[class='fc_meta_audio_btn']"))).click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.ID, "audio_play"))).click()
        
        time.sleep(2)

        for entry in proxy.har["log"]["entries"]:
            if entry["request"]["url"].startswith('https://client-api.arkoselabs.com/fc/get_audio/'):
                payload = entry["request"]["url"]
        
        wav = requests.get(payload, stream=True)
        open('payload.wav', 'wb').write(wav.content)
        self.RecognizeAudio()

if __name__ == "__main__":
    main = Arkose()
    main.start()