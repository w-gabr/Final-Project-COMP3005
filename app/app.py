import psycopg2
from psycopg2 import IntegrityError, Error

connection = psycopg2.connect(
    dbname="Final Project",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
) #connect to the database

cursor = connection.cursor()

def fetchMemberDashboard(member_id):
    SQLquery = """
    SELECT * FROM member_dashboard WHERE member_id = %s;
    """ # Define the SQL query
    cursor.execute(SQLquery, (member_id,)) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

def RegisterMemberToClass(member_id, class_id):
    SQLquery = """
    INSERT INTO ClassRegistration (class_id, member_id)
    VALUES (%s, %s);
    """ # Define the SQL query
    try:
        cursor.execute(SQLquery, (class_id, member_id)) # Execute the query
        connection.commit()
    except Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def add_user(first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at):
    SQLquery ="""
    INSERT INTO Member (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""" # Define the SQL query
    try:
        cursor.execute(SQLquery, (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at)) # Execute the query
        connection.commit()
    except IntegrityError as e: # Catch unique constraint violation
        print("Unique constraint violation: ", e)
        connection.rollback()
    except Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def update_member_info(member_id, phone, fitness_goal):
    SQLquery = """
    UPDATE Member
    SET phone = %s,
        fitness_goal = %s
    WHERE member_id = %s;
    """ # Define the SQL query
    try:
        cursor.execute(SQLquery, (phone, fitness_goal, member_id)) # Execute the query
        connection.commit()
    except psycopg2.Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def input_new_health_metric(member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp):
    SQLquery ="""
    INSERT INTO HealthMetric (member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp)
    VALUES (%s, %s, %s, %s, %s, %s, %s);""" # Define the SQL query
    try:
        cursor.execute(SQLquery, (member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp)) # Execute the query
        connection.commit()
    except psycopg2.Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def schedule_personal_training_session(member_id, trainer_id, start_time, end_time):
    # 1. CHECK: Is the requested session inside the trainer's availability?
    availability_query = """
        SELECT 1
        FROM TrainerAvailability
        WHERE trainer_id = %s
          AND %s >= start_time
          AND %s <= end_time;
    """

    cursor.execute(availability_query, (trainer_id, start_time, end_time))
    is_available = cursor.fetchone()

    if not is_available:
        print("Error: Trainer is not available during this time window.")
        return False


    # 2. CHECK: Prevent overlapping PT sessions
    pt_overlap_query = """
        SELECT 1
        FROM PersonalTrainingSession
        WHERE trainer_id = %s
        AND (
              %s < end_time   
          AND %s > start_time 
        );
    """

    cursor.execute(pt_overlap_query, (trainer_id, start_time, end_time))
    pt_conflict = cursor.fetchone()

    if pt_conflict:
        print("Error: Trainer already has a PT session during this time.")
        return False


    
    class_overlap_query = """
        SELECT 1
        FROM Class
        WHERE trainer_id = %s
        AND (
              %s < end_time
          AND %s > start_time
        );
    """

    cursor.execute(class_overlap_query, (trainer_id, start_time, end_time))
    class_conflict = cursor.fetchone()

    if class_conflict:
        print("Error: Trainer is teaching a class during this time.")
        return False
    SQLquery ="""
    INSERT INTO PersonalTrainingSession (member_id, trainer_id, start_time, end_time, status)
    VALUES (%s, %s, %s, %s, 'scheduled');""" # Define the SQL query
    try:
        cursor.execute(SQLquery, (member_id, trainer_id, start_time, end_time)) # Execute the query
        connection.commit()
    except Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def set_trainer_availability(trainer_id, admin_id, start_time, end_time):
    # 1. First: check for overlap
    overlap_query = """
        SELECT 1
        FROM TrainerAvailability
        WHERE trainer_id = %s
        AND (
            %s < end_time   -- new_start < existing_end
            AND
            %s > start_time -- new_end   > existing_start
        );
    """

    try:
        cursor.execute(overlap_query, (trainer_id, start_time, end_time))
        overlap = cursor.fetchone()

        if overlap:
            print("Error: This availability window overlaps an existing one.")
            return False

        # 2. Insert availability if no overlap
        SQLquery = """
            INSERT INTO TrainerAvailability (trainer_id, admin_id, start_time, end_time, is_booked)
            VALUES (%s, %s, %s, %s, FALSE);
        """

        cursor.execute(SQLquery, (trainer_id, admin_id, start_time, end_time))
        connection.commit()
        print("Availability added successfully.")
        return True

    except Error as e:
        print("Database Error: ", e)
        connection.rollback()
        return False
    
def login_user(conn, email, password, table):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT {table.lower()}_id, password FROM {table} WHERE email = %s;",
            (email,)
        )
        row = cur.fetchone()

        if row is None:
            print("No account with that email.")
            return None

        user_id, stored_password = row

        if stored_password == password:
            print("Login successful!")
            return user_id

        print("Incorrect password.")
        return None

def login_menu(conn):
    print("FITNESS CENTER APP")
    print("-------------------")
    print("1. Member Login/User Registration")
    print("2. Trainer Login")
    print("3. Admin Login")

    choice = input("Choose: ")

    if choice == "1":
        print("1. Login")
        print("2. Register")
        sub_choice = input("Choose: ")
        while True:
            if sub_choice == "1":
                email = input("Email: ")
                password = input("Password: ")
                return ("member", login_user(conn, email, password, "Member"))
            elif sub_choice == "2":
                add_user(
                    first_name=input("First Name: "),
                    last_name=input("Last Name: "),
                    email=input("Email: "),
                    date_of_birth=input("Date of Birth (YYYY-MM-DD): "),
                    gender=input("Gender: "),
                    phone=input("Phone: "),
                    fitness_goal=input("Fitness Goal: "),
                    created_at="NOW()"
                )
                print("Registration successful! Please log in.")
                sub_choice = "1"  
    
    elif choice == "2":
        email = input("Email: ")
        password = input("Password: ")
        return ("trainer", login_user(conn, email, password, "Trainer"))
    elif choice == "3":
        email = input("Email: ")
        password = input("Password: ")
        return ("admin", login_user(conn, email, password, "Admin"))
    else:
        print("Invalid option.")
        return (None, None)

    
    


if __name__ == "__main__":
    role, user_id = login_menu(connection)
    if user_id:
        print(f"Logged in as {role} with ID {user_id}")
        fetchMemberDashboard(user_id)
    else:
        print("Login failed.")
    




    