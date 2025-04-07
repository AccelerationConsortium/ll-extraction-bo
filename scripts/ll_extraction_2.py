# Solvent Extraction Optimization Script
# %pip install ax-platform matplotlib
import matplotlib.pyplot as plt
from ax.service.ax_client import AxClient, ObjectiveProperties
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, needed for 3d projection


# Define extraction evaluation function with proper parameters
def evaluate_extraction(
    aqueous_composition, organic_composition, stirring_speed, stirring_time, temperature
):
    """
    Evaluates the extraction process with the given parameters.

    Parameters:
    - aqueous_composition: Fraction of aqueous solvent (0.0-1.0)
    - organic_composition: Fraction of organic solvent (0.0-1.0)
    - stirring_speed: Speed of stirring in rpm (100-500)
    - stirring_time: Duration of stirring in seconds (10-120)
    - temperature: Temperature during extraction in °C (4-40)

    Returns:
    - Dictionary with metrics for recovery, purity, separation, emulsion, and time
    """
    # This is a placeholder function - in a real scenario, this would
    # be replaced with actual experimental measurements or simulations

    # Example implementation with some realistic relationships:

    # Recovery affected by solvent ratio, stirring and temperature
    R = (
        0.3
        + 0.5 * organic_composition
        + 0.2 * (stirring_speed / 500)
        + 0.1 * (temperature / 40)
    )
    R = min(max(R, 0), 1.0) * 100  # Convert to percentage (0-100%)

    # Purity affected by solvent ratio and temperature
    P = 85 + 10 * aqueous_composition + 5 * (temperature - 20) / 36
    P = min(max(P, 0), 100)  # Limit to valid percentage

    # Separation efficiency affected by stirring and temperature
    S = 0.7 + 0.2 * (1 - stirring_speed / 500) + 0.1 * (temperature - 4) / 36
    S = min(max(S, 0), 1.0) * 100  # Convert to percentage

    # Emulsion formation affected by stirring speed and time
    E = 0.1 + 0.6 * (stirring_speed / 500) + 0.3 * (stirring_time / 120)
    E = min(max(E, 0), 1.0) * 100  # Convert to percentage

    # Total time calculation (base processing time plus separation time)
    T = stirring_time + 50 + 1000 * (1 - S / 100) + 500 * (E / 100)
    T = min(max(T, 0), 2000)  # Reasonable bounds

    return {"recovery": R, "purity": P, "separation": S, "emulsion": E, "total_time": T}


# Initialize Ax client for multi-objective optimization
ax_client = AxClient()

# Define parameters and objectives
ax_client.create_experiment(
    parameters=[
        {"name": "aqueous_composition", "type": "range", "bounds": [0.0, 1.0]},
        {"name": "stirring_speed", "type": "range", "bounds": [100, 500]},
        {"name": "stirring_time", "type": "range", "bounds": [10, 120]},
        {"name": "temperature", "type": "range", "bounds": [4, 40]},
    ],
    objectives={
        "recovery": ObjectiveProperties(minimize=False, threshold=50.0),
        "purity": ObjectiveProperties(minimize=False, threshold=90.0),
        "separation": ObjectiveProperties(minimize=False),
        "emulsion": ObjectiveProperties(minimize=True),
        "total_time": ObjectiveProperties(minimize=True, threshold=1200.0),
    },
    parameter_constraints=[
        # No need for an explicit constraint on aqueous + organic since organic
        # is derived
    ],
)

# Run optimization iterations
num_trials = 30

for i in range(num_trials):
    parameterization, trial_index = ax_client.get_next_trial()

    # Extract parameters
    aqueous_composition = parameterization["aqueous_composition"]
    organic_composition = 1.0 - aqueous_composition  # Enforce composition constraint
    stirring_speed = parameterization["stirring_speed"]
    stirring_time = parameterization["stirring_time"]
    temperature = parameterization["temperature"]

    # Run evaluation
    results = evaluate_extraction(
        aqueous_composition,
        organic_composition,
        stirring_speed,
        stirring_time,
        temperature,
    )

    # Report results
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    # Print progress
    if (i + 1) % 5 == 0:
        print(f"Completed {i+1}/{num_trials} trials")

# Get results
df = ax_client.get_trials_data_frame()
print("\nResults summary:")
print(df)

# Get best parameters
best_parameters, values = ax_client.get_best_parameters()
print("\nBest parameters:")
for param, value in best_parameters.items():
    print(f"{param}: {value}")
print("\nDerived parameter:")
print(f"organic_composition: {1.0 - best_parameters['aqueous_composition']}")

print("\nBest outcomes:")
for metric, value in values.items():
    print(f"{metric}: {value}")

# Plot recovery vs purity
plt.figure(figsize=(10, 8))

# Recovery vs Purity
plt.subplot(2, 2, 1)
plt.scatter(df["recovery"], df["purity"], c=df["total_time"], cmap="viridis")
plt.colorbar(label="Total Time (s)")
plt.xlabel("Recovery (%)")
plt.ylabel("Purity (%)")
plt.axhline(y=90, color="r", linestyle="--", alpha=0.5)  # Purity threshold
plt.axvline(x=50, color="r", linestyle="--", alpha=0.5)  # Recovery threshold

# Separation vs Emulsion
plt.subplot(2, 2, 2)
plt.scatter(df["separation"], df["emulsion"], c=df["total_time"], cmap="viridis")
plt.colorbar(label="Total Time (s)")
plt.xlabel("Separation (%)")
plt.ylabel("Emulsion (%)")

# Temperature vs Stirring Speed
plt.subplot(2, 2, 3)
sc = plt.scatter(
    df["temperature"], df["stirring_speed"], c=df["recovery"], cmap="plasma"
)
plt.colorbar(sc, label="Recovery (%)")
plt.xlabel("Temperature (°C)")
plt.ylabel("Stirring Speed (rpm)")

# Aqueous Composition vs Stirring Time
plt.subplot(2, 2, 4)
sc = plt.scatter(
    df["aqueous_composition"], df["stirring_time"], c=df["purity"], cmap="plasma"
)
plt.colorbar(sc, label="Purity (%)")
plt.xlabel("Aqueous Composition")
plt.ylabel("Stirring Time (s)")

plt.tight_layout()
plt.show()

# Generate 3D plot for key parameters
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

sc = ax.scatter(
    df["aqueous_composition"],
    df["stirring_speed"],
    df["temperature"],
    c=df["recovery"],
    cmap="viridis",
    s=50,
)

ax.set_xlabel("Aqueous Composition")
ax.set_ylabel("Stirring Speed (rpm)")
ax.set_zlabel("Temperature (°C)")
plt.colorbar(sc, label="Recovery (%)")

plt.tight_layout()
plt.show()
