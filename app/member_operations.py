from psycopg2 import IntegrityError, Error

class MemberOperations:
    """Handles all member-related database operations"""
    
    def __init__(self, db):
        self.db = db
        self.cursor = db.get_cursor()
        self.connection = db.get_connection()
    
    def fetch_member_dashboard(self, member_id):
        """Display member dashboard with health metrics, goals, and activity summary"""
        query = "SELECT * FROM member_dashboard WHERE member_id = %s;"
        try:
            self.cursor.execute(query, (member_id,))
            results = self.cursor.fetchall()
            if results:
                print("\n=== MEMBER DASHBOARD ===")
                for row in results:
                    print(f"ID: {row[0]}")
                    print(f"Name: {row[1]}")
                    print(f"Fitness Goal: {row[2]}")
                    print(f"Classes Registered: {row[3]}")
                    print(f"Training Sessions: {row[4]}")
                    print(f"Last Metric Update: {row[5]}")
                    print(f"Weight: {row[6]} kg")
                    print(f"Body Fat: {row[7]}%")
                return True
            else:
                print("No dashboard data found.")
                return False
        except Error as e:
            print(f"Error fetching dashboard: {e}")
            return False
    
    def register_member_to_class(self, member_id, class_id):
        """Register a member to a group fitness class"""
        query = """
        INSERT INTO ClassRegistration (class_id, member_id)
        VALUES (%s, %s);
        """
        try:
            self.cursor.execute(query, (class_id, member_id))
            self.connection.commit()
            print(f"Successfully registered to class {class_id}!")
            return True
        except IntegrityError as e:
            print(f"Registration failed: {e}")
            print("You may already be registered or the class is full.")
            self.connection.rollback()
            return False
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def add_user(self, first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at):
        """Register a new member to the system"""
        query = """
        INSERT INTO Member (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
            self.cursor.execute(query, (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, created_at))
            self.connection.commit()
            print("User registration successful!")
            return True
        except IntegrityError as e:
            print(f"Registration failed - Email already exists: {e}")
            self.connection.rollback()
            return False
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def update_personal_details(self, member_id, trait, updated_value):
        """Update member personal information (name, email, phone)"""
        allowed_traits = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender']
        if trait not in allowed_traits:
            print(f"Error: Cannot update '{trait}'. Allowed fields: {', '.join(allowed_traits)}")
            return False
        
        query = f"UPDATE Member SET {trait} = %s WHERE member_id = %s;"
        try:
            self.cursor.execute(query, (updated_value, member_id))
            self.connection.commit()
            print(f"Successfully updated {trait} to '{updated_value}'")
            return True
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def update_fitness_goal(self, member_id, fitness_goal):
        """Update member's fitness goal"""
        query = "UPDATE Member SET fitness_goal = %s WHERE member_id = %s;"
        try:
            self.cursor.execute(query, (fitness_goal, member_id))
            self.connection.commit()
            print(f"Fitness goal updated to: '{fitness_goal}'")
            return True
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def input_new_health_metric(self, member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp):
        """Log new health metrics for progress tracking"""
        query = """
        INSERT INTO HealthMetric (member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        try:
            self.cursor.execute(query, (member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp))
            self.connection.commit()
            print("Health metrics recorded successfully!")
            return True
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def schedule_personal_training_session(self, member_id, trainer_id, start_time, end_time):
        """Schedule a personal training session with availability validation"""
        try:
            # 1. Validate trainer availability window
            self.cursor.execute("""
                SELECT availability_id
                FROM TrainerAvailability
                WHERE trainer_id = %s
                  AND %s >= start_time
                  AND %s <= end_time
                  AND is_booked = FALSE
                LIMIT 1;
            """, (trainer_id, start_time, end_time))

            availability = self.cursor.fetchone()
            if availability is None:
                print("Error: Trainer is not available at this time.")
                return False

            availability_id = availability[0]

            # 2. Check trainer PT session conflicts
            self.cursor.execute("""
                SELECT 1
                FROM PersonalTrainingSession
                WHERE trainer_id = %s
                  AND (%s < end_time AND %s > start_time);
            """, (trainer_id, end_time, start_time))

            if self.cursor.fetchone():
                print("Error: Trainer already has a PT session during this time.")
                return False
            
            # 3. Check class conflicts for trainer
            self.cursor.execute("""
                SELECT 1
                FROM Class
                WHERE trainer_id = %s
                  AND (%s < end_time AND %s > start_time);
            """, (trainer_id, end_time, start_time))

            if self.cursor.fetchone():
                print("Error: Trainer already has a class during this time.")
                return False

            # 4. Insert PT session
            self.cursor.execute("""
                INSERT INTO PersonalTrainingSession (member_id, trainer_id, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, 'scheduled')
                RETURNING session_id;
            """, (member_id, trainer_id, start_time, end_time))

            new_session_id = self.cursor.fetchone()[0]

            # 5. Mark availability as booked
            self.cursor.execute("""
                UPDATE TrainerAvailability
                SET is_booked = TRUE
                WHERE availability_id = %s;
            """, (availability_id,))

            self.connection.commit()
            print(f"PT session booked successfully! Session ID: {new_session_id}")
            return True

        except Exception as e:
            self.connection.rollback()
            print(f"Database Error: {e}")
            return False