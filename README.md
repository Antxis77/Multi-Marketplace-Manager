# 🛒 Multi Marketplace Manager - v1.2

![Version](https://img.shields.io/badge/version-1.2-blue.svg)
![Safety](https://img.shields.io/badge/security-anti--detection-orange.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

**Multi Marketplace Manager** (anciennement Vinted Pro Bot) est un outil d'automatisation puissant conçu pour les vendeurs souhaitant centraliser la gestion de leur inventaire. Il permet de sauvegarder l'intégralité d'un dressing (images, descriptions, prix) et facilite la republication pour booster la visibilité.

---

## 🚀 Fonctionnalités Clés

### 🛡️ Sécurité & Anti-Détection (Nouveau v1.2)
* **Bypass Avancé** : Masquage des signatures d'automatisation (`AutomationControlled`) et du flag `webdriver` au sein du navigateur.
* **User-Agent Spoofing** : Simule une navigation réelle sous macOS/Chrome pour éviter les blocages de type "comportement inhabituel".
* **Humane-Typing & Injection JS** : Mélange de frappe clavier réelle (pour le prix) et d'injection JavaScript (pour les titres et descriptions) afin de supporter 100% des **emojis** sans erreur.

### 📦 Gestion d'Inventaire & Sync Miroir
* **Synchronisation Automatique** : Lors d'un scan, le bot détecte les articles vendus ou supprimés sur Vinted et les retire automatiquement de votre fichier `inventaire.csv`.
* **Scan Intégral** : Récupération de 100% des annonces via un défilement intelligent (*Auto-Scroll*) qui force le chargement dynamique.
* **Sauvegarde Organisée** : Téléchargement des données et images dans des dossiers structurés et isolés par ID membre.

### 🔄 Republication Intelligente
* **Rappel d'ID** : Affichage systématique de l'ID de l'article en cours de traitement dans la console pour un suivi précis.
* **Nettoyage Post-Publication** : Retrait immédiat de l'article du CSV après validation pour éviter les doublons accidentels.
* **Gestion Multi-Compte** : Isolation complète des cookies, du cache et de l'historique par utilisateur.

---

## 🛠 Installation

1. **Cloner le projet**
```bash
git clone [https://github.com/votre-utilisateur/multi-marketplace-manager.git](https://github.com/votre-utilisateur/multi-marketplace-manager.git)
cd multi-marketplace-manager
```

Installer les dépendances

```bash

pip install undetected-chromedriver requests
```

Configurer Chrome Vérifiez que Google Chrome est installé.

Note : Sur macOS, le chemin est détecté automatiquement. Sur Windows, veillez à modifier le chemin binary_location dans le code source pour pointer vers votre chrome.exe.

📖 Utilisation
Lancez le script avec :

```bash

python main.py

```
Le Menu :

  0 🔑 Connexion / Chrome : Recommandé avant toute action. Ouvre Chrome pour vous connecter. Naviguez manuellement quelques secondes pour valider les cookies.

  1 🚮 Reset Scan : Efface l'historique local, synchronise le stock actuel et rescane l'intégralité du dressing.

  2 🔄 Scan Nouveau : Met à jour l'inventaire : ajoute les nouveaux articles et retire ceux qui ne sont plus en ligne.

  3 🚀 Republier les X derniers : Lance la procédure assistée pour les articles les plus récents de votre fichier.

  4 📤 Republier par ID : Cible un article spécifique via son identifiant unique Vinted.

  C 👤 Changer de Compte : Bascule instantanément sur un autre ID membre (crée un nouveau dossier dédié).

  Q ❌ Quitter : Ferme proprement les sessions Chrome et le script.

📁 Structure des fichiers

vinted_backup/{ID_MEMBRE}/ : Contient les sous-dossiers d'images et le fichier inventaire.csv.

chrome_profile/{ID_MEMBRE}/ : Stocke les cookies et sessions isolées pour chaque compte.

config.txt : Fichier système mémorisant le dernier ID utilisé.

⚠️ Avertissement & Conseils de sécurité
Cet outil est destiné à un usage personnel uniquement. Pour éviter les détections :

Utilisez une IP mobile (partage de connexion 4G/5G) si vous avez un grand volume d'articles.

Espacez vos actions : Évitez de republier plus de 10 articles à la suite sans pause.

Comportement humain : Utilisez régulièrement l'option 0 pour effectuer quelques actions manuelles (liker un article, faire une recherche).
