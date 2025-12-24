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
from selenium.webdriver.common.action_chains import ActionChains

# --- GESTION DE LA CONFIGURATION ---
def get_config():
    if platform.system() == "Windows":
        default_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:
        default_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    config = {
        "ID_MEMBRE": "1", 
        "CHROME_PATH": default_path,
        "CHROME_VERSION": "0",
        "CSV_NAME": "inventaire"
    }
    
    if os.path.exists("config.txt"):
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    else:
        save_config(config["ID_MEMBRE"], config["CHROME_PATH"], config["CHROME_VERSION"], config["CSV_NAME"])
    return config

def save_config(member_id, chrome_path, chrome_version, csv_name):
    with open("config.txt", "w", encoding="utf-8") as f:
        f.write(f"ID_MEMBRE={member_id}\n")
        f.write(f"CHROME_PATH={chrome_path}\n")
        f.write(f"CHROME_VERSION={chrome_version}\n")
        f.write(f"CSV_NAME={csv_name}\n")

class VintedProBot:
    def __init__(self):
        self.driver = None
        self.load_account_config()

    def load_account_config(self):
        config = get_config()
        self.member_id = config["ID_MEMBRE"]
        self.chrome_path = config["CHROME_PATH"]
        self.chrome_version = int(config["CHROME_VERSION"])
        self.csv_filename = f"{config.get('CSV_NAME', 'inventaire')}.csv"
        
        self.base_dir = os.path.abspath(f"vinted_backup/{self.member_id}")
        self.profile_dir = os.path.abspath(f"chrome_profile/{self.member_id}")
        self.csv_path = os.path.join(self.base_dir, self.csv_filename)
        
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.profile_dir, exist_ok=True)
        
        if self.driver:
            self.driver.quit()
            self.driver = None

    def display_info(self):
        print("\n" + "─"*55)
        print("📊 PARAMÈTRES CHARGÉS :")
        print(f"🔹 OS              : {platform.system()} {platform.release()}")
        print(f"🔹 ID Vinted      : {self.member_id}")
        print(f"🔹 Fichier Stock  : {self.csv_filename}")
        print(f"🔹 Version Chrome : {self.chrome_version if self.chrome_version > 0 else 'Auto-détection'}")
        print(f"🔹 Chemin Chrome  : {self.chrome_path}")
        print("─"*55)

    # --- NOUVELLES FONCTIONS DE COMPORTEMENT HUMAIN ---
    def human_scroll(self):
        """Scroll progressif simulant une lecture humaine."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current_pos = 0
        while current_pos < last_height:
            # Scroll par bonds aléatoires entre 300 et 700 pixels
            step = random.randint(300, 700)
            current_pos += step
            self.driver.execute_script(f"window.scrollTo(0, {current_pos});")
            time.sleep(random.uniform(0.6, 1.4))
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            if current_pos > last_height: break

    def human_mouse_move(self, element):
        """Simule un mouvement de souris vers un élément avant d'agir."""
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.3, 0.8))
            actions.perform()
        except:
            pass

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
        except:
            return now.strftime("%d-%m-%Y")

    def start_driver(self):
        if not self.driver:
            print(f"🚀 Lancement Chrome | Profil : {self.member_id}")
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--disable-webgl')
            options.add_argument('--lang=fr-FR')

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
        # Utilisation du mouvement de souris avant d'écrire
        self.human_mouse_move(element)
        self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
        element.send_keys(Keys.SPACE + Keys.BACKSPACE)
        time.sleep(random.uniform(0.5, 1.0))

    def extract_id(self, url):
        match = re.search(r'/items/(\d+)', url)
        return match.group(1) if match else "Inconnu"

    def sync_cleanup(self, online_urls):
        if not os.path.exists(self.csv_path): return
        print(f"🧹 Nettoyage de l'inventaire ({self.csv_filename})...")
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
            
            # Attendre et simuler mouvement vers l'upload
            file_btn = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_btn.send_keys("\n".join(item['Images'].split(";")))
            
            time.sleep(7) 
            self.fast_copy_paste(self.driver.find_element(By.ID, "title"), item['Titre'])
            time.sleep(1.5)
            self.fast_copy_paste(self.driver.find_element(By.ID, "description"), item['Description'])
            time.sleep(1.5)
            
            price_el = self.driver.find_element(By.NAME, "price")
            self.human_mouse_move(price_el) # Mouvement souris vers prix
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
        print(f"🔍 Accès au profil membre {self.member_id}...")
        self.driver.get(f"https://www.vinted.fr/member/{self.member_id}")
        time.sleep(5)
        
        # Remplacement du scroll brut par le scroll humain
        self.human_scroll()
        
        items = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/items/')]")
        urls = list(dict.fromkeys([i.get_attribute('href') for i in items if i.get_attribute('href')]))
        
        print(f"✅ Scan terminé : {len(urls)} annonce(s) trouvée(s).")
        self.sync_cleanup(urls)
        return urls

    def save_process(self, urls, reset=False):
        if reset and os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir); os.makedirs(self.base_dir)
        
        existing_rows = []
        history_urls = []
        fieldnames = ["Titre", "Prix", "Description", "Images", "URL", "Date_Ajout"]

        if not reset and os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_rows = list(reader)
                history_urls = [row['URL'] for row in existing_rows]

        new_entries = []
        for i, url in enumerate(urls):
            if url in history_urls: continue
            print(f"📦 Scraping {i+1}/{len(urls)}... ID: {self.extract_id(url)}")
            time.sleep(random.uniform(6.0, 12.0))
            self.driver.get(url)
            
            # Petit scroll humain aléatoire sur la page de l'article pour simuler une lecture
            if random.choice([True, False]):
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)});")
            
            try:
                title = self.driver.title.split('|')[0].strip()
                price = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")[0].text
                desc = self.driver.find_element(By.XPATH, "//div[@itemprop='description']").text
                
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
                
                new_entries.append({
                    "Titre": title, "Prix": price, "Description": desc, 
                    "Images": ";".join(img_list), "URL": url, "Date_Ajout": real_date
                })
            except: continue

        if new_entries or reset:
            final_data = new_entries + ([] if reset else existing_rows)
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(final_data)
            print(f"💾 {len(new_entries)} nouvel(s) article(s) ajouté(s) en haut du fichier.")

    def run_menu(self):
        while True:
            self.display_info()
            print("\n" + "═"*55)
            print(f"   VINTED PRO v1.4 | COMPTE : {self.member_id}")
            print("═"*55)
            print(" 0. 🔑 Connexion / Chrome")
            print(" 1. 🚮 Reset Scan (Tout refaire + Sync)")
            print(" 2. 🔄 Scan Nouveau (Ajouter + Sync)")
            print(" 3. 🚀 Republier les X derniers")
            print(" 4. 📤 Republier par ID article")
            print(" C. 👤 Changer de Compte")
            print(" P. 📍 Paramètres (Chemin, Version, Fichier)")
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
                    config = get_config()
                    save_config(new_id, self.chrome_path, self.chrome_version, config.get('CSV_NAME', 'inventaire'))
                    self.load_account_config()
                    print(f"✅ Compte basculé sur : {self.member_id}")
            elif c == "P":
                config = get_config()
                print(f"\n1. Chemin : {self.chrome_path}\n2. Version : {self.chrome_version}\n3. Nom CSV : {config.get('CSV_NAME', 'inventaire')}")
                opt = input("Modifier (1/2/3) : ")
                if opt == "1": self.chrome_path = input("Nouveau chemin : ").strip()
                elif opt == "2": self.chrome_version = input("Version majeure : ").strip()
                elif opt == "3": config['CSV_NAME'] = input("Nouveau nom CSV (sans .csv) : ").strip()
                save_config(self.member_id, self.chrome_path, self.chrome_version, config.get('CSV_NAME', 'inventaire'))
                self.load_account_config()
            elif c == "Q":
                if self.driver: self.driver.quit()
                break

if __name__ == "__main__":
    VintedProBot().run_menu()