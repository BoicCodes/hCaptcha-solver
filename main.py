import requests, time, json, threading
from selenium import webdriver
from browsermobproxy import Server
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PyDictionary import PyDictionary

### CONFIG ###

server = Server('browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat')
server.start()

chrome_options = webdriver.ChromeOptions()

proxy = server.create_proxy()
chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
### CONFIG ###


class hCaptcha:
    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)

    def ReverseImage(self, link, word, lenamount):
        dictionary=PyDictionary()
        if word == "motorbus": word = "bus"
        words = dictionary.synonym(word)
        r = requests.post('https://www.imageidentify.com/objects/user-26a7681f-4b48-4f71-8f9f-93030898d70d/prd/urlapi', data={'image': link})
        for dik in words:
            if word in r.json()['identify']['title'] or dik in r.json()['identify']['alternatives'] or word in r.json()['identify']['alternatives'] or dik in r.json()['identify']['title']: return True
        return False

    def HandleReverseImg(self, img, lenamount, word):
        r = requests.get(img, stream=True)
        link = r.url

        while True:
            try:
                if self.ReverseImage(link, word, lenamount):
                    print(f' [!] Image {str((lenamount-9)*-1)} is correct.')
                    self.driver.find_elements_by_css_selector("div[class='task-image']")[int((lenamount-9)*-1)].click()
                    break
                else:
                    print(f' [!] Image {str((lenamount-9)*-1)} is incorrect.')
                    break
            except Exception:
                pass

    def start(self):
        proxy.new_har(options={'captureContent': True})
        self.driver.get('https://caspers.app/')

        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src^='https://assets.hcaptcha.com/captcha/v1/']")))
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "checkbox"))).click()

        time.sleep(5)

        imglist = []

        for entry in proxy.har["log"]["entries"]:
            if entry["request"]["url"].startswith('https://imgs.hcaptcha.com/'): imglist.append(entry["request"]["url"])
            if entry['request']['url'] == 'https://hcaptcha.com/getcaptcha': question = json.loads(entry['response']['content']['text'])['requester_question']['en']

        item = question.split(' ')[-1]
        print(f' [!] Item: {item}')
        print(f' [!] Pages: {str((len(imglist) - 3) / 9)}\n')

        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='Main content of the hCaptcha challenge']")))

        imglist = imglist[:len(imglist)-3]
        for pagenum in range(int(len(imglist)/9)):
            currentpage = imglist[:9]
            for img in imglist[:9]:
                threading.Thread(target=self.HandleReverseImg, args=(img, len(currentpage), item)).start()
                currentpage.remove(img)
                imglist.remove(img)
            while threading.active_count() != 1: pass
            if len(imglist) / 9 != pagenum + 1:
                self.driver.find_element_by_css_selector("div[class='submit-background']").click()
                print('\n [!] Next Page\n')
            else:
                self.driver.find_element_by_css_selector("div[class='submit-background']").click()
                print('\n [!] Done.\n')

if __name__ == '__main__':
    main = hCaptcha()
    start = time.time()
    main.start()
    stop = time.time()
    print(stop - start)