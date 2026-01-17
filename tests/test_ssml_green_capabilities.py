"""Tests for ssml-green capabilities support."""

from ssmd.capabilities import TTSCapabilities, load_ssml_green_platform


def test_supports_key_default_true():
    caps = TTSCapabilities(ssml_green={"elements››level (optional)": False})
    assert caps.supports_key("missing-key") is True
    assert caps.supports_key("elements››level (optional)") is False


def test_load_ssml_green_platform_flatten_and_map(tmp_path):
    data = {
        "SSML_1.0": {
            "elements››level (optional)": True,
            'attribute values››level="strong"': False,
            "elements››time (optional)": True,
            "elements››xml:lang (required)": True,
            "elements›~~(sentence)›xml:lang (optional)": False,
            "elements› (paragraph)›xml:lang (optional)": False,
            "elements››interpret-as (required)": True,
        },
        "COMMON": {
            "elements››ph (required)": True,
            "elements››alias (required)": True,
            "elements››rate (optional)": True,
        },
    }
    path = tmp_path / "azure.json"
    path.write_text(__import__("json").dumps(data), encoding="utf-8")

    caps = load_ssml_green_platform(path)
    assert caps.break_tags is True
    assert caps.phoneme is True
    assert caps.substitution is True
    assert caps.language_scopes["root"] is True
    assert caps.language_scopes["sentence"] is False
    assert caps.language_scopes["paragraph"] is False


def test_language_scope_sentence_warning(tmp_path):
    data = {
        "SSML_1.0": {
            "elements››xml:lang (required)": True,
            "elements›~~(sentence)›xml:lang (optional)": False,
            "elements› (paragraph)›xml:lang (optional)": True,
        }
    }
    path = tmp_path / "lang.json"
    path.write_text(__import__("json").dumps(data), encoding="utf-8")
    caps = load_ssml_green_platform(path)

    from ssmd.segment import Segment
    from ssmd.sentence import Sentence

    sentence = Sentence(segments=[Segment(text="Hello")], language="fr-FR")
    warnings: list[str] = []
    _ = sentence.to_ssml(capabilities=caps, warnings=warnings)
    assert warnings
