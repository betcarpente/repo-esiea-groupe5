from flask import Flask, jsonify

app = Flask(__name__)

ALERT_THRESHOLD = 25


def alert_threshold():
    """Seuil d'alerte au-dessus duquel une notification est declenchee."""
    return ALERT_THRESHOLD


def sanitize_input(value):
    """Echappe les caracteres dangereux d'une entree utilisateur."""
    return value.replace("<", "&lt;").replace(">", "&gt;")


@app.route("/health")
def health():
    return jsonify(status="ok"), 200

# faute volontaire dans le nom de la route pour tester le workflow
@app.route("/status")
def status():
    return jsonify(service="projet-devops-groupe-demo", version="1.0", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas eu metus id tortor elementum dapibus. Orci varius natoque penatibus et magnis dis parturient montes"), 200


if __name__ == "__main__":
    app.run(debug=True)
