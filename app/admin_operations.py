from psycopg2 import Error, IntegrityError

class AdminOperations:
    """Handles all administrative database operations"""
    
    def __init__(self, db):
        self.db = db
        self.cursor = db.get_cursor()
        self.connection = db.get_connection()
    
    def manage_room_booking(self, room_id, class_id, start_time, end_time):
        """Assign room to a class with conflict checking"""
        # Check for room booking conflicts
        conflict_query = """
        SELECT 1
        FROM Class
        WHERE room_id = %s
          AND (%s < end_time AND %s > start_time)
          AND class_id != %s;
        """
        try:
            self.cursor.execute(conflict_query, (room_id, end_time, start_time, class_id))
            if self.cursor.fetchone():
                print("Error: Room is already booked during this time.")
                return False
            
            # Update class with room assignment
            update_query = """
            UPDATE Class
            SET room_id = %s
            WHERE class_id = %s;
            """
            self.cursor.execute(update_query, (room_id, class_id))
            self.connection.commit()
            print(f"Room {room_id} successfully assigned to class {class_id}")
            return True
            
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def create_class(self, trainer_id, admin_id, room_id, class_name, description, start_time, end_time, capacity):
        """Create a new group fitness class"""
        query = """
        INSERT INTO Class (trainer_id, admin_id, room_id, class_name, description, start_time, end_time, capacity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING class_id;
        """
        try:
            # Check trainer availability
            trainer_check = """
            SELECT 1 FROM Class
            WHERE trainer_id = %s AND (%s < end_time AND %s > start_time);
            """
            self.cursor.execute(trainer_check, (trainer_id, end_time, start_time))
            if self.cursor.fetchone():
                print("Error: Trainer has conflicting class during this time.")
                return False
            
            # Check room availability
            room_check = """
            SELECT 1 FROM Class
            WHERE room_id = %s AND (%s < end_time AND %s > start_time);
            """
            self.cursor.execute(room_check, (room_id, end_time, start_time))
            if self.cursor.fetchone():
                print("Error: Room is already booked during this time.")
                return False
            
            # Insert the class
            self.cursor.execute(query, (trainer_id, admin_id, room_id, class_name, description, start_time, end_time, capacity))
            class_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"Class '{class_name}' created successfully! Class ID: {class_id}")
            return True
            
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def update_class(self, class_id, field, new_value):
        """Update class details (name, description, capacity, etc.)"""
        allowed_fields = ['class_name', 'description', 'start_time', 'end_time', 'capacity', 'room_id', 'trainer_id']
        if field not in allowed_fields:
            print(f"Error: Cannot update '{field}'. Allowed fields: {', '.join(allowed_fields)}")
            return False
        
        query = f"UPDATE Class SET {field} = %s WHERE class_id = %s;"
        try:
            self.cursor.execute(query, (new_value, class_id))
            if self.cursor.rowcount == 0:
                print(f"No class found with ID {class_id}")
                return False
            self.connection.commit()
            print(f"Class {class_id} updated: {field} = {new_value}")
            return True
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def cancel_class(self, class_id):
        """Cancel/delete a class"""
        query = "DELETE FROM Class WHERE class_id = %s;"
        try:
            self.cursor.execute(query, (class_id,))
            if self.cursor.rowcount == 0:
                print(f"No class found with ID {class_id}")
                return False
            self.connection.commit()
            print(f"Class {class_id} has been cancelled and removed.")
            return True
        except Error as e:
            print(f"Database Error: {e}")
            self.connection.rollback()
            return False
    
    def view_all_classes(self):
        """View all scheduled classes with registration counts"""
        query = """
        SELECT 
            c.class_id, 
            c.class_name, 
            t.first_name || ' ' || t.last_name AS trainer_name,
            r.room_name,
            c.start_time,
            c.end_time,
            COUNT(cr.member_id) AS registered,
            c.capacity
        FROM Class c
        LEFT JOIN Trainer t ON c.trainer_id = t.trainer_id
        LEFT JOIN Room r ON c.room_id = r.room_id
        LEFT JOIN ClassRegistration cr ON c.class_id = cr.class_id
        GROUP BY c.class_id, c.class_name, t.first_name, t.last_name, r.room_name, c.start_time, c.end_time, c.capacity
        ORDER BY c.start_time;
        """
        try:
            self.cursor.execute(query)
            classes = self.cursor.fetchall()
            
            if classes:
                print("\n=== ALL CLASSES ===")
                for cls in classes:
                    print(f"ID: {cls[0]} | {cls[1]} | Trainer: {cls[2]} | Room: {cls[3]}")
                    print(f"  Time: {cls[4]} to {cls[5]} | Registered: {cls[6]}/{cls[7]}")
                    print()
                return True
            else:
                print("No classes scheduled.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def view_all_rooms(self):
        """View all available rooms"""
        query = "SELECT room_id, room_name, room_type, capacity, location FROM Room ORDER BY room_id;"
        try:
            self.cursor.execute(query)
            rooms = self.cursor.fetchall()
            
            if rooms:
                print("\n=== AVAILABLE ROOMS ===")
                for room in rooms:
                    print(f"ID: {room[0]} | {room[1]} | Type: {room[2]} | Capacity: {room[3]} | Location: {room[4]}")
                return True
            else:
                print("No rooms available.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False
    
    def view_all_trainers(self):
        """View all trainers"""
        query = """
        SELECT trainer_id, first_name, last_name, specialty, hourly_rate, email
        FROM Trainer
        ORDER BY trainer_id;
        """
        try:
            self.cursor.execute(query)
            trainers = self.cursor.fetchall()
            
            if trainers:
                print("\n=== ALL TRAINERS ===")
                for trainer in trainers:
                    print(f"ID: {trainer[0]} | {trainer[1]} {trainer[2]} | Specialty: {trainer[3]} | Rate: ${trainer[4]}/hr | Email: {trainer[5]}")
                return True
            else:
                print("No trainers found.")
                return False
        except Error as e:
            print(f"Database Error: {e}")
            return False