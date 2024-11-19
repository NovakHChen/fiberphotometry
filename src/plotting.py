import numpy as np


class FP_Plotting:
    def __init__(self, width: float = 0.35):
        self.width = width
        self.colors = {
            "Control": "#7B9FAB",
            "PCB": "#B7C3D0",
            "Points": "#4F4F4F",
            "Saline": "#3B87AB",
        }

    def plot_bar(
        self,
        ax,
        x,
        y,
        color,
        label=None,
        width=None,
        x_label=None,
        y_label=None,
        title=None,
    ):
        """Plots a bar graph.

        Parameters:
        ----------
        ax: matplotlib.axes.Axes
            The axes to plot the bar graph on.
        x: list
            The x values to plot.
        y: list
            The y values to plot.
        color: str | list
            The color of the bar graph.
        label: str, optional
            The label of the bar graph.
        x_label: str, optional
            The x label of the bar graph.
        y_label: str, optional
            The y label of the bar graph.
        title: str, optional
            The title of the bar graph.
        """
        if width is None:
            width = self.width

        ax.bar(x, y, label=label, color=color, width=width)
        ax.set_xlabel(x_label) if x_label is not None else None
        ax.set_ylabel(y_label) if y_label is not None else None
        ax.set_title(title) if title is not None else None

    def plot_barByGroup(self, ax, x, y, groups):
        """Plots a bar graph by group.

        Parameters:
        ----------
        ax: matplotlib.axes.Axes
            The axes to plot the bar graph on.
        y: dict
            The y values to plot where each key is based on the label. Ex. {"Control": [1, 2, 3], "PCB": [4, 5, 6]}
        groups: list
            The groups to plot. Ex. ["Control", "PCB"]
        """
        for group in groups:
            self.plot_bar(
                ax,
                x=x - self.width / 2,
                y=y[group],
                width=self.width,
                label=group,
                color=self.colors[group],
            )

    def bar_byLabel(self, ax, labels, y, title, x_label, y_label):
        self.plot_bar(
            ax,
            x=labels,
            y=y,
            color=[self.colors[label] for label in labels],
            title=title,
            x_label=x_label,
            y_label=y_label,
        )

    def plot_linked_averages(
        self,
        ax,
        num_averages: int,
        points: list,
        zorder: int = 10,
        linestyle: str = "--",
    ):
        """Plots scatter points on the plot.

        Parameters:
        ----------
        ax: matplotlib.axes.Axes
            The axes to plot the points on.
        num_averages: int
            The number of averages to plot.
        points: list
            The points to plot. Recommended order of list: control_type1, exp_type1, control_type2, exp_type2, etc
        zorder: int, optional
            The zorder of the points.
        linestyle: str, optional
            The linestyle of the points.
        """
        for y in points:
            ax.scatter(
                [self.x[0] - self.width / 2] * len(y),
                y,
                color=self.colors["Points"],
                zorder=zorder,
            )

        for i in range(num_averages):
            for j in range(0, len(points) - 1, 2):  # Step by 2 to get pairs
                ax.plot(
                    [self.x[j // 2] - self.width / 2, self.x[j // 2] + self.width / 2],
                    [points[j][i], points[j + 1][i]],
                    color=self.colors["Points"],
                    linestyle=linestyle,
                )

    def create_ShockLine(self, ax, shock_time=0):
        """Creates a shock line on the plot.

        Args:
            ax (matplotlib.axes.Axes): The axes to plot the shock line on.
            shock_time (int, optional): The time of the shock. Defaults to 0, assuming data for X is time from shock onset.
        """
        ax.axvline(x=shock_time, color="red", linestyle="--", label="Shock")
