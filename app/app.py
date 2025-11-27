import sys
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

"""===============FUNCTIONS FOR MEMBER ROLE==============="""
def fetch_member_dashboard(member_id):
    SQLquery = """
    SELECT * FROM member_dashboard WHERE member_id = %s;
    """ # Define the SQL query
    cursor.execute(SQLquery, (member_id,)) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

def register_member_to_class(member_id, class_id):
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

def update_personal_details(member_id, trait, updated_value):
    SQLquery = f"""
    UPDATE Member
    SET {trait} = %s
    WHERE member_id = %s;
    """ # Define the SQL query
    try:
        cursor.execute(SQLquery, (updated_value, member_id)) # Execute the query
        connection.commit()
    except psycopg2.Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def uppdate_fitness_goal(member_id, fitness_goal):
    SQLquery = """
    UPDATE Member
    SET fitness_goal = %s
    WHERE member_id = %s;
    """ # Define the SQL query
    try:
        cursor.execute(SQLquery, (fitness_goal, member_id)) # Execute the query
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
    try:
            # 1. Validate trainer availability window
            cursor.execute("""
                SELECT availability_id
                FROM TrainerAvailability
                WHERE trainer_id = %s
                  AND %s >= start_time
                  AND %s <= end_time
                  AND is_booked = FALSE
                LIMIT 1;
            """, (trainer_id, start_time, end_time))

            availability = cursor.fetchone()
            if availability is None:
                print("Trainer is not available at this time.")
                return False

            availability_id = availability[0]

            # 2. Check trainer PT session conflicts
            cursor.execute("""
                SELECT 1
                FROM PersonalTrainingSession
                WHERE trainer_id = %s
                  AND (%s < end_time AND %s > start_time);
            """, (trainer_id, end_time, start_time))

            if cursor.fetchone():
                print("Trainer already has a PT session during this time.")
                return False
            
            # 3. Check class conflicts for trainer
            cursor.execute("""
                SELECT 1
                FROM Class
                WHERE trainer_id = %s
                  AND (%s < end_time AND %s > start_time);
            """, (trainer_id, end_time, start_time))

            if cursor.fetchone():
                print("Trainer already has a class during this time.")
                return False

            # 4. Insert PT session
            cursor.execute("""
                INSERT INTO PersonalTrainingSession (member_id, trainer_id, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, 'scheduled')
                RETURNING session_id;
            """, (member_id, trainer_id, start_time, end_time))

            new_session_id = cursor.fetchone()[0]

            # 5. Mark availability as booked
            cursor.execute("""
                UPDATE TrainerAvailability
                SET is_booked = TRUE
                WHERE availability_id = %s;
            """, (availability_id,))

            connection.commit()
            print("PT session booked successfully! Session ID:", new_session_id)
            return True

    except Exception as e:
        connection.rollback()
        print("Database Error:", e)
        return False
"""===============FUNCTIONS FOR TRAINER ROLE==============="""
def set_trainer_availability(trainer_id, start_time, end_time):
    overlap_query = """
    SELECT 1
    FROM TrainerAvailability
    WHERE trainer_id = %s
      AND (%s < end_time AND %s > start_time); """ # Define the SQL query to check for overlaps
    cursor.execute(overlap_query, (trainer_id, end_time, start_time)) # Execute the overlap check query
    if cursor.fetchone():
        print("Error: Availability overlaps with existing slots.")
        return
    
    SQLquery ="""
    INSERT INTO TrainerAvailability (trainer_id, start_time, end_time, is_booked)
    VALUES (%s, %s, %s, FALSE);""" # Define the SQL query
    try:
        cursor.execute(SQLquery, (trainer_id, start_time, end_time)) # Execute the query
        connection.commit()
    except psycopg2.Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def member_lookup_by_name(name):
    SQLquery = """SELECT 
                    m.member_id,
                    m.first_name,
                    m.last_name,
                    m.email,
                    m.fitness_goal,
                    h.weight_kg,
                    h.body_fat_pct,
                    h.resting_heart_rate,
                    h.systolic_bp,
                    h.diastolic_bp,
                    h.recorded_at
                FROM Member m
                LEFT JOIN HealthMetric h ON m.member_id = h.member_id
                WHERE m.first_name ILIKE %s OR m.last_name ILIKE %s
                ORDER BY h.recorded_at DESC
                LIMIT 1;
            """ # Define the SQL query
    search_pattern = f"%{name}%"
    cursor.execute(SQLquery, (search_pattern, search_pattern)) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

