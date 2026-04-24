import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt


class SleepTrackerApp:
    def __init__(self, root):
        # Main window setup
        self.root = root
        self.root.title("Multi-Person Sleep Tracker")
        self.root.geometry("950x650")

        # Dictionary that stores each person's sleep data
        # Example:
        # {
        #   "Candry": [
        #       {"start": "10:30", "start_ampm": "PM", "end": "7:00", "end_ampm": "AM"}
        #   ]
        # }
        self.people = {}

        # Keeps track of which person is currently selected
        self.current_person = None

        # Stores the current visible input rows
        self.night_rows = []

        self.build_gui()

    def build_gui(self):
        # Main container frame
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        # ---------------- LEFT SIDE: PEOPLE LIST ----------------
        left = ttk.LabelFrame(main, text="People", padding=10)
        left.pack(side="left", fill="y", padx=10)

        ttk.Label(left, text="Person name:").pack(anchor="w")

        # Input box for adding a person's name
        self.name_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.name_var, width=25).pack(pady=5)

        # Button to add the typed person
        ttk.Button(left, text="Add Person", command=self.add_person).pack(pady=5)

        # Frame where person buttons will appear
        self.people_frame = ttk.Frame(left)
        self.people_frame.pack(fill="y", expand=True, pady=10)

        # ---------------- RIGHT SIDE: SLEEP INPUTS ----------------
        right = ttk.LabelFrame(main, text="Sleep Inputs", padding=10)
        right.pack(side="right", fill="both", expand=True, padx=10)

        top_inputs = ttk.Frame(right)
        top_inputs.pack(fill="x")

        ttk.Label(top_inputs, text="Number of nights:").grid(row=0, column=0, padx=5)

        # Input box for number of nights
        self.nights_var = tk.StringVar()
        ttk.Entry(top_inputs, textvariable=self.nights_var, width=8).grid(row=0, column=1, padx=5)

        # Creates or updates the number of night rows
        ttk.Button(top_inputs, text="Generate Nights", command=self.generate_nights).grid(row=0, column=2, padx=5)

        # Shows who is currently selected
        self.selected_label = ttk.Label(right, text="Selected person: None", font=("Arial", 11, "bold"))
        self.selected_label.pack(anchor="w", pady=10)

        # Frame where night input rows appear
        self.inputs_frame = ttk.Frame(right)
        self.inputs_frame.pack(fill="both", expand=True)

        # Bottom buttons
        bottom = ttk.Frame(right)
        bottom.pack(fill="x", pady=10)

        ttk.Button(bottom, text="Save This Person's Times", command=self.save_current_person_times).pack(side="left", padx=5)
        ttk.Button(bottom, text="Graph Sleep Data", command=self.graph_data).pack(side="left", padx=5)

        # Result/average label
        self.result_label = ttk.Label(right, text="", font=("Arial", 10, "bold"))
        self.result_label.pack(anchor="w", pady=10)

    def add_person(self):
        # Get the typed name
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Please enter a person's name.")
            return

        if name in self.people:
            messagebox.showerror("Error", "That person already exists.")
            return

        # Add person with an empty list of nights
        self.people[name] = []

        # Clear name input
        self.name_var.set("")

        # Refresh the visible people list
        self.refresh_people_list()

        # Automatically select the first person added
        if self.current_person is None:
            self.select_person(name)

    def remove_person(self, name):
        # Remove person from dictionary
        if name in self.people:
            del self.people[name]

        # If the removed person was selected, clear the screen
        if self.current_person == name:
            self.current_person = None
            self.selected_label.config(text="Selected person: None")
            self.clear_night_inputs()

        self.refresh_people_list()

    def refresh_people_list(self):
        # Clear old person buttons
        for widget in self.people_frame.winfo_children():
            widget.destroy()

        # Rebuild person buttons
        for name in self.people:
            row = ttk.Frame(self.people_frame)
            row.pack(fill="x", pady=3)

            # Clicking name switches to that person
            ttk.Button(row, text=name, command=lambda n=name: self.select_person(n)).pack(
                side="left", fill="x", expand=True
            )

            # Remove button deletes that person
            ttk.Button(row, text="Remove", command=lambda n=name: self.remove_person(n)).pack(
                side="right", padx=5
            )

    def select_person(self, name):
        # Save current person's data before switching
        self.save_current_person_times(silent=True)

        self.current_person = name
        self.selected_label.config(text=f"Selected person: {name}")

        # If this person already has data, load it
        if self.people[name]:
            self.load_person_times(name)
        else:
            self.clear_night_inputs()

    def clear_night_inputs(self):
        # Remove all current night input widgets
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        # Clear stored row references
        self.night_rows.clear()

    def generate_nights(self):
        # Must have a selected person first
        if self.current_person is None:
            messagebox.showerror("Error", "Please add and select a person first.")
            return

        # Validate number of nights
        try:
            new_nights = int(self.nights_var.get())
            if new_nights <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a positive whole number of nights.")
            return

        # Save whatever is currently typed before changing row count
        existing_data = []

        for row in self.night_rows:
            existing_data.append({
                "start": row["start"].get().strip(),
                "start_ampm": row["start_ampm"].get(),
                "end": row["end"].get().strip(),
                "end_ampm": row["end_ampm"].get()
            })

        # If going from 7 days to 5 days, keep days 1-5 only
        existing_data = existing_data[:new_nights]

        # If going from 5 days to 7 days, add blank rows for days 6 and 7
        while len(existing_data) < new_nights:
            existing_data.append({
                "start": "",
                "start_ampm": "PM",
                "end": "",
                "end_ampm": "AM"
            })

        # Clear old visible rows
        self.clear_night_inputs()

        # Header labels
        headers = ["Day", "Sleep Start", "AM/PM", "Wake Time", "AM/PM"]

        for col, header in enumerate(headers):
            ttk.Label(self.inputs_frame, text=header, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=10, pady=5
            )

        # Create rows using saved data
        for i, saved in enumerate(existing_data):
            start_var = tk.StringVar(value=saved["start"])
            start_ampm = tk.StringVar(value=saved["start_ampm"])
            end_var = tk.StringVar(value=saved["end"])
            end_ampm = tk.StringVar(value=saved["end_ampm"])

            ttk.Label(self.inputs_frame, text=f"Day {i + 1}").grid(
                row=i + 1, column=0, padx=10, pady=5
            )

            ttk.Entry(self.inputs_frame, textvariable=start_var, width=12).grid(
                row=i + 1, column=1, padx=10, pady=5
            )

            ttk.Combobox(
                self.inputs_frame,
                textvariable=start_ampm,
                values=["AM", "PM"],
                width=5,
                state="readonly"
            ).grid(row=i + 1, column=2, padx=10, pady=5)

            ttk.Entry(self.inputs_frame, textvariable=end_var, width=12).grid(
                row=i + 1, column=3, padx=10, pady=5
            )

            ttk.Combobox(
                self.inputs_frame,
                textvariable=end_ampm,
                values=["AM", "PM"],
                width=5,
                state="readonly"
            ).grid(row=i + 1, column=4, padx=10, pady=5)

            # Store references to this row's variables
            self.night_rows.append({
                "start": start_var,
                "start_ampm": start_ampm,
                "end": end_var,
                "end_ampm": end_ampm
            })

        # Save updated rows to current person
        self.save_current_person_times(silent=True)

    def load_person_times(self, name):
        # Load saved data for selected person
        data = self.people[name]

        # Set number of nights box to match saved data
        self.nights_var.set(str(len(data)))

        # Generate the correct number of rows
        self.generate_nights()

        # Fill rows with saved values
        for row, saved in zip(self.night_rows, data):
            row["start"].set(saved["start"])
            row["start_ampm"].set(saved["start_ampm"])
            row["end"].set(saved["end"])
            row["end_ampm"].set(saved["end_ampm"])

    def save_current_person_times(self, silent=False):
        # Do nothing if no person or rows exist
        if self.current_person is None or not self.night_rows:
            return

        saved_data = []

        # Pull values from each row
        for row in self.night_rows:
            saved_data.append({
                "start": row["start"].get().strip(),
                "start_ampm": row["start_ampm"].get(),
                "end": row["end"].get().strip(),
                "end_ampm": row["end_ampm"].get()
            })

        # Save data under current person's name
        self.people[self.current_person] = saved_data

        if not silent:
            messagebox.showinfo("Saved", f"Saved times for {self.current_person}.")

    def parse_time(self, time_str, ampm):
        # Converts 12-hour time into minutes after midnight
        # Example:
        # 10:30 PM -> 1350 minutes
        # 7:00 AM -> 420 minutes

        try:
            parts = time_str.strip().split(":")

            if len(parts) != 2:
                raise ValueError

            hour = int(parts[0])
            minute = int(parts[1])

            if hour < 1 or hour > 12:
                raise ValueError

            if minute < 0 or minute > 59:
                raise ValueError

            # Convert AM/PM to 24-hour time
            if ampm == "AM":
                if hour == 12:
                    hour = 0
            else:
                if hour != 12:
                    hour += 12

            return hour * 60 + minute

        except Exception:
            raise ValueError(f"Invalid time: {time_str} {ampm}")

    def calculate_duration_hours(self, start, start_ampm, end, end_ampm):
        # Convert start and end times to minutes
        start_minutes = self.parse_time(start, start_ampm)
        end_minutes = self.parse_time(end, end_ampm)

        # If wake time is earlier than sleep time, assume sleep went overnight
        # Example:
        # 10 PM to 7 AM
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60

        duration_minutes = end_minutes - start_minutes

        # Convert minutes to hours as a decimal
        return duration_minutes / 60

    def graph_data(self):
        # Save current person's data before graphing
        self.save_current_person_times(silent=True)

        if not self.people:
            messagebox.showerror("Error", "Add at least one person first.")
            return

        plt.figure(figsize=(10, 6))

        graphed_anyone = False
        summary_text = ""

        # Loop through each person and graph their sleep data
        for person, nights in self.people.items():
            if not nights:
                continue

            days = []
            hours_slept = []

            try:
                for i, night in enumerate(nights, start=1):
                    duration = self.calculate_duration_hours(
                        night["start"],
                        night["start_ampm"],
                        night["end"],
                        night["end_ampm"]
                    )

                    days.append(i)
                    hours_slept.append(duration)

            except ValueError as e:
                messagebox.showerror("Input Error", f"{person}: {e}")
                return

            if hours_slept:
                graphed_anyone = True

                # Scatter points
                plt.scatter(days, hours_slept, label=person)

                # Line connecting the points
                plt.plot(days, hours_slept)

                # Calculate person's average
                avg = sum(hours_slept) / len(hours_slept)
                summary_text += f"{person}: average = {avg:.2f} hours\n"

        if not graphed_anyone:
            messagebox.showerror("Error", "No sleep data to graph.")
            return

        # Find the largest number of nights among all people
        max_days = max(len(nights) for nights in self.people.values())

        # Graph labels and settings
        plt.title("Sleep Time by Day")
        plt.xlabel("Day")
        plt.ylabel("Hours Slept")
        plt.xticks(range(1, max_days + 1))
        plt.grid(True)

        # Legend/key showing which person is which
        plt.legend(title="People")

        self.result_label.config(text=summary_text)

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Creates the app window and starts the GUI
    root = tk.Tk()
    app = SleepTrackerApp(root)
    root.mainloop()