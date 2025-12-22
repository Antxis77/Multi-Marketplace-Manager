import os
import time
import shutil
import csv
import requests
import sys
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
def get_config_id():
    if not os.path.exists("config.txt"):
        with open("config.txt", "w") as f: f.write("ID_MEMBRE=1")
        return "1"
    with open("config.txt", "r") as f:
        for line in f:
            if "ID_MEMBRE" in line: return line.split("=")[1].strip()
    return "1"

def set_config_id(new_id):
    with open("config.txt", "w") as f: f.write(f"ID_MEMBRE={new_id}")

class VintedProBot:
    def __init__(self):
        self.driver = None
        self.load_account_config()

    def load_account_config(self):
        self.member_id = get_config_id()
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
            print(f"🚀 Lancement Chrome | Profil : {self.member_id}...")
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            options.add_argument("--window-size=1920,1080")
            self.driver = uc.Chrome(options=options, use_subprocess=True)

    def parse_vinted_date(self, text):
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
        except: return now.strftime("%d-%m-%Y")

    def remove_from_csv(self, item_url):
        """Supprime définitivement l'article du CSV après republication"""
        if not os.path.exists(self.csv_path): return
        rows = []
        found = False
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['URL'] != item_url:
                    rows.append(row)
                else:
                    found = True
        
        if found:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"🗑️ Article retiré de l'inventaire (sera ré-ajouté au prochain scan).")

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

    def robust_fill(self, element, text):
        try:
            text_clean = text.replace('"', '\\"').replace('\n', '\\n')
            self.driver.execute_script(f'arguments[0].value = "{text_clean}";', element)
            element.send_keys(Keys.SPACE + Keys.BACKSPACE)
        except: pass

    def fill_vinted_form(self, item):
        try:
            print(f"\n📢 Publication : {item['Titre'][:40]}...")
            self.driver.get("https://www.vinted.fr/items/new")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))).send_keys("\n".join(item['Images'].split(";")))
            print("⏳ Photos (5s)...")
            time.sleep(5) 
            self.robust_fill(self.driver.find_element(By.ID, "title"), item['Titre'])
            self.robust_fill(self.driver.find_element(By.ID, "description"), item['Description'])
            price = self.driver.find_element(By.NAME, "price")
            price.clear()
            price.send_keys(item['Prix'].replace(',', '.'))
            print("\n✨ Formulaire prêt !"); input("✅ Validez sur Chrome, puis ENTRÉE ici pour supprimer de la liste...")
            self.remove_from_csv(item['URL'])
        except Exception as e: print(f"⚠️ Erreur formulaire : {e}")

    def get_items_urls(self):
        self.driver.get(f"https://www.vinted.fr/member/{self.member_id}"); time.sleep(4)
        self.scroll_to_bottom()
        items = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/items/')]")
        return list(dict.fromkeys([i.get_attribute('href') for i in items if i.get_attribute('href')]))

    def save_process(self, urls, reset=False):
        if reset and os.path.exists(self.base_dir):
            for filename in os.listdir(self.base_dir):
                file_path = os.path.join(self.base_dir, filename)
                try:
                    if os.path.isfile(file_path): os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except: pass
        history = [] if reset else self.get_already_scrapped_urls()
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a' if file_exists and not reset else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or reset:
                writer.writerow(["Titre", "Prix", "Description", "Images", "URL", "Date_Ajout"])
            for i, url in enumerate(urls):
                if url in history: continue
                self.driver.get(url); time.sleep(3)
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
                    f.flush(); print(f"✨ Sauvegardé : {title[:25]} | {real_date}")
                except: continue

    def get_already_scrapped_urls(self):
        if not os.path.exists(self.csv_path): return []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            return [row['URL'] for row in csv.DictReader(f)]

    def run_menu(self):
        while True:
            print("\n" + "═"*50)
            print(f"   VINTED PRO v1.1 | COMPTE : {self.member_id}")
            print("═"*50)
            print(" 0. 🔑 Connexion / Chrome")
            print(" 1. 🚮 Reset Scan (Tout refaire)")
            print(" 2. 🔄 Scan Nouveau (Ajouter)")
            print(" 3. 🚀 Republier les X derniers")
            print(" 4. 📤 Republier par ID")
            print(" C. 👤 Changer de Compte")
            print(" Q. ❌ Quitter")
            print("─"*50)
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
                        input(f"🗑️ Supprimez '{a['Titre'][:20]}' puis ENTRÉE...")
                        self.fill_vinted_form(a)
            elif c == "4":
                item_id = input(" ID Article : ").strip()
                if os.path.exists(self.csv_path):
                    self.start_driver()
                    with open(self.csv_path, 'r', encoding='utf-8') as f:
                        for row in csv.DictReader(f):
                            if item_id in row['URL']: self.fill_vinted_form(row); break
            elif c == "C":
                new_id = input(" Nouvel ID : ").strip()
                if new_id: set_config_id(new_id); self.load_account_config()
                print(f"✅ Basculé sur {new_id}")
            elif c == "Q":
                if self.driver: self.driver.quit()
                break

if __name__ == "__main__":
    VintedProBot().run_menu()