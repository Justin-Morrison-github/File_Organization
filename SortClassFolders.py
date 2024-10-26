from pathlib import Path
from enum import StrEnum
from move import user_continues, ARROW
from colorama import Fore
import json


class Folders(StrEnum):
    ASSIGNMENT = "Assignment"
    INFO = "Info"
    LAB = "Lab"
    LECTURE = "Lecture"
    PASS = "Pass"
    PRACTICE = "Practice"
    REVIEW = "Review"
    TEXTBOOK = "Textbook"
    TUTORIAl = "Tutorial"
    WOOCLAP = "Wooclap"

    # 1st year FALL
    MATH1004 = "Calculus"
    CHEM1101 = "Chemistry"
    ECOR1048 = "Dynamics"
    ECOR1055 = "Eng Disciplines"
    ECOR1057 = "Eng Profession"
    ECOR1046 = "Mechanics"
    ECOR1045 = "Statics"
    PHYS1003 = "Thermodynamics"
    ECOR1047 = "Visual Communication"

    # 1st year WINTER
    ECOR1043 = "Circuits"
    ECOR1042 = "Data Management"
    PHYS1004 = "Electromagnetism"
    ECOR1056 = "Eng Disciplines 2"
    GEOG1020 = "Geography"
    MATH1104 = "Linear Algebra"
    ECOR1044 = "Mechatronics"
    ECOR1041 = "Programming"

    # 2nd year FALL
    ELEC2501 = "Circuits and Signals"
    MATH1005 = "Differential Equations"
    SYSC2310 = "Digital Systems"
    COMP1805 = "Discrete Structures I"
    SYSC2006 = "Imperative Programming"

    # 2nd year WINTER
    SYSC2100 = "Algorithms and Data Structures"
    CCDP2100 = "CCDP"
    SYSC2320 = "Computer Architecture"
    COMP2804 = "Discrete Structures II"
    SYSC2004 = "Object Oriented Software Development"

    def __repr__(self):
        return self.value


class Packet():
    def __init__(self, src: Path, dst: Path, parent: Path, course: Folders, file_number: int = None):
        self.src = src
        self.dst = dst
        self.parent = parent
        self.course = course
        self.name = self.src.stem

        if file_number:
            self.file_number = file_number
        else:
            self.file_number = None

        self.update_packet_if_needed()

    def __str__(self):
        return f"\t{ARROW} SRC:  {self.src.parent.name}\\{self.src.name}\n\t{ARROW} DST:  {self.dst.parent.name}\\{self.dst.name}\n"

    def __repr__(self):
        return f"(src: {self.src.parent.name}\\{self.src.name}, dst: {self.dst.parent.name}\\{self.dst.name})"

    def update_packet_if_needed(self):
        stem = self.src.stem.lower().split()
        index = stem.index(self.parent.lower())
        dst_folder = ""

        if self.parent == Folders.ASSIGNMENT or self.parent == Folders.LAB:
            self.file_number = int(stem[index + 1])

            for folder in self.dst.parent.iterdir():
                if f"{self.parent.title()} {self.file_number}" in folder.name:
                    dst_folder = folder
                    break

        new_dst: Path = self.dst.parent / dst_folder / self.dst.name
        self.dst = new_dst


def main():
    root = Path("C:\\Users\\morri\\OneDrive\\University")
    if not root.exists():
        print('Error')
        exit()

    file = Path("JSON/course_data.json")

    with open(file, 'r') as json_file:
        course_data: dict = json.load(json_file)

    course_dict = {}

    for year, semesters in course_data.items():
        for semester, classlist in semesters.items():
            for course in classlist:
                course_dict.setdefault(
                    year, {}).setdefault(
                    semester, {}).setdefault(
                    course, [])

                course_dict[year][semester][course] = classlist[course]
    print(course_dict)

    # setup_folders(root, course_dict)
    packets_to_be_sent = make_packets(root, course_dict)
    print(packets_to_be_sent)
    if len(packets_to_be_sent) == 0:
        print("No files found...")
    else:
        process_packets(packets_to_be_sent, "print")

        if user_continues():
            process_packets(packets_to_be_sent, "send", True)


def setup_folders(root: Path, courses: dict):
    for course in root.iterdir():
        if course.name in courses:
            class_path = root / course
            for folder in courses[course.name]:
                dir = Path(class_path / folder)
                if not dir.exists():
                    print(f"Making {dir.name}")
                    dir.mkdir()


def make_packets(root: Path, course_dict: dict):
    packet_dict = {}
    for year, semesters in course_dict.items():
        for semester, courses in semesters.items():
            for course, folders in courses.items():
                class_path: Path = root / year / semester / Folders[course]
                if not class_path.exists():
                    print(f"Error {class_path} does not exist")
                    exit()

                for folder in folders:
                    matching_files = list(class_path.glob(f"* {folder} *"))
                    if matching_files:
                        dest_folder: Path = class_path / Folders[folder]
                        for file in matching_files:
                            dest = dest_folder / file.name
                            packet = Packet(file, dest, Folders[folder], course)
                            packet_dict.setdefault(course, {}).setdefault(dest_folder.name, []).append(packet)

    return packet_dict


def process_packets(packet_dict: dict, command="print", send_enabled=False):
    action = "Sending" if send_enabled else "Files to be sent"
    print(f"\n{action}:")

    for course in packet_dict:
        print(f"{Fore.CYAN}{course}: {Folders[course]}{Fore.RESET}")
        for folder in packet_dict[course]:
            print(f"{Fore.YELLOW}  {folder}{Fore.RESET}")
            for packet in packet_dict[course][folder]:
                if command == "print":
                    print(packet)
                elif command == "send":
                    if send_enabled:
                        send_packet(packet, send_enabled)
                    else:
                        print("Send is Not Enabled")


def send_packet(packet: Packet, send_enabled=False) -> None:
    """
    Sends a packet from packet.src to packet.dst. Prints out success or failure
    """

    try:
        if packet.dst.exists():
            print(f"\t{Fore.GREEN}\u2705 From:  {packet.src}")
            print(f"\t{Fore.RED}\u274C   To:  {packet.dst}")
            print(f"\t{Fore.YELLOW}WARNING: File Already Exists")
        else:
            if send_enabled:
                packet.src.rename(packet.dst)
            print(f"\t{Fore.GREEN}\u2705 From:  {packet.src}")
            print(f"\t{Fore.GREEN}\u2705   To:  {packet.dst}", end="")

    except FileNotFoundError as e:
        print(f"\t{Fore.YELLOW}\u274C From:  {packet.src}")
        print(f"\t{Fore.YELLOW}\u274C   To:  {packet.dst}")
        print(f"\t{Fore.RED}ERROR: File Not Found {e}")

    print(Fore.RESET + "\n")


if __name__ == "__main__":
    main()
