import numpy as np

def check_intersection(V1, V2, threashold):
    
    x1, y1, phi1 = V1  # Ship's position and heading
    x2, y2, phi2 = V2  # Torpedo's position and heading
    
    # Direction vectors based on the headings
    dir1 = (np.sin(np.radians(phi1)), np.cos(np.radians(phi1)))  # Ship direction
    dir2 = (np.sin(np.radians(phi2)), np.cos(np.radians(phi2)))  # Torpedo direction
    
    print(dir1, dir2)
    # Setup the matrix A and vector B for solving
    A = np.array([[dir1[0], -dir2[0]], 
                  [dir1[1], -dir2[1]]])
    B = np.array([x2 - x1, 
                  y2 - y1])

    try:
        # Solve for t1 and t2
        t1, t2 = np.linalg.solve(A, B)
        print(t1,t2)
        if t1 > 0 and t2 > 0 and t2 < threashold:
            return True
        else: 
            return False
    except np.linalg.LinAlgError:
        return False  # The lines are parallel or identical

# Example Usage
C1 = (0, 0, 90)  # Ship: starting at (0, 0), heading right (90 degrees)
C2 = (100, -100, 90)  # Torpedo: starting at (50, -100), heading up (0 degrees)
collision = check_intersection(C1, C2, 500)
print("Collision:", collision)
