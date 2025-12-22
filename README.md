# 🛒 Vinted Pro Bot - v1.1

**Vinted Pro Bot** est un outil d'automatisation puissant conçu pour les vendeurs Vinted souhaitant gérer leur inventaire et optimiser leurs ventes. Il permet de sauvegarder l'intégralité d'un dressing (images, descriptions, prix) et facilite la republication pour booster la visibilité des articles.

---

## 🚀 Fonctionnalités Clés

### 📦 Gestion d'Inventaire

* **Scan Intégral** : Grâce au défilement automatique (*Auto-Scroll*), le bot récupère 100% de vos annonces, même les plus anciennes cachées par le chargement dynamique.
* **Calcul de Date Réel** : Le bot convertit les textes de type "Il y a 3 semaines" en dates précises (ex: `01-12-2025`) dans votre fichier CSV.
* **Sauvegarde Locale** : Téléchargement automatique de toutes les images et des données dans des dossiers organisés par ID membre.

### 🔄 Republication Simplifiée

* **Flux Accéléré** : Temps de chargement des photos optimisé à **5 secondes**.
* **Nettoyage Automatique** : Une fois republié, l'article est retiré du CSV. Un nouveau "Scan" le rajoutera avec sa nouvelle date de mise à jour.
* **Rotation Intelligente** : Possibilité de republier les "X derniers" articles ajoutés à l'inventaire.

### 👥 Multi-Compte (Nouveau en V1.1)

* **Isolation Totale** : Chaque compte possède son propre historique et sa propre session Chrome (évite les déconnexions intempestives).
* **Changement Rapide** : Basculez entre vos différents profils directement depuis le menu.

---

## 🛠 Installation

1. **Cloner le projet**
```bash
git clone https://github.com/votre-utilisateur/vinted-pro-bot.git
cd vinted-pro-bot

```


2. **Installer les dépendances**
```bash
pip install undetected-chromedriver requests

```


3. **Configurer Chrome**
Vérifiez que Google Chrome est installé sur votre machine. Le script est configuré par défaut pour macOS (`/Applications/Google Chrome.app/...`). *Si vous êtes sur Windows, modifiez le chemin `binary_location` dans le script.*

---

## 📖 Utilisation

Lancez le script avec :

```bash
python main.py

```

### Le Menu :

* **`0` 🔑 Connexion / Chrome** : Ouvre une instance Chrome avec votre session sauvegardée.
* **`1` 🚮 Reset Scan** : Efface tout l'historique local et rescane tout le dressing.
* **`2` 🔄 Scan Nouveau** : Ajoute uniquement les nouveaux articles détectés sur votre profil.
* **`3` 🚀 Republier les X derniers** : Aide à la republication manuelle assistée des dernières annonces du CSV.
* **`4` 📤 Republier par ID** : Publie un article spécifique via une partie de son URL.
* **`C` 👤 Changer de Compte** : Saisissez un nouvel ID Vinted pour changer de dossier de travail.
* **`Q` ❌ Quitter** : Ferme proprement le bot et le navigateur.

---

## 📁 Structure des fichiers

* `vinted_backup/{ID_MEMBRE}/` : Contient vos images et le fichier `inventaire.csv`.
* `chrome_profile/{ID_MEMBRE}/` : Stocke vos cookies de connexion Vinted (ne pas partager).
* `config.txt` : Mémorise le dernier ID membre utilisé.

---

## ⚠️ Avertissement

Cet outil est destiné à un usage personnel uniquement. L'automatisation peut aller à l'encontre des conditions d'utilisation de Vinted. Utilisez-le de manière responsable avec des délais raisonnables.

---
