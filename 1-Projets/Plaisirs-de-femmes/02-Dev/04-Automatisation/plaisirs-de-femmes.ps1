# ================================
#  Starter Vault Obsidian – plaisirs-de-femmes.fr
#  Génération automatique du vault complet
# ================================

$root = "plaisirs-de-femmes-vault"

# --- Création des dossiers ---
$folders = @(
    "$root/01-Plan",
    "$root/02-Dev/01-Specs",
    "$root/02-Dev/02-Scripts",
    "$root/02-Dev/03-Tests",
    "$root/02-Dev/04-Automatisation",
    "$root/02-Dev/05-PrestaShop",
    "$root/02-Dev/06-StoreCommander",
    "$root/02-Dev/07-Erreurs",
    "$root/02-Dev/99-Archives",
    "$root/03-SEO/Categories",
    "$root/03-SEO/Clusters",
    "$root/03-SEO/Pages-Piliers",
    "$root/04-Produits/01-Fiches-Produits",
    "$root/04-Produits/02-Photos",
    "$root/04-Produits/03-Descriptions",
    "$root/04-Produits/04-Variantes",
    "$root/04-Produits/05-Imports-Exports",
    "$root/04-Produits/06-Analyses",
    "$root/05-Design",
    "$root/06-IA/Conversations",
    "$root/06-IA/Prompts",
    "$root/06-IA/Workflows",
    "$root/99-Archives"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# --- Fonction pour créer un fichier avec contenu ---
function Write-File($path, $content) {
    $content | Out-File -FilePath $path -Encoding UTF8 -Force
}

# ================================
#  BLOC 2 — 01-PLAN
# ================================

Write-File "$root/01-Plan/Vision.md" @"
# 🌟 Vision – plaisirs-de-femmes.fr
…
"@

Write-File "$root/01-Plan/Objectifs.md" @"
# 🎯 Objectifs – plaisirs-de-femmes.fr
…
"@

Write-File "$root/01-Plan/Roadmap.md" @"
# 🗺️ Roadmap – plaisirs-de-femmes.fr
…
"@

Write-File "$root/01-Plan/Structure-catalogue.md" @"
# 🧱 Structure du catalogue
…
"@

Write-File "$root/01-Plan/Univers-et-categories.md" @"
# 🌸 Univers & Catégories
…
"@

Write-File "$root/01-Plan/Branding.md" @"
# 🎨 Branding
…
"@

Write-File "$root/01-Plan/Personas.md" @"
# 👩 Personas
…
"@

Write-File "$root/01-Plan/Strategie-IA.md" @"
# 🤖 Stratégie IA
…
"@

Write-File "$root/01-Plan/Journal-de-projet.md" @"
# 📓 Journal de projet
…
"@
# ================================
#  BLOC 3 — 02-DEV
# ================================

# SPEC
Write-File "$root/02-Dev/01-Specs/Template - Spec.md" @"
# 📄 Spec – {{title}}
…
"@

# SCRIPT
Write-File "$root/02-Dev/02-Scripts/Template - Script.md" @"
# 🧩 Script – {{title}}
…
"@

# TEST
Write-File "$root/02-Dev/03-Tests/Template - Test.md" @"
# 🧪 Test – {{title}}
…
"@

# AUTOMATISATION
Write-File "$root/02-Dev/04-Automatisation/Template - Automatisation.md" @"
# ⚙️ Automatisation – {{title}}
…
"@

# PRESTASHOP
Write-File "$root/02-Dev/05-PrestaShop/Template - PrestaShop.md" @"
# 🛒 PrestaShop – {{title}}
…
"@

# STORECOMMANDER
Write-File "$root/02-Dev/06-StoreCommander/Template - StoreCommander.md" @"
# 📦 StoreCommander – {{title}}
…
"@

# ERREUR
Write-File "$root/02-Dev/07-Erreurs/Template - Erreur.md" @"
# ❌ Erreur – {{title}}
…
"@
# ================================
#  BLOC 4 — 03-SEO
# ================================

# STRATEGIE SEO
Write-File "$root/03-SEO/Strategie-SEO.md" @"
# 🔍 Stratégie SEO – plaisirs-de-femmes.fr
…
"@

# CATEGORIE SEO
Write-File "$root/03-SEO/Categories/Template - Catégorie SEO.md" @"
# 🌸 Catégorie – {{Nom}}
…
"@

# CLUSTER SEO
Write-File "$root/03-SEO/Clusters/Template - Cluster SEO.md" @"
# 🌐 Cluster SEO – {{Nom}}
…
"@

# PAGE PILIER
Write-File "$root/03-SEO/Pages-Piliers/Template - Page Pilier SEO.md" @"
# 🏛️ Page Pilier – {{Nom}}
…
"@
# ================================
#  BLOC 5 — 04-PRODUITS
# ================================

# FICHE PRODUIT
Write-File "$root/04-Produits/01-Fiches-Produits/Template - Fiche Produit.md" @"
# 🧩 Produit – {{Nom}}
…
"@

# DESCRIPTION PRODUIT SEO
Write-File "$root/04-Produits/03-Descriptions/Template - Description Produit SEO.md" @"
# ✍️ Description SEO – {{Nom}}
…
"@

# ANALYSE PRODUIT
Write-File "$root/04-Produits/06-Analyses/Template - Analyse Produit.md" @"
# 🔍 Analyse Produit – {{Nom}}
…
"@
# ================================
#  BLOC 6 — 05-DESIGN
# ================================

Write-File "$root/05-Design/Identité-visuelle.md" @"
# 🎨 Identité visuelle
…
"@

Write-File "$root/05-Design/Moodboard.md" @"
# 🖼️ Moodboard
…
"@

Write-File "$root/05-Design/Inspirations.md" @"
# 💡 Inspirations
…
"@
# ================================
#  BLOC 7 — 06-IA
# ================================

Write-File "$root/06-IA/Conversations/Conversation - Template.md" @"
# 💬 Conversation IA – {{date}}
…
"@

Write-File "$root/06-IA/Prompts/Prompt - Template.md" @"
# 🎯 Prompt – {{title}}
…
"@

Write-File "$root/06-IA/Workflows/Workflow IA - Template.md" @"
# 🤖 Workflow IA – {{title}}
…
"@
# ================================
#  BLOC 8 — 99-ARCHIVES
# ================================

# (Dossier vide, rien à écrire)


Write-Host "Vault généré avec succès dans: $root"
