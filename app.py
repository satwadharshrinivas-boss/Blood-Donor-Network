from flask import Flask, request, send_file
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("donors.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            location TEXT NOT NULL,
            availability TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/register", methods=["POST"])
def register_donor():
    data = request.get_json()

    if not data:
        return {"error": "Donor information is required"}, 400

    required_fields = [
        "name",
        "mobile",
        "blood_group",
        "location",
        "availability"
    ]

    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400

    conn = sqlite3.connect("donors.db")

    conn.execute("""
        INSERT INTO donors
        (name, mobile, blood_group, location, availability)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["mobile"],
        data["blood_group"],
        data["location"],
        data["availability"]
    ))

    conn.commit()
    conn.close()

    return {"message": "Donor registered successfully!"}, 201

@app.route("/search", methods=["GET"])
def search_donors():
    blood_group = request.args.get("blood_group")
    location = request.args.get("location")

    conn = sqlite3.connect("donors.db")
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM donors WHERE availability = ?"
    params = ["Available"]

    if blood_group:
        query += " AND blood_group = ?"
        params.append(blood_group)

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    donors = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "donors": [dict(donor) for donor in donors]
    }
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)