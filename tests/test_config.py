from faceiq.config import AppConfig


def test_weights_total_100():
    config = AppConfig(); config.validate(); assert config.weights.total() == 100


def test_classification_boundaries():
    config = AppConfig(); assert config.classify(85) == "Excellent"; assert config.classify(65) == "Bon"; assert config.classify(45) == "Moyen"; assert config.classify(44.9) == "Mauvais"
