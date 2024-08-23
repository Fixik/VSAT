import pyshark
from PIL import Image
from io import BytesIO
from plotting import plotting


package_table = {}
device_ID = [0]
min_session_time = []
increasing_device_id = 100
rst_package_id = 0


def FlagDefinition(packetTCP):

    box = {}
    returned_block = []
    box["ns"] = packetTCP.flags_ns
    box["cwr"] = packetTCP.flags_cwr
    box["ecn"] = packetTCP.flags_ecn
    box["urg"] = packetTCP.flags_urg
    box["push"] = packetTCP.flags_push
    box["reset"] = packetTCP.flags_reset
    box["syn"] = packetTCP.flags_syn
    box["fin"] = packetTCP.flags_fin
    box["ack"] = packetTCP.flags_ack

    for name, value in box.items():
        if int(value) == 1:
            returned_block.append(str(name))

    return returned_block


def ReadingFiles(file_paths):

    global min_session_time, package_table, device_ID, increasing_device_id, rst_package_id
    block_package_table = {}
    minimum_block_time = []
    rst_packages = []

    for way in file_paths:

        captured_packages = pyshark.FileCapture(f"pcap/{way}", display_filter="tcp")

        for package in captured_packages:
            package_id = str(package["IP"].id)

            mac_source = str(package["ETH"].src)
            mac_destination = str(package["ETH"].dst)

            tcp_seq = str(package["tcp"].seq_raw)
            tcp_ack = str(package["tcp"].ack_raw)

            package_flags = FlagDefinition(package.tcp)
            package_id = package_id + tcp_seq + tcp_ack

            minimum_time_value = float(package.frame_info.time_epoch)

            min_session_time.append(minimum_time_value)

            if len(minimum_block_time) == 0:
                minimum_block_time.append(minimum_time_value)
                minimum_block_time.append(mac_source)

            elif (
                len(minimum_block_time) == 2
                and minimum_block_time[0] > minimum_time_value
            ):
                minimum_block_time[0] = minimum_time_value
                minimum_block_time[1] = mac_source

            if "reset" in package_flags:
                rst_packages.append(
                    {
                        package_id: [
                            mac_source,
                            mac_destination,
                            package_flags,
                            [minimum_time_value],
                        ]
                    }
                )
                continue

            # добавляем в случае отсуствия пакета в таблице
            if package_id not in block_package_table.keys():
                block_package_table[package_id] = [
                    mac_source,
                    mac_destination,
                    package_flags,
                    [minimum_time_value],
                ]

            # в случае если пакет с таким ID есть - добавляем время, и сортируем его
            else:
                package_time = block_package_table[package_id][3]

                if len(package_time) == 2 and minimum_time_value not in package_time:
                    package_time[-1] = minimum_time_value
                    package_time.sort()

                elif len(package_time) <= 1:
                    package_time.append(minimum_time_value)
                    package_time.sort()

    middle_the_list = int(len(rst_packages) / 2)

    for package_index in range(0, int(len(rst_packages) / 2)):

        key = str((list(rst_packages[package_index].keys())[0])) + str(rst_package_id)

        packageA = list(rst_packages[package_index].values())[0]
        packageB = list(rst_packages[package_index + (middle_the_list)].values())[0]

        packageA[-1].append(packageB[-1][0])
        packageA[-1].sort()
        block_package_table[key] = packageA
        rst_package_id += 1

    # расстановка устройств
    for package_data in block_package_table.values():
        if package_data[0] == minimum_block_time[1]:
            package_data[0] = device_ID[-1]
            package_data[1] = device_ID[-1] + increasing_device_id

        else:
            package_data[1] = device_ID[-1]
            package_data[0] = device_ID[-1] + increasing_device_id

    package_table.update(block_package_table)
    device_ID.append(device_ID[-1] + increasing_device_id)


file_paths = [
    "point1.pcap",
    "point2.pcap",
    "point4.pcap",
    "point1.pcap",
    "point3.pcap",
    "point4.pcap",
]
file_paths.sort()


for file_index in range(0, len(file_paths)):
    if file_index % 2 == 0:
        ReadingFiles([file_paths[file_index], file_paths[file_index + 1]])


(Image.open(BytesIO(plotting(package_table, min_session_time, device_ID)))).save(
    "image/plot.png"
)
