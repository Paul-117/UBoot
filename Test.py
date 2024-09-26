import math
import numpy as np

# Define the torpedo's position and heading
x_T = 0
y_T = -100
phi_T = 3  # Torpedo heading (0 degrees = positive y direction)
Torpedo = (x_T, y_T, phi_T)

# Define the ship's position and heading
x_S = 0
y_S = 0
phi_S = 0  # Ship heading (90 degrees = positive x direction)
Ship = (x_S, y_S, phi_S)

# Safety distance for torpedo boundaries
torpedo_safety_distance = 50  # 50 units for torpedo safety distance

# Calculate safety boundaries based on the torpedo's heading
dy = math.sin(math.radians(phi_T)) * torpedo_safety_distance
dx = math.cos(math.radians(phi_T)) * torpedo_safety_distance

# Calculate the left and right boundaries for safety
saftey_L = (x_T - dx, y_T + dy, phi_T)  # Left safety boundary
saftey_R = (x_T + dx, y_T - dy, phi_T)  # Right safety boundary
#saftey_L = (50,150,45)
print("Left Safety Boundary:", saftey_L)
print("Right Safety Boundary:", saftey_R)

# Generate possible courses for the ship
ship_possible_courses = []

for i in range(4):
    ship_possible_courses.append([x_S, y_S, phi_S + i * 90])  # 0, 90, 180, 270 degrees


def check_intersection(V1, V2, threashold):
    
    x1, y1, phi1 = V1  # Ship's position and heading
    x2, y2, phi2 = V2  # Torpedo's position and heading
    
    # Direction vectors based on the headings
    dir1 = (np.sin(np.radians(phi1)), np.cos(np.radians(phi1)))  # Ship direction
    dir2 = (np.sin(np.radians(phi2)), np.cos(np.radians(phi2)))  # Torpedo direction
    
    #print(dir1, dir2)
    # Setup the matrix A and vector B for solving
    A = np.array([[dir1[0], -dir2[0]], 
                  [dir1[1], -dir2[1]]])
    B = np.array([x2 - x1, 
                  y2 - y1])

    try:
        # Solve for t1 and t2
        t1, t2 = np.linalg.solve(A, B)
        #print(t1,t2)
        if t1 > 0 and t2 > 0 and t2 < threashold:
            return True
        else: 
            return False
    except np.linalg.LinAlgError:
        return False  # The lines are parallel or identical


  # Define a separate safety distance for collision checks

# Function to find the closest angle
def find_closest_angle(angles, phi):
    # Extract the last element (angle) from each sub-list
    angle_values = [angle[2] for angle in angles]
    
    # Calculate the absolute differences
    differences = [min((angle - phi) % 360, (phi - angle) % 360) for angle in angle_values]
    
    # Get the index of the minimum difference
    closest_index = np.argmin(differences)
    
    return angles[closest_index]  # Return the whole sub-list for the closest angle
'''
# Example Usage
C1 = (0, 0, 90)  # Ship: starting at (0, 0), heading right (90 degrees)
print(saftey_L)
C2 = (saftey_L)  # Torpedo: starting at (50, -100), heading up (0 degrees)
collision = check_intersection(C1, C2, 500)
print("Collision:", collision)

'''
collision_safety_distance = 500  # Safety distance for collision checks  

evasive_courses = []
# Check each possible course of the ship against the left safety boundary of the torpedo
for course in ship_possible_courses:
    #check_L = False
    print("Course Ship:", course, "Course Torpedo (Left Boundary):", saftey_L)
    check_L = check_intersection(course, saftey_L, collision_safety_distance)  # Use distinct collision safety distance
    print("Course Ship:", course, "Course Torpedo (Right Boundary):", saftey_R)
    check_R = check_intersection(course, saftey_R, collision_safety_distance)  # Use distinct collision safety distance
    
    
    if check_L == False and check_R == False:
        evasive_courses.append(course)
print(evasive_courses)

#a = find_closest_angle(evasive_courses, phi_S )
#print(a)
