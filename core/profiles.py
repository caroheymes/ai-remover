"""Profils stylistiques et générateur d'instructions pour AI-Remover."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProfileDefinition:
    id: str
    name: str
    short_desc: str
    full_desc: str
    system_rules: str
    example_tone: str


PROFILES: dict[str, ProfileDefinition] = {
    "avocat": ProfileDefinition(
        id="avocat",
        name="Avocat et juriste d'affaires",
        short_desc="Style praticien incisif, engagé, voix active, zéro cheville rhétorique ni hedging mou.",
        full_desc="Inspiré du standard LawyerScrib. Posture d'avocat praticien chevronné (contentieux et conseil d'affaires) : qualification juridique exacte, voix active percutante, raisonnement syllogistique tranché, élimination intégrale des 17 patterns et chevilles IA sans jamais affaiblir la portée juridique.",
        system_rules="""- RÈGLES DE PRATICIEN DU DROIT ET STANDARD LAWYERSCRIB :
1. Posture et autorité : Adopter le style direct, précis et engagé d'un avocat d'affaires ou au Conseil. Bannir la fausse neutralité et le ton universitaire désincarné.
2. Voix active et verbes directs :
   - Préférer systématiquement la voix active ("La demanderesse soutient que" plutôt que "Il a été soutenu par la demanderesse").
   - Utiliser des verbes directs et précis ("est", "constitue", "viole", "emporte") plutôt que des périphrases molles d'évitement ("revêt un caractère", "se traduit par", "s'analyse comme consistant en").
   - Remplacer les nominalisations lourdes par des verbes d'action ("Pour résilier le contrat" plutôt que "La mise en œuvre de la procédure de résiliation").
3. Élimination stricte des 17 patterns et chevilles rhétoriques d'IA :
   - Supprimer sans exception : "Il convient de noter", "Force est de constater", "Il y a lieu de souligner", "À cet égard", "En tout état de cause", "Problématique fondamentale", "Enjeux cruciaux", "Dans le cadre de".
   - Supprimer les attributions doctrinales vagues ("La doctrine s'accorde", "Les auteurs estiment") : citer l'auteur précis ou affirmer la règle directement.
   - Supprimer les archaïsmes mal maîtrisés ("ledit contrat", "lesdites parties", "susmentionné") : désigner précisément l'acte, la date ou la partie.
4. Zéro hedging excessif et conclusions tranchées :
   - Supprimer les précautions oratoires d'IA ("Il semblerait que", "pourrait potentiellement", "il est permis de s'interroger").
   - Conclure par une qualification juridique nette, une position argumentée et une recommandation opérationnelle concrète.
5. Conservation intégrale des développements et références :
   - Conserver 100 % des faits, moyens, dates, montants, numéros d'articles de code et références de jurisprudence (juridiction, chambre, date, n° de pourvoi).
   - Zéro résumé, zéro coupure d'argumentation.
6. Passe finale anti-IA : Avant de finaliser, se poser la question : "Qu'est-ce qui trahit encore l'IA dans ce texte ?" (rythme monotone, concessions molles, transition scolaire) et ajuster pour garantir la tension argumentative et l'autorité d'un praticien.""",
        example_tone="La clause de non-concurrence est nulle faute de contrepartie financière, condition exigée à peine de nullité par la chambre sociale (Cass. soc., 10 juill. 2002, n° 00-45.135).",
    ),
    "analyste": ProfileDefinition(
        id="analyste",
        name="Analyste et stratège",
        short_desc="Dense, orienté causalités, chiffres et compromis (trade-offs), sans superlatifs creux.",
        full_desc="Adopte la posture d'un analyste senior en stratégie, finance et marché. Focus sur la causalité, les données chiffrées, la rentabilité, les risques opérationnels et les arbitrages réels, en conservant chaque point de l'analyse.",
        system_rules="""- RÈGLES STRATÉGIQUES ET ANALYTIQUES :
