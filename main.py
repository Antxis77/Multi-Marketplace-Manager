import os
import time
import random
import shutil
import csv
import requests
import select
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ANONYME ---
def get_config_id():
    """Récupère l'ID depuis config.txt ou utilise 1 par défaut pour l'anonymat"""
    if not os.path.exists("config.txt"):
        with open("config.txt", "w") as f: 
            f.write("ID_MEMBRE=1") # ID par défaut anonyme
        return "1"
    with open("config.txt", "r") as f:
        for line in f:
            if "ID_MEMBRE" in line: 
                return line.split("=")[1].strip()
    return "1"

BACKUP_DIR = os.path.abspath("vinted_backup")

class VintedProBot:
    def __init__(self):
        self.driver = None
        self.member_id = get_config_id()

    def start_driver(self):
        if not self.driver:
            print(f"🚀 Lancement de Chrome...")
            options = uc.ChromeOptions()
            options.add_argument("--user-data-dir=" + os.path.abspath("chrome_profile"))
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            options.add_argument("--window-size=1920,1080")
            self.driver = uc.Chrome(options=options, use_subprocess=True)

    def robust_fill(self, element, text):
        """Méthode hybride Injection JS + Simulation Keyboard pour React"""
        try:
            text_clean = text.replace('"', '\\"').replace('\n', '\\n')
            self.driver.execute_script(f"""
                var el = arguments[0];
                el.value = "{text_clean}";
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, element)
            element.send_keys(Keys.SPACE)
            time.sleep(0.1)
            element.send_keys(Keys.BACKSPACE)
        except Exception as e:
            print(f"⚠️ Erreur remplissage : {e}")

    def fill_vinted_form(self, item):
        try:
            print(f"\n📢 Préparation : {item['Titre'][:40]}...")
            self.driver.get("https://www.vinted.fr/items/new")
            
            # 1. Photos
            print("📸 Envoi des photos...")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))).send_keys("\n".join(item['Images'].split(";")))
            print("⏳ Chargement des images (15s)...")
            time.sleep(15)

            # 2. Titre
            print("📝 Saisie du titre...")
            title_input = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.ID, "title")))
            self.robust_fill(title_input, item['Titre'])

            # 3. Description
            print("📝 Saisie de la description...")
            desc_input = self.driver.find_element(By.ID, "description")
            self.robust_fill(desc_input, item['Description'])

            # 4. Prix
            print("💰 Saisie du prix...")
            price_clean = "".join(c for c in item['Prix'] if c.isdigit() or c == '.')
            price_input = self.driver.find_element(By.NAME, "price")
            price_input.clear()
            price_input.send_keys(price_clean)
            
            print("\n✨ Formulaire complété !")
            input("✅ Publiez sur Chrome, puis appuyez sur ENTRÉE ici...")
            return True
        except Exception as e:
            print(f"⚠️ Erreur : {e}")
            return False

    def login_manual(self):
        self.start_driver()
        self.driver.get("https://www.vinted.fr")
        input("✅ Connectez-vous et appuyez sur ENTRÉE...")

    def publish_by_id(self, item_id):
        csv_path = os.path.join(BACKUP_DIR, "inventaire.csv")
        if not os.path.exists(csv_path):
            print("❌ Inventaire absent (Option 1 ou 2 requise)"); return
        with open(csv_path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if item_id in row['URL']:
                    self.fill_vinted_form(row)
                    return
        print(f"❌ ID {item_id} non trouvé dans l'inventaire.")

    def wait_with_bypass(self, minutes):
        print(f"⏳ Attente {minutes}m. [Entrée] pour passer.")
        for i in range(minutes * 60, 0, -1):
            sys.stdout.write(f"\r⏳ {i//60:02d}:{i%60:02d} "); sys.stdout.flush()
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline(); return
            time.sleep(1)

    def republication_expert(self, count):
        csv_path = os.path.join(BACKUP_DIR, "inventaire.csv")
        with open(csv_path, 'r', encoding='utf-8') as f:
            annonces = list(csv.DictReader(f))[-count:]
        for item in annonces:
            self.driver.get(item['URL']); input(f"🗑️ Supprimez '{item['Titre'][:20]}' et Entrée...")
        self.wait_with_bypass(15)
        for item in annonces: self.fill_vinted_form(item)

    def save_process(self, urls, reset=False):
        if reset and os.path.exists(BACKUP_DIR): shutil.rmtree(BACKUP_DIR)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        csv_path = os.path.join(BACKUP_DIR, "inventaire.csv")
        history = self.get_already_scrapped_urls() if not reset else []
        with open(csv_path, 'a' if not reset else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if reset or not os.path.exists(csv_path):
                writer.writerow(["Titre", "Prix", "Description", "Images", "URL", "Date_Ajout"])
            for i, url in enumerate(urls):
                if url in history: continue
                data = self.scrap_item(url, os.path.join(BACKUP_DIR, f"item_{int(time.time())}_{i}"))
                if data:
                    writer.writerow([data['title'], data['price'], data['description'], ";".join(data['images']), url, data['date']])
                    f.flush(); print(f"✨ Sauvegardé : {data['title'][:25]}")

    def scrap_item(self, url, folder):
        try:
            self.driver.get(url); time.sleep(6)
            data = {'url': url, 'title': self.driver.title.split('|')[0].strip()}
            els = self.driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
            data['price'] = "".join(filter(lambda x: x.isdigit() or x in ",.", els[0].text)) if els else "0"
            desc = self.driver.find_elements(By.XPATH, "//div[@itemprop='description']")
            data['description'] = desc[0].text.strip() if desc else ""
            data['date'] = "Aujourd'hui"
            imgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'item-photo')]//img")
            img_urls = list(set([i.get_attribute('src') for i in imgs if i.get_attribute('src')]))
            data['images'] = self.download_images(img_urls, folder)
            return data
        except: return None

    def download_images(self, img_urls, folder):
        os.makedirs(folder, exist_ok=True); paths = []
        for i, url in enumerate(img_urls):
            try:
                r = requests.get(url); p = os.path.join(folder, f"img_{i}.jpg")
                with open(p, 'wb') as f: f.write(r.content)
                paths.append(os.path.abspath(p))
            except: pass
        return paths

    def get_already_scrapped_urls(self):
        csv_path = os.path.join(BACKUP_DIR, "inventaire.csv")
        if not os.path.exists(csv_path): return []
        with open(csv_path, 'r', encoding='utf-8') as f:
            return [row['URL'] for row in csv.DictReader(f)]

    def get_items_urls(self):
        self.driver.get(f"https://www.vinted.fr/member/{self.member_id}"); time.sleep(5)
        items = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/items/')]")
        return list(dict.fromkeys([i.get_attribute('href') for i in items if i.get_attribute('href')]))

    def run_menu(self):
        while True:
            print("\n" + "═"*50)
            print(f"   VINTED PRO MANAGER V1")
            print(f"   ID Actuel : {self.member_id}")
            print("═"*50)
            print(" 0. 🔑 Connexion à Vinted")
            print(" 1. 🚮 Reset complet (Re-scrapper tout)")
            print(" 2. 🔄 Scan nouvelles annonces uniquement")
            print(" 3. 🚀 Republier les X dernières")
            print(" 4. 📤 Remettre en ligne par ID")
            print(" Q. ❌ Quitter le programme")
            print("─"*50)
            
            c = input(" Votre choix : ").upper()
            if c == "0": self.login_manual()
            elif c == "1": self.start_driver(); self.save_process(self.get_items_urls(), True)
            elif c == "2": self.start_driver(); self.save_process(self.get_items_urls(), False)
            elif c == "3": 
                val = input(" Nombre d'articles ? : ")
                if val.isdigit(): self.start_driver(); self.republication_expert(int(val))
            elif c == "4": 
                item_id = input(" Entrez l'ID de l'article : ").strip()
                self.start_driver(); self.publish_by_id(item_id)
            elif c in ["Q", "QUITTER"]: break

if __name__ == "__main__":
    VintedProBot().run_menu()