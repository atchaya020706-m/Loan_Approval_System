from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
import os


app = Flask(__name__)

app.secret_key = "loan_secret_key"


# =========================================================
# LOAD ML MODEL
# =========================================================

with open("loan_model.pkl", "rb") as file:
    model = pickle.load(file)


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # USERS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # =====================================================
    # LOANS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            full_name TEXT,
            age INTEGER,
            gender TEXT,
            marital_status TEXT,

            mobile TEXT,
            email TEXT,
            address TEXT,

            employment_type TEXT,
            monthly_income REAL,

            loan_type TEXT,
            loan_amount REAL,
            loan_tenure INTEGER,
            purpose TEXT,

            credit_score INTEGER,

            eligibility_score REAL,
            emi REAL,
            suggested_loan_amount REAL,

            result TEXT,

            FOREIGN KEY(user_id)
            REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


create_database()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:

            return render_template(
                "register.html",
                error="All fields are required"
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            conn.close()

            return render_template(
                "register.html",
                error="Email already exists"
            )

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# USER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                password
            )
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session.clear()

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            print("--------------------------------")
            print("USER LOGIN SUCCESS")
            print("USER ID:", user["id"])
            print("USER NAME:", user["name"])
            print("--------------------------------")

            return redirect(url_for("dashboard"))

        error = "Invalid Email or Password"

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    current_user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            loan_type,
            purpose,
            age,
            monthly_income,
            loan_amount,
            credit_score,
            result
        FROM loans
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (current_user_id,)
    )

    loans = cursor.fetchall()

    conn.close()

    print("--------------------------------")
    print("DASHBOARD USER ID:", current_user_id)
    print("NUMBER OF LOANS:", len(loans))
    print("--------------------------------")

    return render_template(
        "dashboard.html",
        name=session["name"],
        loans=loans
    )


# =========================================================
# LOAN PAGE
# =========================================================

@app.route("/loan")
def loan():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template(
        "index.html",
        name=session["name"]
    )


# =========================================================
# LOAN PREDICTION
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:

        return redirect(url_for("login"))

    current_user_id = session["user_id"]

    # =====================================================
    # PERSONAL DETAILS
    # =====================================================

    full_name = request.form.get(
        "full_name",
        ""
    ).strip()

    age = int(
        request.form.get(
            "age",
            0
        )
    )

    gender = request.form.get(
        "gender",
        ""
    )

    marital_status = request.form.get(
        "marital_status",
        ""
    )

    mobile = request.form.get(
        "mobile",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    # =====================================================
    # EMPLOYMENT DETAILS
    # =====================================================

    employment_type = request.form.get(
        "employment_type",
        ""
    )

    monthly_income = float(
        request.form.get(
            "monthly_income",
            0
        )
    )

    # =====================================================
    # LOAN DETAILS
    # =====================================================

    loan_type = request.form.get(
        "loan_type",
        ""
    )

    loan_amount = float(
        request.form.get(
            "loan_amount",
            0
        )
    )

    loan_tenure = int(
        request.form.get(
            "loan_tenure",
            0
        )
    )

    purpose = request.form.get(
        "purpose",
        ""
    )

    # =====================================================
    # FINANCIAL DETAILS
    # =====================================================

    credit_score = int(
        request.form.get(
            "credit_score",
            0
        )
    )

    # =====================================================
    # ML PREDICTION
    # =====================================================

    prediction = model.predict(
        [[
            age,
            monthly_income,
            loan_amount,
            credit_score
        ]]
    )

    if prediction[0] == 1:

        result = "Loan Approved ✅"

    else:

        result = "Loan Rejected ❌"

    # =====================================================
    # ELIGIBILITY SCORE
    # =====================================================

    eligibility_score = (
        (credit_score / 900) * 60
        +
        min(
            monthly_income / 100000,
            1
        ) * 40
    )

    eligibility_score = round(
        eligibility_score,
        2
    )

    # =====================================================
    # SUGGESTED LOAN AMOUNT
    # =====================================================

    suggested_loan_amount = monthly_income * 20

    if suggested_loan_amount > loan_amount:

        suggested_loan_amount = loan_amount

    # =====================================================
    # EMI CALCULATION
    # =====================================================

    annual_rate = 8.5

    monthly_rate = annual_rate / (12 * 100)

    months = loan_tenure * 12

    if monthly_rate == 0:

        emi = loan_amount / months

    else:

        emi = (
            loan_amount
            * monthly_rate
            * (1 + monthly_rate) ** months
        ) / (
            ((1 + monthly_rate) ** months) - 1
        )

    emi = round(
        emi,
        2
    )

    # =====================================================
    # SAVE LOAN
    # =====================================================

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO loans
        (
            user_id,
            full_name,
            age,
            gender,
            marital_status,
            mobile,
            email,
            address,
            employment_type,
            monthly_income,
            loan_type,
            loan_amount,
            loan_tenure,
            purpose,
            credit_score,
            eligibility_score,
            emi,
            suggested_loan_amount,
            result
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            current_user_id,
            full_name,
            age,
            gender,
            marital_status,
            mobile,
            email,
            address,
            employment_type,
            monthly_income,
            loan_type,
            loan_amount,
            loan_tenure,
            purpose,
            credit_score,
            eligibility_score,
            emi,
            suggested_loan_amount,
            result
        )
    )

    saved_loan_id = cursor.lastrowid

    conn.commit()

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    cursor.execute(
        """
        SELECT *
        FROM loans
        WHERE id = ?
        """,
        (saved_loan_id,)
    )

    saved_loan = cursor.fetchone()

    conn.close()

    print("--------------------------------")
    print("LOAN SAVED SUCCESSFULLY")
    print("LOAN ID:", saved_loan_id)
    print("USER ID:", current_user_id)
    print("CUSTOMER:", full_name)
    print("DATABASE:", DATABASE)
    print("DATABASE SAVE:", saved_loan is not None)
    print("--------------------------------")

    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template(
        "result.html",

        full_name=full_name,
        age=age,
        gender=gender,
        marital_status=marital_status,
        mobile=mobile,
        email=email,
        address=address,
        employment_type=employment_type,
        monthly_income=monthly_income,
        loan_type=loan_type,
        loan_amount=loan_amount,
        loan_tenure=loan_tenure,
        purpose=purpose,
        credit_score=credit_score,
        eligibility_score=eligibility_score,
        emi=emi,
        suggested_loan_amount=suggested_loan_amount,
        result=result
    )


