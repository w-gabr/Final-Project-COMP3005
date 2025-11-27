import sys
from database import Database
from member_operations import MemberOperations
from trainer_operations import TrainerOperations
from admin_operations import AdminOperations
from utils import Utils

def login_menu(utils, db):
    """Display login menu and handle authentication"""
    print("\n" + "="*50)
    print("   HEALTH & FITNESS CLUB MANAGEMENT SYSTEM")
    print("="*50)
    print("\n1. Member Login/Registration")
    print("2. Trainer Login")
    print("3. Admin Login")
    print("4. Exit")
    
    choice = input("\nChoose an option: ")
    
    if choice == "1":
        print("\n--- MEMBER PORTAL ---")
        print("1. Login")
        print("2. Register New Account")
        sub_choice = input("Choose: ")
        
        if sub_choice == "1":
            email = input("Email: ")
            password = input("Password: ")
            return ("member", utils.login_user(email, password, "Member"))
        elif sub_choice == "2":
            print("\n--- NEW MEMBER REGISTRATION ---")
            first_name = input("First Name: ")
            last_name = input("Last Name: ")
            email = input("Email: ")
            password = input("Password: ")
            date_of_birth = input("Date of Birth (YYYY-MM-DD): ")
            gender = input("Gender (M/F/Other): ")
            phone = input("Phone: ")
            fitness_goal = input("Fitness Goal: ")
            
            # Register with password
            db.cursor.execute("""
                INSERT INTO Member (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal, password))
            db.commit()
            
            print("\nRegistration successful! Please log in.")
            return login_menu(utils, db)
    
    elif choice == "2":
        print("\n--- TRAINER LOGIN ---")
        email = input("Email: ")
        password = input("Password: ")
        return ("trainer", utils.login_user(email, password, "Trainer"))
    
    elif choice == "3":
        print("\n--- ADMIN LOGIN ---")
        email = input("Email: ")
        password = input("Password: ")
        return ("admin", utils.login_user(email, password, "Admin"))
    
    elif choice == "4":
        print("\nThank you for using the Fitness Club Management System!")
        sys.exit(0)
    
    else:
        print("Invalid option. Please try again.")
        return (None, None)

def member_menu(member_ops, utils, user_id):
    """Member dashboard menu"""
    while True:
        print("\n" + "="*50)
        print("   MEMBER DASHBOARD")
        print("="*50)
        print("1. Profile Management")
        print("2. Class Registration")
        print("3. Schedule Personal Training Session")
        print("4. View Dashboard")
        print("5. Logout")
        
        choice = input("\nChoose: ")
        
        if choice == "1":
            print("\n--- PROFILE MANAGEMENT ---")
            print("1. Update Personal Details")
            print("2. Update Fitness Goal")
            print("3. Input New Health Metric")
            pm_choice = input("Choose: ")
            
            if pm_choice == "1":
                trait = input("Field to update (first_name, last_name, email, phone): ")
                new_value = input(f"Enter new value for {trait}: ")
                member_ops.update_personal_details(user_id, trait, new_value)
            
            elif pm_choice == "2":
                goal = input("Enter new fitness goal: ")
                member_ops.update_fitness_goal(user_id, goal)
            
            elif pm_choice == "3":
                print("\n--- LOG HEALTH METRICS ---")
                try:
                    weight = float(input("Weight (kg): "))
                    body_fat = float(input("Body Fat (%): "))
                    heart_rate = int(input("Resting Heart Rate (bpm): "))
                    systolic = int(input("Systolic BP (mmHg): "))
                    diastolic = int(input("Diastolic BP (mmHg): "))
                    member_ops.input_new_health_metric(user_id, "NOW()", weight, body_fat, heart_rate, systolic, diastolic)
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
        
        elif choice == "2":
            utils.get_classes()
            try:
                class_id = int(input("\nEnter Class ID to register: "))
                member_ops.register_member_to_class(user_id, class_id)
            except ValueError:
                print("Invalid class ID.")
        
        elif choice == "3":
            utils.get_trainer_availability()
            try:
                trainer_id = int(input("\nEnter Trainer ID: "))
                start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
                end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")
                member_ops.schedule_personal_training_session(user_id, trainer_id, start_time, end_time)
            except ValueError:
                print("Invalid input.")
        
        elif choice == "4":
            member_ops.fetch_member_dashboard(user_id)
        
        elif choice == "5":
            print("\nLogging out...")
            break
        
        else:
            print("Invalid option.")

def trainer_menu(trainer_ops, utils, user_id):
    """Trainer dashboard menu"""
    while True:
        print("\n" + "="*50)
        print("   TRAINER DASHBOARD")
        print("="*50)
        print("1. Set Availability")
        print("2. View Schedule")
        print("3. Member Lookup by Name")
        print("4. Logout")
        
        choice = input("\nChoose: ")
        
        if choice == "1":
            print("\n--- SET AVAILABILITY ---")
            start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
            end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")
            trainer_ops.set_trainer_availability(user_id, start_time, end_time)
        
        elif choice == "2":
            trainer_ops.view_schedule(user_id)
        
        elif choice == "3":
            utils.get_member_names_for_lookup()
            name = input("\nEnter member's first or last name: ")
            trainer_ops.member_lookup_by_name(name)
        
        elif choice == "4":
            print("\nLogging out...")
            break
        
        else:
            print("Invalid option.")
def admin_menu(admin_ops, utils, user_id, db):
    """Admin dashboard menu"""
    while True:
        print("\n" + "="*50)
        print("   ADMIN DASHBOARD")
        print("="*50)
        print("1. Class Management")
        print("2. Room Management")
        print("3. View All Trainers")
        print("4. Logout")
        
        choice = input("\nChoose: ")
        
        if choice == "1":
            print("\n--- CLASS MANAGEMENT ---")
            print("1. Create New Class")
            print("2. Update Class")
            print("3. Cancel Class")
            print("4. View All Classes")
            cm_choice = input("Choose: ")
            
            if cm_choice == "1":
                print("\n--- CREATE NEW CLASS ---")
                admin_ops.view_all_trainers()
                admin_ops.view_all_rooms()
                try:
                    trainer_id = int(input("Trainer ID: "))
                    room_id = int(input("Room ID: "))
                    class_name = input("Class Name: ")
                    description = input("Description: ")
                    start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
                    end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")
                    capacity = int(input("Capacity: "))
                    admin_ops.create_class(trainer_id, user_id, room_id, class_name, description, start_time, end_time, capacity)
                except ValueError:
                    print("Invalid input.")
            
            elif cm_choice == "2":
                admin_ops.view_all_classes()
                try:
                    class_id = int(input("\nClass ID to update: "))
                    field = input("Field to update (class_name, description, capacity, start_time, end_time): ")
                    new_value = input(f"New value for {field}: ")
                    admin_ops.update_class(class_id, field, new_value)
                except ValueError:
                    print("Invalid input.")
            
            elif cm_choice == "3":
                admin_ops.view_all_classes()
                try:
                    class_id = int(input("\nClass ID to cancel: "))
                    confirm = input(f"Confirm cancellation of class {class_id}? (yes/no): ")
                    if confirm.lower() == "yes":
                        admin_ops.cancel_class(class_id)
                except ValueError:
                    print("Invalid input.")
            
            elif cm_choice == "4":
                admin_ops.view_all_classes()
        
        elif choice == "2":
            print("\n--- ROOM MANAGEMENT ---")
            admin_ops.view_all_rooms()
            admin_ops.view_all_classes()
            try:
                class_id = int(input("\nClass ID to assign room: "))
                room_id = int(input("Room ID: "))
                # Get class times
                db.cursor.execute("SELECT start_time, end_time FROM Class WHERE class_id = %s", (class_id,))
                times = db.cursor.fetchone()
                if times:
                    admin_ops.manage_room_booking(room_id, class_id, times[0], times[1])
                else:
                    print("Class not found.")
            except ValueError:
                print("Invalid input.")
        
        elif choice == "3":
            admin_ops.view_all_trainers()
        
        elif choice == "4":
            print("\nLogging out...")
            break
        
        else:
            print("Invalid option.")

if __name__ == "__main__":
    # Initialize database connection
    db = Database()
    
    # Initialize operation modules
    member_ops = MemberOperations(db)
    trainer_ops = TrainerOperations(db)
    admin_ops = AdminOperations(db)
    utils = Utils(db)
    
    try:
        # Main application loop
        while True:
            role, user_id = login_menu(utils, db)
            
            if user_id is None:
                continue
            
            print(f"\nWelcome! Logged in as {role} (ID: {user_id})")
            
            if role == "member":
                member_menu(member_ops, utils, user_id)
            elif role == "trainer":
                trainer_menu(trainer_ops, utils, user_id)
            elif role == "admin":
                admin_menu(admin_ops, utils, user_id, db)
    
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
    
    finally:
        # Close database connection
        db.close()
        print("Goodbye!")