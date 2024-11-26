import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data from the .txt file
file_path = "data.txt"  # Replace with the path to your file
columns = ['Replication', 'X1', 'Y1', 'X2', 'Y2']
df = pd.read_csv(file_path, sep="\t", skipinitialspace=True, header=None, names=columns)

# Convert X1, Y1, X2, Y2 to numeric, coercing errors to NaN
df['X1'] = pd.to_numeric(df['X1'], errors='coerce')
df['Y1'] = pd.to_numeric(df['Y1'], errors='coerce')
df['X2'] = pd.to_numeric(df['X2'], errors='coerce')
df['Y2'] = pd.to_numeric(df['Y2'], errors='coerce')

# Get unique replications
replications = df["Replication"].unique()

# Create a colormap to assign a distinct color for each replication
colors = plt.colormaps["tab10"].colors

# Plotting
plt.figure(figsize=(12, 8))

# To store the parabola coefficients and R^2 values for output
output_data = []

for i, replication in enumerate(replications):
    subset = df[df["Replication"] == replication]
    
    # Use color for each replication
    color = colors[i % len(colors)]
    
    # Line 1: Fit parabola for X1, Y1
    line1 = subset.dropna(subset=["X1", "Y1"])
    if not line1.empty:
        coeffs_line1 = np.polyfit(line1["X1"], line1["Y1"], 2)
        x1_fit = np.linspace(min(line1["X1"]), max(line1["X1"]), 100)
        y1_fit = np.polyval(coeffs_line1, x1_fit)
        plt.scatter(line1["X1"], line1["Y1"], s=50, color=color)
        plt.plot(x1_fit, y1_fit, label=f"{replication}", linestyle="--", color=color)
        
        # Calculate R^2 for Line 1
        y1_predicted = np.polyval(coeffs_line1, line1["X1"])
        ss_residual_1 = np.sum((line1["Y1"] - y1_predicted) ** 2)
        ss_total_1 = np.sum((line1["Y1"] - np.mean(line1["Y1"])) ** 2)
        r2_line1 = 1 - ss_residual_1 / ss_total_1
        
        # Calculate center of parabola (vertex) for Line 1
        a1, b1, c1 = coeffs_line1
        x1_center = -b1 / (2 * a1)
        y1_center = np.polyval(coeffs_line1, x1_center)

    # Line 2: Fit parabola for X2, Y2
    line2 = subset.dropna(subset=["X2", "Y2"])
    if not line2.empty:
        coeffs_line2 = np.polyfit(line2["X2"], line2["Y2"], 2)
        x2_fit = np.linspace(min(line2["X2"]), max(line2["X2"]), 100)
        y2_fit = np.polyval(coeffs_line2, x2_fit)
        plt.scatter(line2["X2"], line2["Y2"], s=50, color=color)
        plt.plot(x2_fit, y2_fit, linestyle=":", color=color)
        
        # Calculate R^2 for Line 2
        y2_predicted = np.polyval(coeffs_line2, line2["X2"])
        ss_residual_2 = np.sum((line2["Y2"] - y2_predicted) ** 2)
        ss_total_2 = np.sum((line2["Y2"] - np.mean(line2["Y2"])) ** 2)
        r2_line2 = 1 - ss_residual_2 / ss_total_2
        
        # Calculate center of parabola (vertex) for Line 2
        a2, b2, c2 = coeffs_line2
        x2_center = -b2 / (2 * a2)
        y2_center = np.polyval(coeffs_line2, x2_center)
        
        # Calculate the differences in center points (x and y) between Line 1 and Line 2
        center_diff_x = abs(x1_center - x2_center)
        center_diff_y = abs(y1_center - y2_center)
        
        # Append the data for output
        output_data.append({
            "Replication": replication,
            "Line1_Coefficients": coeffs_line1.tolist(),
            "Line2_Coefficients": coeffs_line2.tolist(),
            "R2_Line1": r2_line1,
            "R2_Line2": r2_line2,
            "Center_Difference_X": center_diff_x,
            "Center_Difference_Y": center_diff_y
        })

# Add plot details
plt.title("Fitted Parabolas for Multiple Replications")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.grid(True)
plt.show()

# Save the DataFrame to an Excel file
output_file_path = "output_data.xlsx"  # Replace with your desired output file path
output_df = pd.DataFrame(output_data)
output_df.to_excel(output_file_path, index=False)

print(f"Data saved to {output_file_path}")
