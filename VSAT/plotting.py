
import io
import matplotlib.pyplot as plt


def plotting(package_table, min_session_time, device_ID):

    plt.figure(figsize=(9, 21), dpi=800)
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.set_ylim([0, max(min_session_time) - min(min_session_time)])
    ax.set_xlim([0, max(device_ID)])
    ax.yaxis.set_inverted(True)

    coordinatesY = []

    for x_coordinate in device_ID:
        ax.axvline(x=x_coordinate, color="black")

    for package_data in package_table.values():

        x1 = package_data[0]
        x2 = package_data[1]
        y1 = package_data[-1][0] - min(min_session_time)
        y2 = package_data[-1][1] - min(min_session_time)

        coordinatesY.append(y1)
        coordinatesY.append(y2)

        color = "red" if x1 > x2 else "green"
        message = " ".join(package_data[2])

        plt.autoscale(False)
        plt.text(
            ((x2 + x1) / 2), ((y2 + y1) / 2), message, color=color, fontsize=10
        )
        plt.annotate(
            "",
            xy=(x1, y1),
            xytext=(x2, y2),
            arrowprops={"arrowstyle": "<|-", "color": color},
        )

    plt.yticks(coordinatesY, fontsize=1)

    buffer = io.BytesIO()
    buffer.seek(0)
    plt.savefig(buffer, format = "png")
    return buffer.getvalue()


