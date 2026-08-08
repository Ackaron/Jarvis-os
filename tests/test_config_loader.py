from core.config_loader import get_domains_config, get_routing_config


def test_routing_config_has_defaults():
    config = get_routing_config()
    assert "defaults" in config
    assert "primary_model" in config["defaults"]


def test_routing_config_has_presentation_rule():
    config = get_routing_config()
    assert config["routing_rules"]["presentation"]["primary"] == "ollama-local"


def test_domains_config_has_four_domains():
    config = get_domains_config()
    assert set(config["domains"].keys()) == {"intc", "bootlegger", "house", "education"}


def test_domains_config_intc_has_expected_fields():
    domain = get_domains_config()["domains"]["intc"]
    assert domain["name"] == "ИНТЦ"
    assert "интц" in domain["aliases"]
