import psycopg2

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
    except psycopg2.Error as e: # Catch database errors
        print("Database Error: ", e)
        connection.rollback()

def add_member(first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at):
    SQLquery ="""
    INSERT INTO Member (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""" # Define the SQL query
    try:
        cursor.execute(SQLquery, (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at)) # Execute the query
        connection.commit()
    except psycopg2.IntegrityError as e: # Catch unique constraint violation
        print("Unique constraint violation: ", e)
        connection.rollback()
    except psycopg2.Error as e: # Catch database errors
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
    except psycopg2.Error as e: # Catch database errors
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

    except psycopg2.Error as e:
        print("Database Error: ", e)
        connection.rollback()
        return False


def get_personal_training_sessions(trainer_id):
        cursor.execute("""
            SELECT session_id, member_id, start_time, end_time, status
            FROM PersonalTrainingSession
            WHERE trainer_id = %s
            ORDER BY start_time;
        """, (trainer_id,))
        return cursor.fetchall()

def get_classes_by_trainer(trainer_id):
        cursor.execute("""
            SELECT class_id, class_name, start_time, end_time, capacity
            FROM Class
            WHERE trainer_id = %s           
        """, (trainer_id,))
        return cursor.fetchall()

input_new_health_metric(4, '2025-10-15 10:00', 80.0, 20.0, 70, 120, 80)
RegisterMemberToClass(4, 1)
fetchMemberDashboard(4)