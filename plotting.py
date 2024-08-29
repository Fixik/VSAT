import io
import cv2
import numpy as np
import matplotlib.pyplot as plt


def design_generation(number_of_devices, background, background_height):
    for x in number_of_devices:
        cv2.line(background, (x, 0), (x, background_height), (0, 0, 0), 10)

        device_name = f"Pep {x}"

        x = (x - int(x * 0.06)) if x == number_of_devices[-1] else x
        x = int(x + max(number_of_devices) * 0.01) if x == number_of_devices[0] else x

        rendering_text(x, 10, device_name, background, 2, (0, 0, 0))


def rendering_text(x, y, text, background, font_size, color, thickness=2):
    cv2.putText(
        background,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_size,
        color,
        thickness=thickness,
    )


def preprocessing(packages, number_of_devices, session_time, mode=False):

    time_block, package_table = [], []

    if mode == True:
        for packageID in range(0, len(packages)):
            x1 = packages[packageID][0]
            x2 = packages[packageID][1]

            min_session_time = min(session_time)

            y1 = int((packages[packageID][-1][0] - min_session_time) * 1000)
            y2 = int((packages[packageID][-1][1] - min_session_time) * 1000)

            for last_id_package in range(0, packageID):
                last_id_package = packageID - 1 - last_id_package
                x = [package_table[last_id_package][0], package_table[last_id_package][1]]

                if x1 in x and x2 in x:
                    yl1 = int((packages[last_id_package][-1][0] - min_session_time) * 1000)
                    yl2 = int((packages[last_id_package][-1][1] - min_session_time) * 1000)

                    if x1 == x[1] and y1 > yl2:
                        y1 += package_table[last_id_package][-1][0] - yl1 + 100
                        y2 += package_table[last_id_package][-1][1] - yl2 + 100
                        break

                    if x1 == x[0] and y1 - yl1 < 50:
                        print(50 -(y1 - yl1))
                        y1 += 50 - (y1 - yl1)
                        y2 += 50 - (y2 - yl2)
                        break
                else:
                    y1 += 50
                    y2 += 50
                    break

            package_table.append([x1, x2, packages[packageID][2], [y1, y2]])
            time_block.append(y1)
            time_block.append(y2)

        return soft_generation(package_table, number_of_devices, time_block)

    else:
        return heavy_generation(packages, session_time, number_of_devices)


def soft_generation(packages, number_of_devices, time_block):

    # высота фона
    background_width = max(number_of_devices)
    background_height = int(max(time_block))
    print(background_height)

    # генерация белых пикселей (фона)
    background = np.zeros((background_height, background_width, 3), np.uint8)
    background.fill(255)

    # отрисовка пояснительных прямых
    design_generation(number_of_devices, background, background_height)

    for package in packages:

        x1, x2 = package[0], package[1]
        y1, y2 = package[-1][0], package[-1][1]

        package_data = " ".join(package[2])

        color = (0, 153, 0) if x1 < x2 else (0, 0, 255)

        rendering_text(x1, y1, str(y1), background, 0.5, (0, 0, 0))
        rendering_text(x2, y2, str(y2), background, 0.5, (0, 0, 0))
        rendering_text(
            int((x1 + x2) / 2),
            int((y1 + y2) / 2),
            package_data,
            background,
            2,
            color,
            5,
        )
        cv2.arrowedLine(background, (x1, y1), (x2, y2), color, 5, tipLength=0.01)

    return background


def heavy_generation(package_table, min_session_time, device_ID):

    plt.figure(figsize=(9, 21), dpi=800)
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.set_ylim([0, max(min_session_time) - min(min_session_time)])
    ax.set_xlim([0, max(device_ID)])
    ax.yaxis.set_inverted(True)

    coordinatesY = []

    for x_coordinate in device_ID:
        ax.axvline(x=x_coordinate, color="black")

    for package_data in package_table:

        x1 = package_data[0]
        x2 = package_data[1]
        y1 = package_data[-1][0] - min(min_session_time)
        y2 = package_data[-1][1] - min(min_session_time)

        coordinatesY.append(y1)
        coordinatesY.append(y2)

        color = "red" if x1 > x2 else "green"
        message = " ".join(package_data[2])

        plt.autoscale(False)
        plt.text(((x2 + x1) / 2), ((y2 + y1) / 2), message, color=color, fontsize=10)
        plt.annotate(
            "",
            xy=(x1, y1),
            xytext=(x2, y2),
            arrowprops={"arrowstyle": "<|-", "color": color},
        )

    plt.yticks(coordinatesY, fontsize=1)

    buffer = io.BytesIO()
    buffer.seek(0)
    plt.savefig(buffer, format="png")
    return buffer.getvalue()



