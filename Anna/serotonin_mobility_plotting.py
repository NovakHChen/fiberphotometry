import matplotlib.pyplot as plt
import numpy as np
from src.plotting import FP_Plotting


def plot_serotonin_levels(
    averages, overall_averages, fontSize={"title": 17, "label": 16, "tick": 13}
):
    """
    Plots the average serotonin levels during mobile and immobile states for control and PCB groups.
    Parameters:
    averages (list of dict): A list of dictionaries containing individual serotonin level averages for each condition.
                             Each dictionary should have the keys 'control_mobile', 'control_immobile', 'pcb_mobile', and 'pcb_immobile'.
    overall_averages (dict): A dictionary containing the overall average serotonin levels for each condition.
                             Should have the keys 'control_mobile', 'control_immobile', 'pcb_mobile', and 'pcb_immobile'.
    fontSize (dict): A dictionary containing the font sizes for the title, label, and tick labels.
    Returns:
    None: This function displays a bar plot with scatter points and connecting lines.
    """

    def find_averages(column):
        return [avg[column] for avg in averages]

    categories = ["Mobile", "Immobile"]
    exp_groups = ["Control", "PCB"]

    # Find means by group
    # Ex. {"Control": ..., "PCB": ...}
    meansByGroup = {
        exp_group: [
            overall_averages[f"{exp_group}_{cat}"] for cat in categories.lower()
        ]
        for exp_group in exp_groups
    }

    # Find averages by group and category
    # organized in a list
    # Ex. [control_mobile, control_immobile, pcb_mobile, pcb_immobile]
    avg_points = [
        find_averages(f"{cat}_{state}")
        for cat in exp_groups.lower()
        for state in categories.lower()
    ]

    x = np.arange(len(categories))
    width = 0.35

    plotting = FP_Plotting(x=x, width=width)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bar for means
    plotting.plot_bar(ax, x, meansByGroup, exp_groups)

    # Plot points for averages
    plotting.plot_linked_averages(
        ax=ax,
        num_averages=len(averages),
        points=avg_points,
    )

    ax.set_xlabel("Condition", fontsize=fontSize["label"])
    ax.set_ylabel("Average Serotonin Activity (Z-Score)", fontsize=fontSize["label"])
    ax.set_title(
        "Average Serotonin Level During Mobile and Immobile States",
        fontsize=fontSize["title"],
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=fontSize["tick"])
    ax.legend()

    plt.tight_layout()
    plt.show()


def plot_velocities(
    velocities,
    labels,
):
    """
    Plot a bar graph of velocities.

    Parameters:
    ----------
    velocities : list of float
        List of mean velocities to plot.
    labels : list of str
        Corresponding labels for the velocities.
    """
    plotting = FP_Plotting()
    fig, ax = plt.figure(figsize=(8, 6))
    plotting.bar_byLabel(
        ax,
        labels,
        velocities,
        title="Average Velocity Comparison",
        x_label="Files",
        y_label="Average Velocity",
    )
    plt.show()


def plot_distances(
    distances,
    labels,
):
    """
    Plot a bar graph of distances traveled.

    Parameters:
    ----------
    distances : list of float
        List of total distances to plot.
    labels : list of str
        Corresponding labels for the distances.
    """
    plotting = FP_Plotting()
    fig, ax = plt.figure(figsize=(8, 6))
    plotting.bar_byLabel(
        ax,
        labels,
        distances,
        title="Total Distance Traveled Comparison",
        x_label="Files",
        y_label="Total Distance Traveled",
    )
    plt.show()
