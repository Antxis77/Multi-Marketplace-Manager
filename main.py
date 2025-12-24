import os
import time
import shutil
import csv
import requests
import random
import re
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- GESTION DE LA CONFIGURATION ---
def get_config():
    config = {"ID_MEMBRE": "1", "CHROME_PATH": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    else:
        save_config(config["ID_MEMBRE"], config["CHROME_PATH"])
    return config

def save_config(member_id, chrome_path):
    with open("config.txt", "w") as f:
        f.write(f"ID_MEMBRE={member_id}\n")
        f.write(f"CHROME_PATH={chrome_path}\n")

class VintedProBot:
    def __init__(self):
        self.driver = None
        self.load_account_config()

    def load_account_config(self):
        config = get_config()
        self.member_id = config["ID_MEMBRE"]
        self.chrome_path = config["CHROME_PATH"]
        self.base_dir = os.path.abspath(f"vinted_backup/{self.member_id}")
        self.profile_dir = os.path.abspath(f"chrome_profile/{self.member_id}")
        self.csv_path = os.path.join(self.base_dir, "inventaire.csv")
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.profile_dir, exist_ok=True)
        if self.driver:
            self.driver.quit()
            self.driver = None

    def start_driver(self):
        if not self.driver:
            print(f"🚀 Lancement Chrome | Profil : {self.member_id}")
            print(f"📍 Chemin Chrome : {self.chrome_path}")
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Utilisation du chemin configuré
            options.binary_location = self.chrome_path
            options.add_argument("--window-size=1920,1080")
            
            try:
                self.driver = uc.Chrome(options=options, use_subprocess=True)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                print(f"❌ Erreur au lancement de Chrome. Vérifiez le chemin dans l'option [P].\nErreur: {e}")

    # --- MÉTHODES DE REMPLISSAGE ---
    def human_type(self, element, text):
        element.clear()
        time.sleep(0.5)
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.2))

    def fast_copy_paste(self, element, text):
        self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
        element.send_keys(Keys.SPACE + Keys.BACKSPACE)

    def extract_id(self, url):
        match = re.search(r'/items/(\d+)', url)
        return match.group(1) if match else "Inconnu"

    def parse_vinted_date(self, text):
        now = datetime.now()
        t = text.lower()
        try:
            if any(x in t for x in ["instant", "seconde", "minute", "heure"]): return now.strftime("%d-%m-%Y")
            if "hier" in t: return (now - timedelta(days=1)).strftime("%d-%m-%Y")
            numbers = [int(s) for s in t.split() if s.isdigit()]
            num = numbers[0] if numbers else 1
            if "jour" in t: delta = timedelta(days=num)
            elif "semaine" in t: delta = timedelta(weeks=num)
            elif "mois" in t: delta = timedelta(days=num * 30)
            elif "an" in t: delta = timedelta(days=num * 365)
            else: return now.strftime("%d-%m-%Y")
            return (now - delta).strftime("%d-%m-%Y")
        except: return now.strftime("%d-%m-%Y")

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

    def sync_cleanup(self, online_urls):
        if not os.path.exists(self.csv_path): return
        print("🧹 Synchronisation de l'inventaire...")
        rows_to_keep = []
        count_removed = 0
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['URL'] in online_urls: rows_to_keep.append(row)
                else: count_removed += 1
        if count_removed > 0:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows_to_keep)
            print(f"✅ {count_removed} article(s) retiré(s) (vendus/supprimés).")

    def fill_vinted_form(self, item):
        item_id = self.extract_id(item['URL'])
        try:
            print(f"\n📢 En cours : {item['Titre'][:30]}... [ID: {item_id}]")
            self.driver.get("https://www.vinted.fr/items/new")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))).send_keys("\n".join(item['Images'].split(";")))
            print("⏳ Photos (7s)...")
            time.sleep(7) 
            self.fast_copy_paste(self.driver.find_element(By.ID, "title"), item['Titre'])
            time.sleep(random.uniform(1.0, 2.0))
            self.fast_copy_paste(self.driver.find_element(By.ID, "description"), item['Description'])
            time.sleep(random.uniform(1.0, 2.0))
            self.human_type(self.driver.find_element(By.NAME, "price"), item['Prix'].replace(',', '.'))
            print(f"✨ Formulaire prêt !")
            input(f"✅ Validez sur Chrome, puis ENTRÉE ici pour supprimer l'ID {item_id}...")
            self.remove_from_csv(item['URL'])
        except Exception as e: print(f"⚠️ Erreur formulaire : {e}")

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.5, 4.0))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

    def get_items_urls(self):
        self.driver.get(f"https://www.vinted.fr/member/{self.member_id}")
        time.sleep(5)
        self.scroll_to_bottom()
        items = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/items/')]")
        urls = list(dict.fromkeys([i.get_attribute('href') for i in items if i.get_attribute('href')]))
        self.sync_cleanup(urls)
        return urls

    def save_process(self, urls, reset=False):
        if reset and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir); os.makedirs(self.base_dir)
        history = [] if reset else self.get_already_scrapped_urls()
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a' if file_exists and not reset else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or reset:
                writer.writerow(["Titre", "Prix", "Description", "Images", "URL", "Date_Ajout"])
            for i, url in enumerate(urls):
                if url in history: continue
                print(f"🔍 Scan article {i+1}/{len(urls)}...")
                time.sleep(random.uniform(8.0, 15.0))
                self.driver.get(url)
                try:
                    title = self.driver.title.split('|')[0].strip()
                    price = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")[0].text
                    desc = self.driver.find_element(By.XPATH, "//div[@itemprop='description']").text
                    date_text = self.driver.find_element(By.CSS_SELECTOR, "div[itemprop='upload_date'] span").text
                    real_date = self.parse_vinted_date(date_text)
                    folder_item = os.path.join(self.base_dir, f"item_{int(time.time())}_{i}")
                    os.makedirs(folder_item, exist_ok=True)
                    imgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'item-photo')]//img")
                    img_list = []
                    for j, img in enumerate(list(set([im.get_attribute('src') for im in imgs if im.get_attribute('src')]))):
                        r = requests.get(img)
                        p = os.path.join(folder_item, f"img_{j}.jpg")
                        with open(p, 'wb') as f_img: f_img.write(r.content)
                        img_list.append(os.path.abspath(p))
                    writer.writerow([title, price, desc, ";".join(img_list), url, real_date])
                    f.flush()
                    print(f"✨ Sauvegardé : {title[:20]}...")
                except: continue

    def get_already_scrapped_urls(self):
        if not os.path.exists(self.csv_path): return []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            return [row['URL'] for row in csv.DictReader(f)]

    def run_menu(self):
        while True:
            print("\n" + "═"*55)
            print(f"   VINTED PRO v1.4 | COMPTE : {self.member_id}")
            print("═"*55)
            print(" 0. 🔑 Connexion / Chrome")
            print(" 1. 🚮 Reset Scan (Tout refaire + Sync)")
            print(" 2. 🔄 Scan Nouveau (Ajouter + Sync)")
            print(" 3. 🚀 Republier les X derniers")
            print(" 4. 📤 Republier par ID")
            print(" C. 👤 Changer de Compte")
            print(" P. 📍 Modifier chemin Chrome")
            print(" Q. ❌ Quitter")
            print("─"*55)
            c = input("\n Choix : ").upper()
            if c == "0": self.start_driver(); self.driver.get("https://www.vinted.fr")
            elif c == "1": self.start_driver(); self.save_process(self.get_items_urls(), True)
            elif c == "2": self.start_driver(); self.save_process(self.get_items_urls(), False)
            elif c == "3":
                num = input(" Nombre d'articles : ")
                if num.isdigit() and os.path.exists(self.csv_path):
                    self.start_driver()
                    with open(self.csv_path, 'r', encoding='utf-8') as f:
                        annonces = list(csv.DictReader(f))[-int(num):]
                    for a in annonces:
                        self.driver.get(a['URL'])
                        input(f"🗑️ Supprimez l'ID {self.extract_id(a['URL'])} puis ENTRÉE...")
                        self.fill_vinted_form(a)
            elif c == "4":
                item_id = input(" ID Article : ").strip()
                if os.path.exists(self.csv_path):
                    self.start_driver()
                    with open(self.csv_path, 'r', encoding='utf-8') as f:
                        for row in csv.DictReader(f):
                            if item_id in row['URL']: self.fill_vinted_form(row); break
            elif c == "C":
                new_id = input(" Nouvel ID Membre : ").strip()
                if new_id: save_config(new_id, self.chrome_path); self.load_account_config()
            elif c == "P":
                new_path = input(f" Chemin actuel : {self.chrome_path}\n Nouveau chemin : ").strip()
                if new_path: save_config(self.member_id, new_path); self.load_account_config()
            elif c == "Q":
                if self.driver: self.driver.quit()
                break

if __name__ == "__main__":
    VintedProBot().run_menu()
