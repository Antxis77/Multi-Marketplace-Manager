import os
import time
import shutil
import csv
import requests
import random
import re
import platform
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- GESTION DE LA CONFIGURATION ---
def get_config():
    if platform.system() == "Windows":
        default_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:
        default_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    config = {
        "ID_MEMBRE": "1", 
        "CHROME_PATH": default_path,
        "CHROME_VERSION": "0" 
    }
    
    if os.path.exists("config.txt"):
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    else:
        save_config(config["ID_MEMBRE"], config["CHROME_PATH"], config["CHROME_VERSION"])
    return config

def save_config(member_id, chrome_path, chrome_version):
    with open("config.txt", "w", encoding="utf-8") as f:
        f.write(f"ID_MEMBRE={member_id}\n")
        f.write(f"CHROME_PATH={chrome_path}\n")
        f.write(f"CHROME_VERSION={chrome_version}\n")

class VintedProBot:
    def __init__(self):
        self.driver = None
        self.load_account_config()

    def load_account_config(self):
        config = get_config()
        self.member_id = config["ID_MEMBRE"]
        self.chrome_path = config["CHROME_PATH"]
        self.chrome_version = int(config["CHROME_VERSION"])
        self.base_dir = os.path.abspath(f"vinted_backup/{self.member_id}")
        self.profile_dir = os.path.abspath(f"chrome_profile/{self.member_id}")
        self.csv_path = os.path.join(self.base_dir, "inventaire.csv")
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.profile_dir, exist_ok=True)
        if self.driver:
            self.driver.quit()
            self.driver = None

    def parse_vinted_date(self, text):
        """ Transforme 'Il y a 2 jours' en date réelle dd-mm-yyyy """
        now = datetime.now()
        t = text.lower()
        try:
            if any(x in t for x in ["instant", "seconde", "minute", "heure"]): 
                return now.strftime("%d-%m-%Y")
            if "hier" in t: 
                return (now - timedelta(days=1)).strftime("%d-%m-%Y")
            
            numbers = [int(s) for s in t.split() if s.isdigit()]
            num = numbers[0] if numbers else 1
            
            if "jour" in t: delta = timedelta(days=num)
            elif "semaine" in t: delta = timedelta(weeks=num)
            elif "mois" in t: delta = timedelta(days=num * 30)
            elif "an" in t: delta = timedelta(days=num * 365)
            else: return now.strftime("%d-%m-%Y")
            
            return (now - delta).strftime("%d-%m-%Y")
        except:
            return now.strftime("%d-%m-%Y")

    def start_driver(self):
        if not self.driver:
            print(f"🚀 Lancement Chrome | Profil : {self.member_id}")
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if platform.system() == "Windows":
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-gpu')

            options.binary_location = self.chrome_path
            
            try:
                ver = self.chrome_version if self.chrome_version > 0 else None
                self.driver = uc.Chrome(options=options, version_main=ver, use_subprocess=True)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                print(f"❌ Erreur lancement Chrome : {e}")

    def fast_copy_paste(self, element, text):
        self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
        element.send_keys(Keys.SPACE + Keys.BACKSPACE)

    def extract_id(self, url):
        match = re.search(r'/items/(\d+)', url)
        return match.group(1) if match else "Inconnu"

    def sync_cleanup(self, online_urls):
        if not os.path.exists(self.csv_path): return
        print("🧹 Nettoyage de l'inventaire...")
        rows_to_keep = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['URL'] in online_urls: rows_to_keep.append(row)
        
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_keep)

    def fill_vinted_form(self, item):
        item_id = self.extract_id(item['URL'])
        try:
            print(f"\n📢 Remplissage : {item['Titre'][:30]}...")
            self.driver.get("https://www.vinted.fr/items/new")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))).send_keys("\n".join(item['Images'].split(";")))
            time.sleep(7) 
            self.fast_copy_paste(self.driver.find_element(By.ID, "title"), item['Titre'])
            time.sleep(1.5)
            self.fast_copy_paste(self.driver.find_element(By.ID, "description"), item['Description'])
            time.sleep(1.5)
            price_el = self.driver.find_element(By.NAME, "price")
            price_el.clear()
            price_el.send_keys(item['Prix'].replace(',', '.'))
            print(f"✨ Formulaire prêt ! ID original : {item_id}")
            input(f"✅ Validez sur Chrome, puis ENTRÉE ici pour retirer l'article du stock...")
            self.remove_from_csv(item['URL'])
        except Exception as e: print(f"⚠️ Erreur formulaire : {e}")

    def remove_from_csv(self, item_url):
        if not os.path.exists(self.csv_path): return
        rows = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = [row for row in reader if row['URL'] != item_url]
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def get_items_urls(self):
        self.driver.get(f"https://www.vinted.fr/member/{self.member_id}")
        time.sleep(5)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height
        items = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/items/')]")
        urls = list(dict.fromkeys([i.get_attribute('href') for i in items if i.get_attribute('href')]))
        self.sync_cleanup(urls)
        return urls

    def save_process(self, urls, reset=False):
        if reset and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir); os.makedirs(self.base_dir)
        
        history = []
        if not reset and os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                history = [row['URL'] for row in csv.DictReader(f)]

        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a' if file_exists and not reset else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or reset:
                writer.writerow(["Titre", "Prix", "Description", "Images", "URL", "Date_Ajout"])
            
            for i, url in enumerate(urls):
                if url in history: continue
                print(f"🔍 Scan {i+1}/{len(urls)}... ID: {self.extract_id(url)}")
                time.sleep(random.uniform(8.0, 15.0))
                self.driver.get(url)
                try:
                    title = self.driver.title.split('|')[0].strip()
                    price = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")[0].text
                    desc = self.driver.find_element(By.XPATH, "//div[@itemprop='description']").text
                    
                    # Récupération de la date réelle (balise upload_date)
                    try:
                        date_text = self.driver.find_element(By.CSS_SELECTOR, "div[itemprop='upload_date'] span").text
                        real_date = self.parse_vinted_date(date_text)
                    except:
                        real_date = datetime.now().strftime("%d-%m-%Y")

                    folder_item = os.path.join(self.base_dir, f"item_{int(time.time())}_{i}")
                    os.makedirs(folder_item, exist_ok=True)
                    imgs = [im.get_attribute('src') for im in self.driver.find_elements(By.XPATH, "//div[contains(@class, 'item-photo')]//img")]
                    img_list = []
                    for j, img_url in enumerate(list(set(imgs))[:20]):
                        r = requests.get(img_url)
                        p = os.path.join(folder_item, f"img_{j}.jpg")
                        with open(p, 'wb') as f_img: f_img.write(r.content)
                        img_list.append(os.path.abspath(p))
                    
                    writer.writerow([title, price, desc, ";".join(img_list), url, real_date])
                    f.flush()
                except: continue

    def run_menu(self):
        while True:
            print("\n" + "═"*55)
            print(f"   VINTED PRO v1.3 | COMPTE : {self.member_id}")
            print("═"*55)
            print(" 0. 🔑 Connexion / Chrome")
            print(" 1. 🚮 Reset Scan (Tout refaire + Sync)")
            print(" 2. 🔄 Scan Nouveau (Ajouter + Sync)")
            print(" 3. 🚀 Republier les X derniers")
            print(" 4. 📤 Republier par ID article")
            print(" C. 👤 Changer de Compte")
            print(" P. 📍 Modifier Chemin / Version Chrome")
            print(" Q. ❌ Quitter")
            print("─"*55)
            c = input("\n Choix : ").upper()
            
            if c == "0": self.start_driver(); self.driver.get("https://www.vinted.fr")
            elif c == "1": self.start_driver(); self.save_process(self.get_items_urls(), True)
            elif c == "2": self.start_driver(); self.save_process(self.get_items_urls(), False)
            elif c == "3":
                num = input(" Nombre d'articles à republier : ")
                if num.isdigit() and os.path.exists(self.csv_path):
                    self.start_driver()
                    with open(self.csv_path, 'r', encoding='utf-8') as f:
                        annonces = list(csv.DictReader(f))[-int(num):]
                    for a in annonces:
                        self.driver.get(a['URL'])
                        input(f"🗑️ Supprimez l'article sur Chrome, puis ENTRÉE ici pour republier...")
                        self.fill_vinted_form(a)
            elif c == "4":
                item_id = input(" Entrez l'ID de l'article : ").strip()
                if os.path.exists(self.csv_path):
                    self.start_driver()
                    with open(self.csv_path, 'r', encoding='utf-8') as f:
                        for row in csv.DictReader(f):
                            if item_id in row['URL']:
                                self.driver.get(row['URL'])
                                input(f"🗑️ Supprimez l'article sur Chrome, puis ENTRÉE ici pour republier...")
                                self.fill_vinted_form(row)
                                break
            elif c == "C":
                new_id = input(" Nouvel ID Membre Vinted : ").strip()
                if new_id:
                    save_config(new_id, self.chrome_path, self.chrome_version)
                    self.load_account_config()
                    print(f"✅ Compte basculé sur : {self.member_id}")
            elif c == "P":
                print(f"\n1. Chemin : {self.chrome_path}\n2. Version : {self.chrome_version}")
                opt = input("Modifier (1/2) : ")
                if opt == "1": self.chrome_path = input("Nouveau chemin : ").strip()
                elif opt == "2": self.chrome_version = input("Version majeure (ex: 120) : ").strip()
                save_config(self.member_id, self.chrome_path, self.chrome_version); self.load_account_config()
            elif c == "Q":
                if self.driver: self.driver.quit()
                break

if __name__ == "__main__":
    VintedProBot().run_menu()