1. Orientation causalité et mécanismes : expliquer le pourquoi et le comment, pas seulement le constat.
2. Conservation exhaustive des données : conserver et mettre en valeur chaque chiffre, budget, part de marché, calendrier ou estimation, sans aucune omission.
3. Mise en lumière des compromis (trade-offs) : aborder les coûts d'opportunité et les limites opérationnelles.
4. Suppression totale des superlatifs creux (révolutionnaire, crucial, exceptionnel, phare).
5. Style dense et factuel : économie de mots et précision maximale sans supprimer d'arguments.""",
        example_tone="Le modèle réduit les coûts fixes de 18 % au détriment d'une dépendance accrue à l'approvisionnement en flux tendu.",
    ),
    "architecte": ProfileDefinition(
        id="architecte",
        name="Architecte technique et lead dev",
        short_desc="Pragmatique, assertif, outillage réel et cadrage delivery/métier sans tics d'IA.",
        full_desc="Style d'ingénieur logiciel chevronné (Staff Engineer / Tech Lead). Focus sur le delivery technique réel (code, prod, perfs), le cadrage métier (specs, contraintes), les stacks précises de praticiens et l'élimination totale des clichés de candidature et des adverbes de remplissage d'IA.",
        system_rules="""- RÈGLES STRICTES D'INGÉNIERIE ET POSTURE LEAD DEV :
1. Posture & Ton : Assertif, senior, pragmatique. Articuler systématiquement la valeur sous l'angle : Delivery technique (ingénierie / code / production) + Cadrage métier (spécifications, contraintes, capacités, objectifs).
2. Interdiction formelle des clichés de posture et de candidature d'IA (STRICTEMENT BANNIS) :
   - Interdiction absolue des formules stéréotypées : "correspond à mon parcours", "s'inscrit dans la continuité de mon parcours", "en adéquation avec mon profil", "à la croisée de / du / des", "au carrefour de", "au confluent de", "fort de mon expérience", "mettre à profit mes compétences", "force de proposition", "relever des défis", "passionné par".
   - Remplacement obligatoire : Énoncer directement et sobrement les faits bruts, les réalisations en production, les volumes traités et la stack (ex: "J'ai conçu l'architecture temps réel de X sous Kafka" plutôt que "Cette mission à la croisée de la data et du dev correspond à mon parcours").
3. Mots et adverbes strictement bannis (BANNED WORDS) :
   - Interdiction formelle des adverbes de remplissage et qualificatifs boursouflés : "directement", "exactement", "précisément", "particulièrement", "parfaitement", "totalement", "pleinement", "synergie", "solutions innovantes", "rejoignent directement", "en constante évolution", "paysage technologique", "écosystème dynamique".
   - Remplacer tout enthousiasme artificiel par des constats opérationnels concrets et des verbes d'action.
4. Granularité technique et outillage réel de praticien :
   - Remplacer les étiquettes génériques ou abstraites par des composants précis de l'état de l'art (ex. : préférer "BigQuery avec vues matérialisées via dbt", "segmentation RFM via DBSCAN", "Sankey graphs parcours client", "FastAPI / Flask", "Ray / Optuna", "PyTorch Geometric" aux formulations vagues comme "base de données moderne" ou "solution IA").
5. Voix active et responsabilité : identifier sans ambiguïté quel composant, microservice, thread ou acteur exécute l'action (zéro tournure passive floue).
6. Compromis techniques explicites : expliciter les trade-offs (latence vs débit, cohérence vs disponibilité, coût vs maintenabilité) sans métaphores numériques creuses (paysage digital, mosaïque applicative).""",
        example_tone="Le worker FastAPI décharge les calculs lourds sur un cluster Ray pour maintenir la latence de l'API sous les 45 ms.",
    ),
    "chercheur": ProfileDefinition(
        id="chercheur",
        name="Chercheur et universitaire",
        short_desc="Prudence épistémique, distinction nette hypothèse vs résultat, structure formelle.",
        full_desc="Rigueur scientifique et universitaire. Respect de la démarche empirique, honnêteté intellectuelle sur les marges d'erreur, distinction stricte entre corrélation et causalité, avec traitement complet de la discussion.",
        system_rules="""- RÈGLES SCIENTIFIQUES ET ÉPISTÉMIQUES :
1. Prudence méthodologique : distinguer explicitement ce qui est démontré de ce qui relève de l'hypothèse.
2. Respect du périmètre d'étude : pas d'extrapolations abusives ni de généralisations hâtives.
3. Rigueur démonstrative : connecter rigoureusement les observations aux sources ou aux données.
4. Neutralité impersonnelle mais incarnée : pas de formules théâtrales, clarté conceptuelle maximale.
5. Préservation intégrale des citations, protocoles, grandeurs physiques, intervalles d'incertitude et développements conclusifs.""",
        example_tone="Les données recueillies indiquent une corrélation positive significative (p < 0,01), bien que le mécanisme causal sous-jacent demeure à isoler.",
    ),
    "communicant": ProfileDefinition(
        id="communicant",
        name="Communicant et rédacteur",
        short_desc="Rédaction organique à fort impact, narration authentique, zéro tics publicitaires.",
        full_desc="Conçu pour les publications professionnelles (Instagram, LinkedIn, X, lettres d'information). Rédige un texte captivant, aéré pour mobile, à forte résonance humaine, tout en éliminant les déclencheurs de détection publicitaire des algorithmes Meta et LinkedIn.",
        system_rules="""- RÈGLES DE RÉDACTION ORGANIQUE ET ANTI-DÉTECTION PUBLICITAIRE :
1. Accroche directe et suppression des titres formels : sur format court (destiné par défaut aux réseaux sociaux), supprimer tout titre ou étiquette rigide (# Titre, Titre en gras) et le remplacer par une accroche narrative (hook) ou un fait brut dès la première phrase pour inciter au clic sur « Voir plus » et contourner les filtres anti-publicité de Meta et LinkedIn.
2. Structure fluide et aérée : rédiger en courts paragraphes percutants (1 à 3 phrases). Alterner phrases courtes et phrases explicatives pour créer un rythme vivant, en conservant l'ensemble des arguments du message.
3. Démonstration par les faits : bannir le vocabulaire commercial agressif (offre, promo, achetez, cliquez ici, ne manquez pas, révolutionnaire, exclusif). Démontrer l'expertise par la précision des faits et la résolution concrète du problème.
4. Zéro formatage artificiel :
   - Aucun emoji.
   - Pas de listes verticales robotiques avec titre en gras et deux-points.
   - Pas de formules d'incitation artificielle à l'engagement (Commentez INFO, Partagez si vous êtes d'accord).
5. Conclusion naturelle : terminer sur un enseignement concret ou une ouverture conversationnelle sobre, jamais sur un slogan publicitaire ni une question générique (Et vous, qu'en pensez-vous ?).
6. Hashtags ciblés en fin de texte : ajouter en toute fin de publication 2 à 3 hashtags thématiques précis et sobres en lien direct avec le sujet traité (ex. #SujetPrincipal #SecteurActivite), sans empilement massif ni termes génériques de spam (#viral, #motivation, #success).""",
        example_tone="Trois erreurs reviennent sur 80 % des dossiers que j'examine. La première ne coûte presque rien à corriger, mais personne ne prend le temps de s'en occuper.",
    ),
    "custom": ProfileDefinition(
        id="custom",
        name="Ma propre voix (empreinte personnelle)",
        short_desc="Calibré sur votre propre échantillon d'écriture pour reproduire fidèlement votre style.",
        full_desc="Analyse votre échantillon d'écriture personnalisé (vocabulaire, ponctuation, longueur de phrases, tournures favorites) pour reproduire fidèlement votre signature humaine unique tout en conservant 100 % du texte source.",
        system_rules="""- RÈGLES DE REPRODUCTION DU STYLE PERSONNEL :
1. Imiter fidèlement la structure des phrases, le niveau de langue et le vocabulaire de l'échantillon fourni.
2. Conserver les habitudes stylistiques du texte de référence (transitions, apartés, ponctuation favorite).
3. Conserver l'intégralité des arguments et paragraphes du texte source sans coupure.
4. Épouser le rythme de pensée de l'auteur sans ajouter de tournures stéréotypées d'IA.""",
        example_tone="(S'adapte dynamiquement à votre échantillon)",
    ),
}


