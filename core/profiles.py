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
        short_desc="Phrasé rigoureux, nuances doctrinales, vocabulaire juridique précis, zéro affirmation péremptoire.",
        full_desc="Inspiré du skill BMAD Avocat et Academic Writer. Adopte une rigueur juridique doctrinale, qualifie exactement les faits et concepts, privilégie le raisonnement hypothético-déductif et élimine toute affirmation non étayée.",
        system_rules="""- RÈGLES DOCTRINALES ET JURIDIQUES :
1. Précision terminologique : qualifier juridiquement les notions sans approximation tout en conservant chaque référence de loi, article ou règlement.
2. Conservation intégrale des développements : traiter et restituer chaque moyen, chaque étape du raisonnement et chaque nuance de fait sans jamais résumer.
3. Zéro affirmation péremptoire gratuite : chaque conclusion découle d'une prémisse vérifiable.
4. Mesure et pondération : utiliser des modalisateurs précis (le cas échéant, sous réserve de, à l'aune de) sans empilement artificiel.
5. Ton institutionnel et doctrinal : sobre, analytique, dénué de tout enthousiasme ou verbiage émotionnel.
6. Structure soignée : respecter scrupuleusement la progression logique des phrases et paragraphes de l'auteur.""",
        example_tone="La stipulation litigieuse ne saurait s'analyser en une obligation de résultat en l'absence d'aléa maîtrisé par le débiteur.",
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
        short_desc="Pragmatique, concis, direct, axé sur les contraintes réelles et l'ingénierie.",
        full_desc="Style d'ingénieur logiciel chevronné (staff engineer ou software architect). Focus sur les compromis de scalabilité, la latence, la maintenabilité, les cas limites et l'expérience de production réelle, sans tronquer les spécifications.",
        system_rules="""- RÈGLES D'INGÉNIERIE ET TECH LEAD :
1. Pragmatisme et sobriété : phrases courtes, directes, centrées sur le fonctionnement réel du système.
2. Préservation intégrale des concepts techniques : conserver chaque protocole, API, nom de composant, métrique et cas limite mentionné.
3. Compromis techniques explicites : peser débit vs latence, cohérence vs disponibilité, simplicité vs flexibilité.
4. Voix active : identifier clairement qui ou quel composant exécute l'action (pas de passif flou).
5. Rejet des métaphores numériques creuses (paysage digital, mosaïque applicative).""",
        example_tone="Le service maintient un cache mémoire local pour éviter d'inonder la base PostgreSQL lors des pics de charge.",
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
=== RÈGLES FONDAMENTALES D'HUMANISATION ÉDITORIALE (ZÉRO TRONCATURE, ZÉRO RÉSUMÉ) ===

1. RÈGLE MAÎTRESSE : CONSERVATION INTÉGRALE ET ALIGNEMENT PARAGRAPHE PAR PARAGRAPHE
   - L'humanisation N'EST PAS un résumé, N'EST PAS une synthèse, et N'EST PAS une réécriture libre.
   - Tu dois restituer 100 % de la matière textuelle : chaque phrase, chaque argument, chaque incise, chaque exemple et chaque paragraphe du texte source doivent avoir leur équivalent dans le texte final.
   - INTERDICTION STRICTE DE CONDENSER OU TRONQUER LA FIN : Le dernier paragraphe et la conclusion doivent être traités avec la même exhaustivité et la même richesse de développement que le premier.
   - Respecter le fil conducteur de l'auteur : conserver l'ordre des phrases et des idées sans intervertir arbitrairement les paragraphes ni supprimer des propositions subordonnées.

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
   - delve, tapestry, testament, vibrant, crucial turning point, pivotal, landscape (abstrait), underscore, showcase, beacon, catalyst, cornerstone.
   - en constante évolution, dans un monde numérique, témoigne de l'importance, joue un rôle clé / charnière, riche mosaïque, pierre angulaire.

7. AUCUN EMOJI NI PRÉAMBULE :
   - Ne jamais inclure d'emojis.
   - Aucun préambule ('Voici le texte :', 'Certainement...'), aucune salutation ni commentaire. Renvoyer UNIQUEMENT le texte final humanisé.

8. PRÉSERVATION STRICTE DES FAITS, CITATIONS ET DONNÉES TECHNIQUES :
   - Conserver l'intégralité des dates, chiffres, noms propres, références juridiques (articles, règlements, directives), termes entre parenthèses et vocabulaire de spécialité.
   - Ne rien inventer.
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
        "Tu es un éditeur et rédacteur humain de référence, expert en réécriture anti-IA et en polissage stylistique.",
        f"Ton rôle : Humaniser le texte ci-dessous selon le profil : **{profile.name}** tout en conservant l'INTÉGRALITÉ de son contenu et de sa structure.",
        "",
        "=== MISSION CRUCIALE ===",
        "1. REPRODUCTION EXHAUSTIVE : Tu dois traiter et restituer TOUT le texte source, du tout premier mot jusqu'au TOUT DERNIER PARAGRAPHE, sans AUCUNE coupe ni aucun résumé.",
        "2. RESPECT DE LA STRUCTURE : Conserve la même structure de paragraphes. Chaque phrase ou argument doit être humanisé et restitué à sa place.",
        "3. SUPPRESSION DES TICS D'IA : Élimine les tirets cadratins (—), les faux contrastes (Non seulement... mais aussi), les listes stéréotypées et les formules creuses.",
        "4. PRÉSERVATION DES FAITS ET TERMES : Conserve scrupuleusement tous les chiffres, dates, noms, articles de loi, règlements et termes techniques.",
        "",
        "--- DIRECTIVES SPÉCIFIQUES DU PROFIL ---",
        profile.system_rules,
        "",
    ]

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
            "--- TEXTE SOURCE À HUMANISER INTÉGRALEMENT (NE RIEN SUPPRIMER, NE RIEN RÉSUMER) ---",
            input_text.strip(),
            "",
            "--- TEXTE FINAL HUMANISÉ (Restituer l'INTÉGRALITÉ du texte humanisé, sans préambule, sans coupure de fin, sans emojis) ---",
        ]
    )

    return "\n".join(prompt_parts)
