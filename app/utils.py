from psycopg2 import Error

class Utils:
    """Utility functions for common queries and helper operations"""
    
    def __init__(self, db):
        self.db = db
        self.cursor = db.get_cursor()
        self.connection = db.get_connection()
    
    def get_classes(self):
        """Display all classes with registration counts"""
        query = """
        SELECT 
            c.class_id, 
            c.class_name,
            c.start_time,
            c.end_time,
            COUNT(cr.member_id) AS total_registered,
            c.capacity,
            t.first_name || ' ' || t.last_name AS trainer_name
        FROM Class c
        LEFT JOIN ClassRegistration cr ON c.class_id = cr.class_id
        LEFT JOIN Trainer t ON c.trainer_id = t.trainer_id
        GROUP BY c.class_id, c.class_name, c.start_time, c.end_time, c.capacity, t.first_name, t.last_name
        ORDER BY c.start_time;
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if results:
                print("\n=== AVAILABLE CLASSES ===")
                for row in results:
                    print(f"ID: {row[0]} | {row[1]} | Trainer: {row[6]}")
                    print(f"  Time: {row[2]} to {row[3]}")
                    print(f"  Registered: {row[4]}/{row[5]}")
                    print()
                return True
            else:
                print("No classes available.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def get_trainer_availability(self):
        """Display available trainer time slots"""
        query = """
        SELECT 
            t.trainer_id, 
            t.first_name, 
            t.last_name, 
            t.specialty, 
            ta.start_time, 
            ta.end_time,
            ta.availability_id
        FROM TrainerAvailability ta
        JOIN Trainer t ON ta.trainer_id = t.trainer_id
        WHERE ta.is_booked = FALSE
        ORDER BY ta.start_time;
        """
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if results:
                print("\n=== AVAILABLE TRAINER SLOTS ===")
                for row in results:
                    print(f"Trainer ID: {row[0]} | {row[1]} {row[2]} | Specialty: {row[3]}")
                    print(f"  Available: {row[4]} to {row[5]}")
                    print()
                return True
            else:
                print("No trainer availability at this time.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def get_member_names_for_lookup(self):
        """Display all member names for trainer lookup"""
        query = "SELECT member_id, first_name, last_name FROM Member ORDER BY last_name, first_name;"
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if results:
                print("\n=== REGISTERED MEMBERS ===")
                for row in results:
                    print(f"ID: {row[0]} | {row[1]} {row[2]}")
                return True
            else:
                print("No members found.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def login_user(self, email, password, table):
        """Authenticate user login"""
        query = f"SELECT {table.lower()}_id, password FROM {table} WHERE email = %s;"
        try:
            self.cursor.execute(query, (email,))
            row = self.cursor.fetchone()

            if row is None:
                print("No account found with that email.")
                return None

            user_id, stored_password = row

            if stored_password == password:
                print("Login successful!")
                return user_id

            print("Incorrect password.")
            return None
        except Error as e:
            print(f"Database Error: {e}")
            return None