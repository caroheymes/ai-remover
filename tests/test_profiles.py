from __future__ import annotations

from core.profiles import PROFILES, build_humanize_prompt


class TestProfiles:
    def test_all_expected_profiles_exist(self):
        expected_keys = {
            "avocat",
            "analyste",
            "architecte",
            "chercheur",
            "communicant",
            "custom",
        }
        assert set(PROFILES.keys()) == expected_keys

    def test_profile_attributes(self):
        for pid, prof in PROFILES.items():
            assert prof.id == pid
            assert len(prof.name) > 0
            assert len(prof.short_desc) > 0
            assert len(prof.full_desc) > 0
            assert len(prof.system_rules) > 0
            assert len(prof.example_tone) > 0

    def test_build_prompt_default_fallback(self):
        prompt = build_humanize_prompt(
            "Voici un texte d'exemple.", profile_id="unknown_profile"
        )
        # Should fallback to avocat
        assert PROFILES["avocat"].name in prompt
        assert "Voici un texte d'exemple." in prompt
        assert "INTERDICTION DES TIRETS CADRATINS" in prompt

    def test_build_prompt_with_custom_sample(self):
        sample = "Mon style personnel avec des phrases très percutantes et familières."
        input_text = "Dans un monde en constante évolution, l'IA joue un rôle clé."
        prompt = build_humanize_prompt(
            input_text=input_text,
            profile_id="custom",
            custom_sample=sample,
        )
        assert sample in prompt
        assert "ÉCHANTILLON D'ÉCRITURE DE RÉFÉRENCE" in prompt
        assert input_text in prompt
        assert PROFILES["custom"].name in prompt

    def test_build_prompt_communicant(self):
        input_text = "Introduction au sujet."
        prompt = build_humanize_prompt(input_text=input_text, profile_id="communicant")
        assert PROFILES["communicant"].name in prompt
        assert "RÈGLES DE RÉDACTION ORGANIQUE" in prompt
        assert input_text in prompt

    def test_build_prompt_architecte_lead_dev(self):
        input_text = "Notre architecture utilise des solutions innovantes en synergie."
        prompt = build_humanize_prompt(input_text=input_text, profile_id="architecte")
        assert PROFILES["architecte"].name in prompt
        assert "RÈGLES STRICTES D'INGÉNIERIE ET POSTURE LEAD DEV" in prompt
        assert "BANNED WORDS" in prompt
        assert "directement" in prompt
        assert "synergie" in prompt
        assert "correspond à mon parcours" in prompt
        assert "à la croisée de" in prompt
        assert "Delivery technique" in prompt
        assert "Cadrage métier" in prompt
        assert "BigQuery avec vues matérialisées via dbt" in prompt

    def test_english_source_language_preservation_and_cliches(self):
        from core.score_stylometry import analyze_stylometry

        en_text = (
            "I am thrilled to apply for this Staff Engineer role, which sits at the intersection of "
            "data and AI and aligns perfectly with my background. I leveraged my expertise to ship "
            "cutting-edge solutions and seamlessly integrate Python pipelines. "
            "Thank you for your time and consideration."
        )
        prompt = build_humanize_prompt(input_text=en_text, profile_id="architecte")
        assert "CONSERVATION STRICTE DE LA LANGUE DU TEXTE SOURCE" in prompt
        assert "thrilled to apply" in prompt
        assert "at the intersection of" in prompt

        stylo = analyze_stylometry(en_text)
        assert stylo.ai_phrase_count >= 5
        assert stylo.composite_score > 0.45