CORE_HUMANIZER_GUIDELINES = """
=== RÈGLES FONDAMENTALES D'HUMANISATION ÉDITORIALE (ZÉRO TRONCATURE DU FOND, ZÉRO PARAPHRASE ROBOTIQUE) ===

1. RÈGLE MAÎTRESSE : CONSERVATION DU FOND INFORMATIF SANS PARAPHRASE MÉCANIQUE MOT-À-MOT
   - Tu dois restituer 100 % de la matière informative réelle : faits, arguments substantiels, chiffres, dates, noms, articles de loi, concepts et étapes de raisonnement.
   - INTERDICTION DE LA PARAPHRASE MÉCANIQUE SYNONYMIQUE : Ne remplace pas chaque phrase creuse par une autre phrase creuse (ex: ne pas transformer "revêt un caractère fondamental" en "constitue un enjeu déterminant" ni "la situation est complexe" en "cette configuration commande une analyse").
   - Supprime ou tranche le verbiage de remplissage et les formules de politesse d'IA en fin de texte ("Je reste à votre disposition...", "N'hésitez pas..."). Ne les remplace pas par des équivalents polis : supprime-les ou remplace-les par une action concrète.
   - Condense et fusionne les phrases redondantes. Restitue les paragraphes de fond avec clarté sans tronquer la démonstration substantielle.

2. INTERDICTION DES TIRETS CADRATINS :
   - Aucun tiret cadratin (—) ni demi-cadratin (–) dans le texte final.
   - Les remplacer selon le sens par une virgule, un point, deux-points ou des parenthèses sobres.

3. ÉLIMINATION DES FAUX CONTRASTES ET STAGING :
   - Bannir les formules stéréotypées d'IA : "Non seulement... mais aussi...", "Ce n'est pas seulement X, c'est Y", "Not only... but also", "Non pas X, mais Y", "Loin d'être X, Y...".
   - Exprimer le fait de manière directe et affirmative sans théâtralisation.

4. SUPPRESSION DES CONCLUSIONS DRAMATIQUES ET FORMULES CREUSES :
   - Supprimer les phrases isolées de pseudo-sagesse en une ligne ("C'est là la vraie victoire", "À méditer", "Un pas dans la bonne direction").
   - Bannir les formules pseudo-profondes ("Au fond", "En réalité", "Au cœur de la question", "X est le miroir de Y", "Le langage de...").
   - Supprimer les annonces théâtrales ("Plongeons dans...", "Voyons voir...", "Honnêtement ?", "Voici ce que vous devez savoir...").

5. AUCUN GROUPEMENT PAR TROIS FORCÉ NI LISTES ARTIFICIELLES :
   - Ne pas forcer artificiellement les énumérations à trois éléments si la pensée n'en demande pas trois.
   - Bannir les listes à puces artificielles avec titre en gras et deux-points (**Titre :** Description). Rédiger en paragraphes continus et fluides.

6. MOTS ET FORMULES INTERDITS (sauf si indispensables au domaine technique) :
   - Clichés de posture, lettre de motivation et candidature d'IA : "correspond à mon parcours", "s'inscrit dans la continuité de mon parcours", "en adéquation avec mon profil", "à la croisée de / du / des", "au carrefour de", "au confluent de", "fort de mon expérience", "mettre à profit mes compétences", "passionné par", "force de proposition", "relever de nouveaux défis", "dans le cadre de mes fonctions", "en phase avec vos enjeux".
   - Buzzwords et superlatifs creux : delve, tapestry, testament, vibrant, crucial turning point, pivotal, landscape (abstrait), underscore, showcase, beacon, catalyst, cornerstone.
   - en constante évolution, dans un monde numérique, témoigne de l'importance, joue un rôle clé / charnière, riche mosaïque, pierre angulaire, paysage technologique, écosystème dynamique.
   - synergie, solutions innovantes, rejoignent directement.
   - Adverbes de remplissage et modalisateurs boursouflés : directement, exactement, précisément, particulièrement, parfaitement, totalement, pleinement.

7. AUCUN EMOJI NI PRÉAMBULE :
   - Ne jamais inclure d'emojis.
   - Aucun préambule ('Voici le texte :', 'Certainement...'), aucune salutation ni commentaire. Renvoyer UNIQUEMENT le texte final humanisé.

8. PRÉSERVATION STRICTE DES FAITS, CITATIONS ET DONNÉES TECHNIQUES :
   - Conserver l'intégralité des dates, chiffres, noms propres, références juridiques (articles, règlements, directives), termes entre parenthèses et vocabulaire de spécialité.
   - Ne rien inventer.

9. PONCTUATION ET TYPOGRAPHIE HUMAINE STANDARD (CLAVIER ASCII PUR) :
   - Pour TOUS les signes de ponctuation (doubles et simples : ; ! ? : , .) : ZÉRO espace avant le signe, UN SEUL espace standard après (ex: 'Bonjour! Comment vas-tu? Voici: la suite.').
   - Guillemets : Utiliser exclusivement les guillemets droits doubles \" (U+0022). Bannir les chevrons français « » et les guillemets courbes “ ”.
   - Apostrophes : Utiliser exclusivement l'apostrophe droite standard ' (U+0027). Bannir l'apostrophe typographique courbe ’ et ‘.
   - ZÉRO ESPACE INSÉCABLE OU DEMI-ESPACE : Ne jamais insérer d'espace insécable (U+00A0), d'espace fine (U+202F) ou de demi-cadratin. Utiliser uniquement la barre d'espace standard du clavier (U+0020).
"""


