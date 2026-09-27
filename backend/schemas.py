# ============================================================
# CHURNGUARD API SCHEMAS
# ============================================================


# ============================================================
# SIGNUP VALIDATION
# ============================================================

def validate_signup_data(data):

    required_fields = [
        "username",
        "email",
        "password"
    ]

    for field in required_fields:

        if field not in data:

            return False, f"{field} is required"

    username = str(data["username"]).strip()

    email = str(data["email"]).strip()

    password = str(data["password"])


    if len(username) < 3:

        return False, "Username must contain at least 3 characters"


    if "@" not in email:

        return False, "Invalid email address"


    if len(password) < 6:

        return False, "Password must contain at least 6 characters"


    return True, "Valid"


# ============================================================
# LOGIN VALIDATION
# ============================================================

def validate_login_data(data):

    if "email" not in data:

        return False, "Email is required"

    if "password" not in data:

        return False, "Password is required"


    if not str(data["email"]).strip():

        return False, "Email cannot be empty"


    if not str(data["password"]):

        return False, "Password cannot be empty"


    return True, "Valid"