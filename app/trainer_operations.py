from psycopg2 import Error

class TrainerOperations:
    """Handles all trainer-related database operations"""
    
    def __init__(self, db):
        self.db = db
        self.cursor = db.get_cursor()
        self.connection = db.get_connection()
    
    def set_trainer_availability(self, trainer_id, start_time, end_time):
        """Define trainer availability periods with overlap prevention"""
        # Check for overlapping availability
        overlap_query = """
        SELECT 1
        FROM TrainerAvailability
        WHERE trainer_id = %s
          AND (%s < end_time AND %s > start_time);
        """
        try:
            self.cursor.execute(overlap_query, (trainer_id, end_time, start_time))
            if self.cursor.fetchone():
                print("Error: Availability overlaps with existing slots.")
                return False
            
            # Insert new availability
            insert_query = """
            INSERT INTO TrainerAvailability (trainer_id, start_time, end_time, is_booked)
            VALUES (%s, %s, %s, FALSE);
            """
            self.cursor.execute(insert_query, (trainer_id, start_time, end_time))
            self.connection.commit()
            print(f"Availability set successfully from {start_time} to {end_time}")
            return True
            
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def view_schedule(self, trainer_id):
        """View all upcoming PT sessions and classes for the trainer"""
        print("\n=== YOUR UPCOMING SCHEDULE ===")
        
        # Get PT sessions
        pt_query = """
        SELECT pts.session_id, m.first_name, m.last_name, pts.start_time, pts.end_time, pts.status
        FROM PersonalTrainingSession pts
        JOIN Member m ON pts.member_id = m.member_id
        WHERE pts.trainer_id = %s AND pts.start_time >= NOW()
        ORDER BY pts.start_time;
        """
        try:
            self.cursor.execute(pt_query, (trainer_id,))
            pt_sessions = self.cursor.fetchall()
            
            if pt_sessions:
                print("\n--- Personal Training Sessions ---")
                for session in pt_sessions:
                    print(f"Session {session[0]}: {session[1]} {session[2]} | {session[3]} to {session[4]} | Status: {session[5]}")
            else:
                print("\nNo upcoming PT sessions.")
            
            # Get classes
            class_query = """
            SELECT c.class_id, c.class_name, c.start_time, c.end_time, r.room_name, c.capacity
            FROM Class c
            LEFT JOIN Room r ON c.room_id = r.room_id
            WHERE c.trainer_id = %s AND c.start_time >= NOW()
            ORDER BY c.start_time;
            """
            self.cursor.execute(class_query, (trainer_id,))
            classes = self.cursor.fetchall()
            
            if classes:
                print("\n--- Group Classes ---")
                for cls in classes:
                    print(f"Class {cls[0]}: {cls[1]} | {cls[2]} to {cls[3]} | Room: {cls[4]} | Capacity: {cls[5]}")
            else:
                print("\nNo upcoming classes.")
            
            return True
            
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def member_lookup_by_name(self, name):
        """Search for member by name and view their health profile"""
        query = """
        SELECT 
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
        """
        search_pattern = f"%{name}%"
        try:
            self.cursor.execute(query, (search_pattern, search_pattern))
            results = self.cursor.fetchall()
            
            if results:
                print("\n=== MEMBER PROFILE ===")
                for row in results:
                    print(f"Member ID: {row[0]}")
                    print(f"Name: {row[1]} {row[2]}")
                    print(f"Email: {row[3]}")
                    print(f"Fitness Goal: {row[4]}")
                    if row[5]:
                        print(f"\nLatest Health Metrics (as of {row[10]}):")
                        print(f"  Weight: {row[5]} kg")
                        print(f"  Body Fat: {row[6]}%")
                        print(f"  Resting Heart Rate: {row[7]} bpm")
                        print(f"  Blood Pressure: {row[8]}/{row[9]} mmHg")
                    else:
                        print("\nNo health metrics recorded yet.")
                return True
            else:
                print(f"No member found with name matching '{name}'")
                return False
                
        except Error as e:
            print(f"Database Error: {e}")
            return False