# =========================================================
# EMI CALCULATOR
# =========================================================

@app.route("/emi", methods=["GET", "POST"])
def emi():

    if "user_id" not in session:

        return redirect(url_for("login"))

    emi_value = None
    total = None
    interest = None

    if request.method == "POST":

        amount = float(
            request.form["amount"]
        )

        rate = float(
            request.form["rate"]
        )

        years = int(
            request.form["years"]
        )

        months = years * 12

        monthly_rate = rate / (12 * 100)

        if monthly_rate == 0:

            emi_value = amount / months

        else:

            emi_value = (
                amount
                * monthly_rate
                * (1 + monthly_rate) ** months
            ) / (
                ((1 + monthly_rate) ** months) - 1
            )

        total = round(
            emi_value * months,
            2
        )

        interest = round(
            total - amount,
            2
        )

        emi_value = round(
            emi_value,
            2
        )

    return render_template(
        "emi.html",
        emi=emi_value,
        total=total,
        interest=interest
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        error = "Invalid Admin Username or Password"

    return render_template(
        "admin_login.html",
        error=error
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # ALL LOANS
    # =====================================================

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            full_name,
            email,
            loan_type,
            loan_amount,
            credit_score,
            eligibility_score,
            result
        FROM loans
        ORDER BY id DESC
        """
    )

    loans = cursor.fetchall()

    # =====================================================
    # TOTAL USERS
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    )

    total_users = cursor.fetchone()[0]

    # =====================================================
    # TOTAL APPLICATIONS
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM loans
        """
    )

    total_loans = cursor.fetchone()[0]

    # =====================================================
    # APPROVED
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM loans
        WHERE result LIKE '%Approved%'
        """
    )

    approved = cursor.fetchone()[0]

    # =====================================================
    # REJECTED
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM loans
        WHERE result LIKE '%Rejected%'
        """
    )

    rejected = cursor.fetchone()[0]

    # =====================================================
    # PENDING
    # =====================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM loans
        WHERE result NOT LIKE '%Approved%'
        AND result NOT LIKE '%Rejected%'
        """
    )

    pending = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",

        loans=loans,

        total_users=total_users,

        total_loans=total_loans,

        approved=approved,

        rejected=rejected,

        pending=pending
    )


# =========================================================
# APPROVE LOAN
# =========================================================

@app.route("/approve/<int:id>")
def approve(id):

    if "admin" not in session:

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE loans
        SET result = 'Loan Approved by Admin ✅'
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# REJECT LOAN
# =========================================================

@app.route("/reject/<int:id>")
def reject(id):

    if "admin" not in session:

        return redirect(
            url_for("admin_login")
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE loans
        SET result = 'Loan Rejected by Admin ❌'
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )