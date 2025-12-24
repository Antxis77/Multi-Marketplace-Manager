# 🛒 Multi Marketplace Manager - v1.4

**Multi Marketplace Manager** est un outil d'automatisation professionnel conçu pour la gestion et la sauvegarde d'inventaires sur Vinted. La version 1.4 marque un tournant majeur dans la furtivité en remplaçant les actions mécaniques par des **simulations comportementales humaines**.

---

## 🚀 Nouveautés de la v1.4

### 🧠 Simulation du Comportement Humain (Nouveau)

* **Mouse Pathing (ActionChains)** : Le curseur ne "téléporte" plus sur les boutons. Le bot simule des mouvements de souris fluides vers les champs de saisie avant d'interagir.
* **Scroll Progressif & Aléatoire** : Remplacement du défilement instantané par un scroll par paliers irréguliers, simulant un utilisateur qui consulte ses annonces ou lit une description.
* **Micro-Pauses Cognitives** : Ajout de temps d'attente aléatoires entre chaque action (frappe, clic, upload) pour casser la régularité détectable par les algorithmes.

### 🛡️ Sécurité Renforcée

* **Antidétection Hardware** : Désactivation du WebGL et masquage des empreintes GPU pour limiter le *Canvas Fingerprinting*.
* **Isolation Totale** : Chaque compte possède son propre dossier de profil Chrome, ses propres cookies et son propre cache, rendant les comptes indépendants les uns des autres.
* **Langue & User-Agent** : Forçage des paramètres de navigation en `fr-FR` pour garantir une cohérence parfaite avec l'adresse IP de connexion.

### 📊 Optimisation de l'Inventaire

* **Tri Antéchronologique** : Les nouveaux articles scannés sont désormais ajoutés **en haut** du fichier CSV. Vos articles les plus récents sont toujours les premiers accessibles.
* **Sync Miroir Intelligente** : Nettoyage automatique du stock local si un article est supprimé ou vendu sur la plateforme.

---

## 🛠 Installation

1. **Cloner le projet**

```bash
git clone https://github.com/Antxis77/multi-marketplace-manager.git
cd multi-marketplace-manager

```

2. **Installer les dépendances**

```bash
pip install undetected-chromedriver requests

```

3. **Configuration**
Vérifiez que Google Chrome est installé. Le script générera un fichier `config.txt` au premier lancement pour mémoriser vos préférences (Chemin Chrome, ID Membre, etc.).

---

## 📖 Utilisation

Lancez le script avec :

```bash
python main.py

```

### Le Menu :

* **`0` 🔑 Connexion / Chrome** : Ouvre une session pour vous connecter manuellement et stabiliser les cookies.
* **`1` 🚮 Reset Scan** : Efface tout et reconstruit l'inventaire complet (Plus récent en haut).
* **`2` 🔄 Scan Nouveau** : Ajoute uniquement les pépites récemment postées sans toucher au reste.
* **`3` 🚀 Republier les X derniers** : Automatisé avec mouvements de souris humains sur les articles en haut de liste.
* **`4` 📤 Republier par ID** : Pour cibler précisément une pièce de votre stock.
* **`P` 📍 Paramètres** : Modifiez à la volée le chemin de Chrome ou le nom de votre fichier CSV.

---

## 📁 Structure des dossiers

* `vinted_backup/{ID_MEMBRE}/` : Vos photos et le fichier `inventaire.csv`.
* `chrome_profile/{ID_MEMBRE}/` : Données de navigation isolées (très important pour l'anti-ban).

---

## ⚠️ Conseils de "Survie" (Anti-Ban)

Pour maximiser la longévité de vos comptes avec la v1.4 :

1. **IP Tournante** : Utilisez un partage de connexion mobile. Activez le **mode avion** quelques secondes entre chaque changement de compte pour renouveler votre adresse IP.
2. **Volume Raisonnable** : Ne republiez pas 50 articles d'un coup. Procédez par vagues de 10 à 15 articles.
3. **Préchauffage** : Après une connexion sur un nouveau profil, naviguez 2-3 minutes manuellement (option 0) avant de lancer un scan.

---

*Développé pour un usage éducatif et personnel. Respectez les conditions d'utilisation de la plateforme.*

---