"""===============ADDITIONAL QUERIES for CLI==============="""
def get_classes():
    SQLquery = """SELECT 
    Class.class_id, 
    Class.class_name, 
    COUNT(ClassRegistration.member_id) AS total_registered,
    Class.capacity
    FROM ClassRegistration
    JOIN Class ON ClassRegistration.class_id = Class.class_id
    GROUP BY Class.class_id, Class.class_name
    ORDER BY Class.class_id;"""
 # Define the SQL query
    cursor.execute(SQLquery) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

def get_trainer_avaiability():
    SQLquery = """
    SELECT T.trainer_id, T.first_name, T.last_name, T.specialty, TA.start_time, TA.end_time
    FROM TrainerAvailability as TA JOIN Trainer T ON TA.trainer_id = T.trainer_id
    WHERE TA.is_booked = FALSE;
    """ # Define the SQL query
    cursor.execute(SQLquery) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

def get_member_names_for_lookup():
    SQLquery = """SELECT first_name, last_name FROM Member;""" # Define the SQL query
    cursor.execute(SQLquery) # Execute the query
    results = cursor.fetchall() # Fetch all results
    for row in results:
        print(row)

"""===============LOGIN MENU FUNCTION==============="""   
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
    else:
        print("Login failed.")
        sys.exit()
        
    if role == "member":
        print("1. Profile Management")
        print("2. Class Registration")
        print("3. Schedule Personal Training Session")
        print("4. View Dashboard")
        print("5. Logout")
        member_choice = input("Choose: ")
        while member_choice != "5":
            if member_choice == "1":
                print("1. Update Personal Details")
                print("2. Update Fitness Goal")
                print("3. Input New Health Metric")
                pm_choice = input("Choose: ")
                if pm_choice == "2":
                    goal = input("Enter new fitness goal: ")
                    uppdate_fitness_goal(user_id, goal)
                elif pm_choice == "1":
                    trait = input("Trait to update (first_name, last_name, email, phone): ")
                    new_value = input(f"Enter new value for {trait}: ")
                    update_personal_details(user_id, trait, new_value)
                elif pm_choice == "3":
                    input_new_health_metric(
                        member_id=user_id,
                        recorded_at="NOW()",
                        weight_kg=float(input("Weight (kg): ")),
                        body_fat_pct=float(input("Body Fat (%): ")),
                        resting_heart_rate=int(input("Resting Heart Rate (bpm): ")),
                        systolic_bp=int(input("Systolic BP (mmHg): ")),
                        diastolic_bp=int(input("Diastolic BP (mmHg): "))
                    )
            elif member_choice == "2":
                print("class ID | class Name | total registered | capacity")
                get_classes()
                class_id = int(input("Enter Class ID to register: "))
                register_member_to_class(user_id, class_id)
            elif member_choice == "3":
                print("ID | first name | last name | specialty | start time | end time")
                get_trainer_avaiability()
                trainer_id = int(input("Trainer ID: "))
                start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
                end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")
                schedule_personal_training_session(user_id, trainer_id, start_time, end_time)
            elif member_choice == "4":
                print("name | upcoming PT sessions | total classes attended | avg health metrics")
                fetch_member_dashboard(user_id)
            print("1. Profile Management")
            print("2. Class Registration")
            print("3. Schedule Personal Training Session")
            print("4. View Dashboard")
            print("5. Logout")
            member_choice = input("Choose: ")   
    elif role == "trainer":
        print("1. Set Availability")
        print("2. Schedule Viewing")
        print("3. Member Lookup by Name")
        print("4. Logout")
        trainer_choice = input("Choose: ")
        while trainer_choice != "4":
            if trainer_choice == "1":
                start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
                end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")
                set_trainer_availability(user_id, start_time, end_time)
            elif trainer_choice == "2":
                print("Trainer schedule viewing not yet implemented.")
            elif trainer_choice == "3":
                print("Available member names for lookup:")
                get_member_names_for_lookup()
                name = input("Enter member's first or last name to lookup: ")
                print("member_id | first_name | last_name | email | fitness_goal | weight_kg | body_fat_pct | resting_heart_rate | systolic_bp | diastolic_bp | recorded_at")
                member_lookup_by_name(name)
            print("1. Member Lookup by Name")
            print("2. Logout")
            trainer_choice = input("Choose: ")
    




    