def build_humanize_prompt(
    input_text: str,
    profile_id: str = "avocat",
    custom_sample: str | None = None,
    language: str = "fr",
) -> str:
    """Construit le prompt complet pour le modèle de langage."""
    profile = PROFILES.get(profile_id, PROFILES["avocat"])

    prompt_parts = [
        "Tu es un éditeur et rédacteur humain de référence, expert en réécriture anti-IA et en polissage stylistique de haut niveau.",
        f"Ton rôle : Réécrire et humaniser le texte ci-dessous selon la voix de : **{profile.name}**.",
        "",
        "=== MISSION CRUCIALE ===",
        "1. RESTITUTION SUBSTANTIELLE : Tu dois restituer 100 % de la matière informative, factuelle et technique du texte source, sans omission d'arguments de fond.",
        "2. INTERDICTION FORMELLE DU REMPLACEMENT SYNONYMIQUE CREUX ET DES CLICHÉS D'IA : Ne remplace JAMAIS un cliché d'IA par un autre cliché (ex: interdiction absolue de 'correspond à mon parcours', 'à la croisée de/du', 'au carrefour de', 'solutions innovantes', 'synergie'). Coupe les bavardages, va droit aux faits opérationnels, à la stack et aux chiffres.",
        "3. ZÉRO FORMULE DE POLITESSE D'IA : Supprime toutes les formules de politesse préfabriquées ('Je reste à votre entière disposition...', 'N'hésitez pas...') sans les remplacer par d'autres banalités.",
        "4. PRÉSERVATION DES FAITS ET RÉFÉRENCES : Conserve scrupuleusement tous les chiffres, dates, noms, stacks, métriques et composants techniques.",
        "",
        "--- DIRECTIVES SPÉCIFIQUES DU PROFIL ---",
        profile.system_rules,
        "",
    ]

    if profile_id == "avocat":
        prompt_parts.extend(
            [
                "--- EXEMPLE DE TRANSFORMATION ATTENDU (STANDARD LAWYERSCRIB) ---",
                "Texte original (saturé d'IA) :",
                "\"Comme il a été souligné supra, la problématique de la validité de la clause de non-concurrence revêt un caractère fondamental dans le cadre du présent litige. Il convient, à cet égard, de rappeler que la doctrine majoritaire s'accorde à reconnaître que ladite clause doit, pour être valide, répondre à des conditions cumulatives que la jurisprudence a progressivement précisées. Force est de constater que ces conditions ne semblent pas réunies en l'espèce. Il s'agit non seulement d'une question de droit, mais d'une question de justice contractuelle. En conclusion, la situation est complexe et nécessite une analyse approfondie. Je reste à votre entière disposition pour tout complément.\"",
                "",
                "Ce que l'IA fait de mal (À PROSCRIRE FORMELLEMENT - paraphrase mécanique synonymique creuse) :",
                "\"La validité de la clause de non-concurrence constitue l'enjeu déterminant du litige. La jurisprudence soumet la régularité de cette stipulation à des critères cumulatifs stricts. Ces exigences ne sont pas satisfaites en l'espèce. Le litige touche ainsi tant à la qualification juridique de la clause qu'à l'équilibre contractuel global. Cette configuration commande une analyse approfondie des pièces et des risques. Je me tiens à votre disposition pour vous assister dans la suite de ce dossier.\"",
                "",
                "Ce qu'un avocat praticien chevronné écrit réellement (RÉSULTAT ATTENDU) :",
                "\"La clause de non-concurrence est nulle faute de contrepartie financière, condition que la chambre sociale exige depuis 2002 (Cass. soc., 10 juill. 2002, n° 00-45.135). La nullité est relative : votre client peut s'en prévaloir ou y renoncer. S'il entend se réinstaller immédiatement, une lettre de renonciation adressée à l'employeur avant la fin du préavis est suffisante.\"",
                "",
            ]
        )

    if profile_id == "architecte":
        prompt_parts.extend(
            [
                "--- EXEMPLE DE TRANSFORMATION ATTENDU (POSTURE LEAD DEV / STAFF ENGINEER) ---",
                "Texte original (saturé de clichés IA de candidature/posture) :",
                '"Cette opportunité à la croisée de la data et du software engineering correspond parfaitement à mon parcours. Fort de mon expérience de Lead Developer, je souhaite mettre à profit mes compétences pour concevoir des solutions innovantes en synergie avec vos équipes et relever vos défis technologiques."',
                "",
                "Ce que l'IA fait de mal (À PROSCRIRE FORMELLEMENT - paraphrase avec les mêmes clichés d'IA) :",
                "\"Ce rôle situé au carrefour de l'ingénierie logicielle et de la data s'inscrit dans la continuité de mon parcours. Mon expertise technique me permettra de concevoir des architectures robustes en phase avec vos enjeux.\"",
                "",
                "Ce qu'un Lead Dev / Architecte senior pragmatique écrit réellement (RÉSULTAT ATTENDU) :",
                "\"Mon expérience combine la mise en production de pipelines de données temps réel sous Kafka/Flink et le lead d'équipes de 6 ingénieurs sur des microservices Python/Go. Sur ce projet, j'interviens pour structurer le delivery, fiabiliser l'infrastructure et garantir la tenue des SLAs de production.\"",
                "",
            ]
        )

    if profile_id == "custom" and custom_sample and custom_sample.strip():
        prompt_parts.extend(
            [
                "--- ÉCHANTILLON D'ÉCRITURE DE RÉFÉRENCE (À IMITER STRICTEMENT) ---",
                custom_sample.strip(),
                "",
            ]
        )

    prompt_parts.extend(
        [
            CORE_HUMANIZER_GUIDELINES,
            "",
            "--- TEXTE SOURCE À HUMANISER (SUPPRIMER LE BAVARDAGE, ALLER DROIT AU FAIT JURIDIQUE) ---",
            input_text.strip(),
            "",
            "--- TEXTE FINAL HUMANISÉ (Restituer UNIQUEMENT le texte final de praticien, sans préambule, sans formules de politesse IA, sans emojis) ---",
        ]
    )

    return "\n".join(prompt_parts)
