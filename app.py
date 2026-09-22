"""Antigravity Humanizer Studio - Application Streamlit complète.
Dé-ia-isation de texte, nettoyage Unicode, stylométrie et profils de style métier.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.ai_bridge import humanize_text, is_agy_available
from core.file_processor import (
    create_clean_docx,
    create_clean_pdf,
    extract_text_from_file,
    generate_diff_pdf,
    generate_diff_report_html,
    strip_image_metadata,
)
from core.profiles import PROFILES
from core.score_stylometry import (
    EditorialReport,
    analyze_stylometry,
    generate_editorial_report,
)
from core.text_unicode import clean_unicode, inspect_unicode

# ---------------------------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Humanizer Studio",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, minimalist interface
st.markdown(
    """
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .sub-title {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .choice-box {
        background-color: #F8FAFC;
        border-left: 4px solid #4F46E5;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sample file path for custom voice persistence
CUSTOM_VOICE_FILE = BASE_DIR / ".my_voice_sample.txt"

# ---------------------------------------------------------------------------
# Barre latérale : Paramètres du moteur et choix du profil
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Configuration du moteur d'IA")

    agy_installed = is_agy_available()
    engine_options = [
        "CLI Antigravity (Local & sans clé)",
        "Apportez votre propre clé / BYOK (API Google Gemini)",
    ]
    default_engine_idx = 0 if agy_installed else 1

    ai_engine = st.radio(
        "Moteur de réécriture :",
        options=engine_options,
        index=default_engine_idx,
        help="Antigravity CLI utilise votre session locale active sans clé requise. Le mode BYOK permet d'utiliser l'API Google Gemini avec votre propre clé d'API.",
    )

    api_key = ""
    gemini_model = "gemini-3-flash-preview"
    if ai_engine == "Apportez votre propre clé / BYOK (API Google Gemini)":
        st.markdown("#### Clé API Google AI Studio (BYOK)")
        default_env_key = os.environ.get("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Votre clé d'API Gemini :",
            value=st.session_state.get("gemini_api_key", default_env_key),
            type="password",
            help="Saisissez votre clé issue de Google AI Studio. Elle reste en mémoire pour votre session et n'est jamais transmise à des tiers.",
            placeholder="AIzaSy...",
        )
        st.session_state["gemini_api_key"] = api_key

        st.markdown(
            """
<div style="font-size: 0.85rem; color: #475569; margin-top: -6px; margin-bottom: 12px;">
    👉 <a href="https://aistudio.google.com/apikey" target="_blank" style="text-decoration: underline; color: #4F46E5; font-weight: 600;">Obtenir une clé gratuite sur Google AI Studio</a><br>
    <span style="color: #16A34A; font-weight: 500;">⚡ Quota gratuit : 15 requêtes/min sans carte bancaire.</span>
</div>
""",
            unsafe_allow_html=True,
        )

        model_options = [
            "gemini-3-flash-preview",
            "gemini-3.6-flash",
            "gemini-3.1-pro-preview",
            "gemini-3-pro-preview",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "Autre (saisie libre)",
        ]
        chosen_model = st.selectbox(
            "Modèle Gemini cible :",
            model_options,
            index=0,
            help="Sélectionnez le modèle Google Gemini à utiliser via votre clé API (ex. gemini-3-flash-preview).",
        )
        if chosen_model == "Autre (saisie libre)":
            gemini_model = st.text_input(
                "Identifiant du modèle :",
                value="gemini-3-flash-preview",
                placeholder="ex. gemini-3-flash-preview ou gemini-3.6-flash",
            )
        else:
            gemini_model = chosen_model

        if api_key.strip():
            st.success("✅ Clé API configurée (Mode BYOK actif)")
        else:
            st.warning(
                "⚠️ Clé API requise pour la réécriture IA. Les onglets d'inspection Unicode et de stylométrie restent 100 % opérationnels sans clé."
            )
    else:
        if agy_installed:
            st.success(
                "✅ Connecté au CLI local Antigravity (`agy`). Aucun envoi de clé requis."
            )
        else:
            st.warning(
                "⚠️ L'exécutable local `agy` n'est pas détecté dans l'environnement courant. Veuillez basculer sur le mode **BYOK (API Gemini)** ou installer Antigravity CLI."
            )

    st.markdown("---")
    st.markdown("### Profil de réécriture")

    profile_keys = list(PROFILES.keys())
    selected_profile_idx = st.selectbox(
        "Sélectionnez le style cible :",
        range(len(profile_keys)),
        format_func=lambda i: PROFILES[profile_keys[i]].name,
        index=0,
    )
    current_profile = PROFILES[profile_keys[selected_profile_idx]]

    st.info(f"**{current_profile.name}**\n\n{current_profile.short_desc}")

    # Custom voice sample management
    custom_sample_text = ""
    if current_profile.id == "custom":
        st.markdown("#### Échantillon de votre voix")
        saved_sample = ""
        if CUSTOM_VOICE_FILE.is_file():
            saved_sample = CUSTOM_VOICE_FILE.read_text(encoding="utf-8")

        custom_sample_text = st.text_area(
            "Collez 1 à 3 paragraphes représentatifs de votre écriture :",
            value=saved_sample,
            height=140,
            placeholder="Exemple : extraits d'emails types, articles de blog rédigés de votre main, mémos professionnels...",
        )
        if st.button("Sauvegarder cet échantillon"):
            CUSTOM_VOICE_FILE.write_text(custom_sample_text, encoding="utf-8")
            st.toast("Échantillon vocal sauvegardé avec succès.")

    st.markdown("---")
    st.markdown("### Réinitialisation")
    reset_voice_sample = st.checkbox(
        "Effacer aussi l'échantillon de voix enregistré", value=False
    )
    if st.button(
        "Réinitialiser tous les paramètres", type="secondary", use_container_width=True
    ):
        st.session_state.clear()
        if reset_voice_sample and CUSTOM_VOICE_FILE.is_file():
            CUSTOM_VOICE_FILE.unlink(missing_ok=True)
        st.toast("Tous les réglages et données de session ont été réinitialisés.")
        st.rerun()


# ---------------------------------------------------------------------------
# En-tête principal
# ---------------------------------------------------------------------------
st.markdown('<div class="main-title">Humanizer Studio</div>', unsafe_allow_html=True)
st.markdown(
    "<div class=\"sub-title\">Suppression des tics d'écriture d'IA, nettoyage Unicode déterministe et calibration stylistique.</div>",
    unsafe_allow_html=True,
)


def get_or_create_diff_pdf(
    report: EditorialReport, input_text: str, output_text: str, profile_name: str
) -> tuple[bool, bytes, str]:
    """Mémorise la génération PDF dans session_state pour éviter de relancer Playwright inutilement."""
    cache_key = f"diff_pdf_{hash((input_text, output_text, profile_name))}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    ok, pdf_data, err = generate_diff_pdf(
        report=report,
        input_text=input_text,
        output_text=output_text,
        profile_name=profile_name,
    )
    if ok:
        st.session_state[cache_key] = (ok, pdf_data, err)
    return ok, pdf_data, err


def render_editorial_and_stylometry_report(
    input_text: str, output_text: str, current_profile: Any, unicode_stats: Any = None
) -> None:
    """Affiche le rapport comparatif complet : diff mot-à-mot, métriques clés, tics d'IA détectés et journal d'audit."""
    if not input_text or not output_text:
        return

    st.markdown("---")
    st.markdown("### Traçabilité des modifications et bilan stylométrique")

    unicode_rep = inspect_unicode(input_text)
    editorial_rep = generate_editorial_report(
        input_text=input_text,
        output_text=output_text,
        profile_id=current_profile.id,
        unicode_stats=unicode_stats if unicode_stats else unicode_rep,
    )

    rep_in = editorial_rep.rep_in
    rep_out = editorial_rep.rep_out
    diff_stats = editorial_rep.diff_stats

    # 4 Cartes Métriques Clés
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "Indice de densité d'IA",
            f"{rep_out.composite_score:.2f}",
            delta=f"{rep_out.composite_score - rep_in.composite_score:.2f}",
            delta_color="inverse",
            help="Indice global de 0,0 (naturellement humain) à 1,0 (forte densité d'empreintes statistiques d'IA).",
        )
    with m2:
        st.metric(
            "Tics d'IA neutralisés",
            f"{rep_out.ai_phrase_count}",
            delta=f"{rep_out.ai_phrase_count - rep_in.ai_phrase_count}",
            delta_color="inverse",
            help="Nombre de formules convenues, clichés, faux contrastes et tics structurels purgés.",
        )
    with m3:
        st.metric(
            "Conservation factuelle",
            f"{diff_stats.get('retention_rate', 100)} %",
            delta=f"{diff_stats.get('words_preserved', 0)} / {diff_stats.get('words_before', 0)} mots",
            delta_color="off",
            help="Proportion des termes et faits du texte source rigoureusement conservés dans le texte final.",
        )
    with m4:
        st.metric(
            "Relief du rythme (burstiness)",
            f"{rep_out.burstiness:.2f}",
            delta=f"{rep_out.burstiness - rep_in.burstiness:+.2f}",
            help="Variance de la longueur des phrases. L'écriture humaine alterne phrases courtes et longues (> 0,40).",
        )

    # 3 Onglets d'analyse détaillée
    tab_diff, tab_choices, tab_stylometry = st.tabs(
        [
            "Diff visuel mot-à-mot",
            "Journal des modifications et choix",
            "Diagnostic stylométrique détaillé",
        ]
    )

    with tab_diff:
        st.markdown(
            """
<div style="display: flex; gap: 15px; align-items: center; margin-bottom: 12px; font-size: 0.9rem;">
    <span>Légende :</span>
    <span style="background-color: #FEE2E2; color: #991B1B; text-decoration: line-through; padding: 2px 8px; border-radius: 4px; font-weight: 500;">Mots et tics d'IA supprimés</span>
    <span style="background-color: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 4px; font-weight: 600;">Formulations réécrites</span>
    <span style="color: #64748B;">(Le texte non surligné correspond aux éléments préservés à l'identique)</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(editorial_rep.diff_html, unsafe_allow_html=True)

        st.caption(
            f"Volume initial : **{diff_stats.get('words_before', 0)} mots** | Volume final : **{diff_stats.get('words_after', 0)} mots** | Supprimés : **{diff_stats.get('words_deleted', 0)}** | Insérés : **{diff_stats.get('words_added', 0)}**"
        )

    with tab_choices:
        col_bilan_left, col_bilan_right = st.columns(2)

        with col_bilan_left:
            st.markdown("#### 1. Tics identifiés dans la source")
            if editorial_rep.tics_by_category or unicode_rep.flagged_positions:
                for category, tics in editorial_rep.tics_by_category.items():
                    with st.container():
                        st.markdown(
                            f"**{category}** ({len(tics)} occurrence{'s' if len(tics) > 1 else ''}) :"
                        )
                        for t in tics:
                            st.markdown(f"- `{t['text']}` : *{t['label']}*")

                if unicode_rep.flagged_positions:
                    st.markdown(
                        f"**Artefacts et caractères invisibles (Layer A)** ({len(unicode_rep.flagged_positions)} trouvé(s)) :"
                    )
                    for char_name, count in unicode_rep.found_chars.items():
                        st.markdown(f"- `{char_name}` : **{count}** occurrence(s)")
            else:
                st.success(
                    "Aucun tic de phrasé d'IA ni artefact Unicode détecté dans le texte source."
                )

        with col_bilan_right:
            st.markdown("#### 2. Choix éditoriaux appliqués")
            for choice in editorial_rep.choices_made:
                with st.expander(choice["category"], expanded=True):
                    st.caption(choice["description"])
                    for item in choice["items"]:
                        st.markdown(f"- {item}")

    with tab_stylometry:
        c_st1, c_st2 = st.columns(2)
        with c_st1:
            st.markdown("#### Richesse lexicale (MATTR)")
            st.write(
                f"- Score source : **{rep_in.mattr:.2f}**\n"
                f"- Score final : **{rep_out.mattr:.2f}**\n"
                "- *Le MATTR (Moving-Average Type-Token Ratio) évalue la variété du vocabulaire sur des fenêtres glissantes de 50 mots.*"
            )
        with c_st2:
            st.markdown("#### Longueur moyenne des phrases")
            st.write(
                f"- Texte source : **{rep_in.avg_sentence_len:.1f} mots/phrase**\n"
                f"- Texte humanisé : **{rep_out.avg_sentence_len:.1f} mots/phrase**\n"
                f"- Coefficient de variation (burstiness) : **{rep_out.burstiness:.2f}**"
            )

    # Téléchargement du rapport de diff visuel
    st.markdown("---")
    ok_pdf, pdf_bytes, pdf_err = get_or_create_diff_pdf(
        editorial_rep, input_text, output_text, current_profile.name
    )

    if ok_pdf and pdf_bytes:
        st.download_button(
            label="Télécharger le rapport de diff visuel (.pdf)",
            data=pdf_bytes,
            file_name="tracking_des_modifs.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    else:
        html_report = generate_diff_report_html(
            editorial_rep, input_text, output_text, current_profile.name
        )
        st.download_button(
            label="Télécharger le rapport de diff visuel (.html)",
            data=html_report,
            file_name="tracking_des_modifs.html",
            mime="text/html",
            type="primary",
            use_container_width=True,
            help=f"Moteur PDF indisponible ({pdf_err}). Téléchargement de secours au format HTML interactif."
            if pdf_err
            else None,
        )


# ---------------------------------------------------------------------------
# Onglets de navigation
# ---------------------------------------------------------------------------
tab_text, tab_doc, tab_voice, tab_guide = st.tabs(
    [
        "Texte instantané",
        "Documents et médias",
        "Voix personnalisée",
        "Guide des règles de style",
    ]
)


# ---------------------------------------------------------------------------
# Onglet 1 : Traitement de texte instantané
# ---------------------------------------------------------------------------
with tab_text:
    col_ex1, col_ex2, col_ex3, col_ex_clear = st.columns([1, 1, 1, 1])
    if col_ex1.button("Exemple juridique"):
        st.session_state["raw_input_text"] = (
            "En conclusion, il est crucial de souligner que cet accord ne constitue pas seulement un jalon important, mais témoigne également d'un vibrant partenariat dans un paysage en constante évolution. — Le contrat joue un rôle charnière."
        )
        st.session_state["humanized_text"] = ""
        st.rerun()
    if col_ex2.button("Exemple technique"):
        st.session_state["raw_input_text"] = (
            "Let's dive into the architecture. In today's fast-paced digital world, microservices delve into a rich tapestry of distributed events. It is important to note that performance is maximized — no guessing."
        )
        st.session_state["humanized_text"] = ""
        st.rerun()
    if col_ex3.button("Exemple de communication"):
        st.session_state["raw_input_text"] = (
            "Découvrez une expérience révolutionnaire nichée au cœur de l'innovation ! Nos solutions de pointe favorisent une synergie inégalée, ouvrant la voie à un avenir prometteur où chaque défi devient une opportunité."
        )
        st.session_state["humanized_text"] = ""
        st.rerun()
    if col_ex_clear.button("Effacer"):
        st.session_state["raw_input_text"] = ""
        st.session_state["humanized_text"] = ""
        st.rerun()

    col_in, col_out = st.columns(2)

    with col_in:
        st.markdown("#### Texte source")
        input_text = st.text_area(
            "Entrez votre texte à humaniser :",
            value=st.session_state.get("raw_input_text", ""),
            height=300,
            label_visibility="collapsed",
            placeholder="Collez ici votre texte brut ou généré par une IA...",
        )
        st.session_state["raw_input_text"] = input_text
        report_before = analyze_stylometry(input_text)
        unicode_report = inspect_unicode(input_text)

        st.caption(
            f"Mots : **{report_before.word_count}** | Phrases : **{report_before.sentence_count}** | Tics détectés : **{report_before.ai_phrase_count}** | Invisibles : **{unicode_report.invisible_count + unicode_report.space_homoglyph_count}**"
        )

    with col_out:
        st.markdown("#### Texte humanisé")
        output_text = st.text_area(
            "Résultat épuré :",
            value=st.session_state.get("humanized_text", ""),
            height=300,
            label_visibility="collapsed",
            placeholder="Le texte réécrit apparaîtra ici...",
        )
        if output_text:
            report_after = analyze_stylometry(output_text)
            st.caption(
                f"Mots : **{report_after.word_count}** | Phrases : **{report_after.sentence_count}** | Indice de densité d'IA : **{report_after.composite_score}** ({report_after.density_tier})"
            )
        else:
            st.caption("En attente de traitement...")

    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])
    with btn_col1:
        run_humanize = st.button(
            "Humaniser le texte", type="primary", use_container_width=True
        )
    with btn_col2:
        if output_text:
            st.download_button(
                "Télécharger le texte (.txt)",
                data=output_text,
                file_name="texte_humanise.txt",
                mime="text/plain",
                use_container_width=True,
            )

    if run_humanize:
        if not input_text or not input_text.strip():
            st.warning("Veuillez saisir un texte à humaniser.")
        else:
            with st.spinner(
                f"Traitement en cours avec le profil {current_profile.name}..."
            ):
                # Étape 1 : Nettoyage Unicode initial
                clean_step1, unicode_stats = clean_unicode(
                    input_text, normalize_spaces=True
                )
                st.session_state["last_unicode_stats"] = unicode_stats

                # Étape 2 : Humanisation par blocs avec conservation intégrale
                success, ai_response = humanize_text(
                    input_text=clean_step1,
                    profile_id=current_profile.id,
                    custom_sample=custom_sample_text
                    if current_profile.id == "custom"
                    else None,
                    engine="BYOK" if "BYOK" in ai_engine else "agy",
                    api_key=api_key,
                    gemini_model=gemini_model,
                )

                if not success:
                    st.error(f"Erreur : {ai_response}")
                else:
                    # Étape 3 : Nettoyage Unicode final
                    clean_step2, _ = clean_unicode(ai_response, normalize_spaces=True)
                    clean_step2 = clean_step2.replace("—", ",").replace("–", "-")

                    st.session_state["humanized_text"] = clean_step2
                    st.rerun()

    # Section d'analyse comparative et choix éditoriaux
    if output_text and input_text:
        render_editorial_and_stylometry_report(
            input_text=input_text,
            output_text=output_text,
            current_profile=current_profile,
            unicode_stats=st.session_state.get("last_unicode_stats"),
        )


# ---------------------------------------------------------------------------
# Onglet 2 : Traitement de documents et médias
# ---------------------------------------------------------------------------
with tab_doc:
    st.markdown("#### Dépôt de fichiers")
    st.caption(
        "Prend en charge les documents texte (.docx, .pdf, .md, .txt) et les images (.png, .jpg) pour la purge des métadonnées de traçage C2PA et EXIF."
    )

    uploaded_file = st.file_uploader(
        "Déposez un fichier ici :",
        type=["docx", "pdf", "md", "txt", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        filename = uploaded_file.name
        ext = Path(filename).suffix.lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            st.markdown(f"##### Fichier image : `{filename}`")
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.image(
                    uploaded_file, caption="Image originale", use_container_width=True
                )

            with col_img2:
                if st.button("Purger les métadonnées d'IA et EXIF"):
                    ok, clean_img_buf, stats = strip_image_metadata(uploaded_file)
                    if ok:
                        st.success(
                            "Métadonnées de provenance (C2PA, EXIF, XMP, SynthID) purgées avec succès."
                        )
                        st.json(stats)
                        clean_name = f"clean_{filename}"
                        st.download_button(
                            label=f"Télécharger {clean_name}",
                            data=clean_img_buf,
                            file_name=clean_name,
                            mime=f"image/{stats['format'].lower()}",
                        )
                    else:
                        st.error(f"Erreur : {stats.get('error')}")

        else:
            # Document texte
            st.markdown(f"##### Document texte : `{filename}`")
            ok, doc_text, doc_type = extract_text_from_file(uploaded_file)

            if not ok:
                st.error(doc_text)
            else:
                st.text_area(
                    "Aperçu du contenu extrait :",
                    value=doc_text[:1000] + ("..." if len(doc_text) > 1000 else ""),
                    height=150,
                )

                if st.button("Humaniser l'intégralité du document"):
                    with st.spinner(
                        f"Traitement du document selon le profil {current_profile.name}..."
                    ):
                        clean_initial, doc_unicode_stats = clean_unicode(doc_text)
                        success, ai_out = humanize_text(
                            input_text=clean_initial,
                            profile_id=current_profile.id,
                            custom_sample=custom_sample_text
                            if current_profile.id == "custom"
                            else None,
                            engine="BYOK" if "BYOK" in ai_engine else "agy",
                            api_key=api_key,
                            gemini_model=gemini_model,
                        )

                        if success:
                            clean_final, _ = clean_unicode(
                                ai_out, normalize_spaces=True
                            )
                            clean_final = clean_final.replace("—", ",").replace(
                                "–", "-"
                            )
                            st.success("Document humanisé avec succès.")
                            st.text_area(
                                "Résultat final :", value=clean_final, height=250
                            )

                            col_d1, col_d2 = st.columns(2)
                            with col_d1:
                                if ext == ".docx":
                                    docx_buf = create_clean_docx(clean_final)
                                    st.download_button(
                                        "Télécharger le document Word épuré (.docx)",
                                        data=docx_buf,
                                        file_name=f"humanise_{filename}",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        use_container_width=True,
                                    )
                                elif ext == ".pdf":
                                    pdf_buf = create_clean_pdf(clean_final)
                                    st.download_button(
                                        "Télécharger le document PDF épuré (.pdf)",
                                        data=pdf_buf,
                                        file_name=f"humanise_{filename}",
                                        mime="application/pdf",
                                        use_container_width=True,
                                    )
                                elif ext == ".md":
                                    st.download_button(
                                        "Télécharger le document Markdown épuré (.md)",
                                        data=clean_final,
                                        file_name=f"humanise_{filename}",
                                        mime="text/markdown",
                                        use_container_width=True,
                                    )
                                else:
                                    st.download_button(
                                        "Télécharger le document texte épuré (.txt)",
                                        data=clean_final,
                                        file_name=f"humanise_{filename}",
                                        mime="text/plain",
                                        use_container_width=True,
                                    )

                            # Bilan comparatif du document
                            render_editorial_and_stylometry_report(
                                input_text=doc_text,
                                output_text=clean_final,
                                current_profile=current_profile,
                                unicode_stats=doc_unicode_stats,
                            )
                        else:
                            st.error(ai_out)


# ---------------------------------------------------------------------------
# Onglet 3 : Voix personnalisée
# ---------------------------------------------------------------------------
with tab_voice:
    st.markdown("#### Studio de calibration stylistique")
    st.markdown("""
    Pour que l'outil reproduise fidèlement **votre signature humaine**, collez 2 ou 3 paragraphes de votre propre rédaction (courriels, articles, mémos rédigés par vos soins).
    
    L'algorithme analyse votre empreinte stylométrique (rythme, longueur moyenne de phrases, vocabulaire) et l'injecte lors des réécritures avec le profil **« Ma propre voix »**.
    """)

    voice_sample = st.text_area(
        "Votre échantillon d'écriture authentique :",
        value=CUSTOM_VOICE_FILE.read_text(encoding="utf-8")
        if CUSTOM_VOICE_FILE.is_file()
        else "",
        height=220,
        placeholder="Exemple : Lorsque je rédige un rapport, je vais directement aux faits sans détour. Inutile d'ajouter des formules d'emphase superflues...",
    )

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("Enregistrer comme voix par défaut", type="primary"):
            CUSTOM_VOICE_FILE.write_text(voice_sample, encoding="utf-8")
            st.success("Empreinte vocale enregistrée.")
    with col_v2:
        if voice_sample.strip():
            rep_v = analyze_stylometry(voice_sample)
            st.markdown("**Diagnostic de votre style :**")
            st.markdown(
                f"- Longueur moyenne des phrases : **{rep_v.avg_sentence_len:.1f} mots**"
            )
            st.markdown(f"- Relief du rythme (burstiness) : **{rep_v.burstiness:.2f}**")
            st.markdown(f"- Diversité lexicale (MATTR) : **{rep_v.mattr:.2f}**")


# ---------------------------------------------------------------------------
# Onglet 4 : Guide des règles de style
# ---------------------------------------------------------------------------
with tab_guide:
    st.markdown("### Guide des 25 règles de dé-ia-isation")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("""
        #### A. Mise en scène et théâtralisation
        1. **Pas de faux contraste « Not X but Y »** : éviter *« Ce n'est pas seulement X, c'est Y »*.
        2. **Pas de clôture dramatique en une ligne** : supprimer *« C'est là la vraie victoire »*.
        3. **Pas d'aphorisme creux** : remplacer *« La symétrie est le langage de la confiance »* par le fait réel.
        4. **Pas de chauffe théâtrale** : bannir *« Plongeons dans... »*, *« Honnêtement ? »*.
        5. **Pas de débat artificiel contre des fantômes** : supprimer les réfutations d'objections non soulevées.

        #### B. Rythme mécanique et répétition
        6. **Pas de triade forcée** : éviter les groupes de trois artificiels (*innovation, inspiration et impact*).
        7. **Pas d'ouvertures de phrases répétitives**.
        8. **Zéro tiret cadratin (—)** : remplacer par virgule, point ou deux-points.
        9. **Pas d'empilement de modalisateurs** (*« pourrait potentiellement sembler »*).
        10. **Suppression des paires de mots avec traits d'union excessifs**.
        """)
    with col_g2:
        st.markdown("""
        #### C. Inflation verbale et fausse autorité
        11. **Bannir les mots d'IA surutilisés** (*delve, tapestry, testament, crucial, landscape*).
        12. **Supprimer l'importance artificielle** (*« marque un tournant décisif », « témoigne de »*).
        13. **Pas de participe présent en queue de phrase** (*« ...soulignant ainsi son importance »*).
        14. **Pas de ton publicitaire surjoué** (*« niché au cœur de », « vibrant », « breathtaking »*).
        15. **Remplacer les verbes d'évitement** (*« se positionne comme », « arbore »*) par *est* ou *a*.

        #### D. Formatage et résidus
        16. **Pas de liste à puces avec titres en gras et deux-points**.
        17. **Pas d'emojis décoratifs dans les titres ou le corps du texte**.
        18. **Suppression totale des résidus de conversation** (*« J'espère que cela aide », « Excellente question »*).
        """)
