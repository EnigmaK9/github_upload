import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import requests

# The initial interface configuration is set up
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# The path to the configuration file is defined
CONFIG_FILE = "github_credentials.json"

class GitHubUploaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GitHub ZIP Uploader")
        # Window size is increased for more vertical space
        self.geometry("400x450")

        # Input variables are initialized
        self.zip_path = tk.StringVar()
        self.token = tk.StringVar()
        self.repo_name = tk.StringVar()
        self.release_tag = tk.StringVar()
        self.is_prerelease = tk.BooleanVar()

        # Configuration is loaded if it exists
        self.load_config()

        # The graphical interface is created
        self.create_widgets()

    def create_widgets(self):
        # The GitHub Token field is set up with an example
        ctk.CTkLabel(self, text="GitHub Token (example: ghp_xxxxxxxx)").pack(pady=5)
        token_entry = ctk.CTkEntry(self, textvariable=self.token, show="*")
        token_entry.pack(pady=5)
        token_entry.insert(0, "ghp_exampletoken1234")

        # The Repository field is set up with an example
        ctk.CTkLabel(self, text="Repository (example: owner/repo)").pack(pady=5)
        repo_entry = ctk.CTkEntry(self, textvariable=self.repo_name)
        repo_entry.pack(pady=5)
        repo_entry.insert(0, "owner/repository")

        # The Release Tag field is set up with an example
        ctk.CTkLabel(self, text="Release Tag (example: v1.0.0)").pack(pady=5)
        tag_entry = ctk.CTkEntry(self, textvariable=self.release_tag)
        tag_entry.pack(pady=5)
        tag_entry.insert(0, "v1.0.0")

        # A checkbox for indicating prerelease status is added
        ctk.CTkCheckBox(self, text="Pre-release", variable=self.is_prerelease).pack(pady=5)

        # A button for selecting the ZIP file is added
        ctk.CTkButton(self, text="Select ZIP File", command=self.select_file).pack(pady=10)

        # A label for displaying the selected file is added
        self.selected_file_label = ctk.CTkLabel(self, textvariable=self.zip_path)
        self.selected_file_label.pack(pady=5)

        # A button for uploading the file to GitHub is added
        ctk.CTkButton(self, text="Upload to GitHub", command=self.upload_file).pack(pady=10)

        # A button for saving the token to the configuration file is added
        ctk.CTkButton(self, text="Save Token", command=self.save_config).pack(pady=10)

    def select_file(self):
        try:
            # The file selection dialog is opened
            file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
            if file_path:
                self.zip_path.set(file_path)
        except Exception as e:
            # An error message is displayed if file selection fails
            messagebox.showerror("Error", f"An error occurred while selecting file: {str(e)}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                # The token is loaded from the JSON file
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.token.set(config.get("token", ""))
            except json.JSONDecodeError:
                # An error message is displayed if the JSON format is invalid
                messagebox.showerror("Error", "Failed to load config: Invalid JSON format.")
            except Exception as e:
                # An error message is displayed if loading the config fails
                messagebox.showerror("Error", f"An error occurred while loading config: {str(e)}")

    def save_config(self):
        try:
            # The token is saved to the JSON file
            config = {"token": self.token.get()}
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
            # A success message is displayed upon saving
            messagebox.showinfo("Saved", "Token saved successfully!")
        except Exception as e:
            # An error message is displayed if saving the config fails
            messagebox.showerror("Error", f"An error occurred while saving config: {str(e)}")

    def upload_file(self):
        # It is checked that all required fields are filled
        if not all([self.token.get(), self.repo_name.get(), self.release_tag.get(), self.zip_path.get()]):
            messagebox.showerror("Error", "All fields are required.")
            return

        headers = {"Authorization": f"token {self.token.get()}"}
        data = {
            "tag_name": self.release_tag.get(),
            "name": self.release_tag.get(),
            "prerelease": self.is_prerelease.get()
        }
        repo_url = f"https://api.github.com/repos/{self.repo_name.get()}/releases"

        try:
            # The release creation request is sent to GitHub
            response = requests.post(repo_url, headers=headers, json=data)
            response.raise_for_status()

            release_data = response.json()
            upload_url = release_data["upload_url"].replace("{?name,label}", "")
            with open(self.zip_path.get(), "rb") as zip_file:
                # The ZIP file is uploaded to the release
                files = {"file": (os.path.basename(self.zip_path.get()), zip_file)}
                upload_response = requests.post(
                    upload_url,
                    headers={**headers, "Content-Type": "application/zip"},
                    params={"name": os.path.basename(self.zip_path.get())},
                    files=files
                )
                upload_response.raise_for_status()
                # A success message is displayed if the file is uploaded
                messagebox.showinfo("Success", "File uploaded successfully!")
        except requests.exceptions.HTTPError as e:
            # An error message is displayed if an HTTP error occurs
            messagebox.showerror("HTTP Error", f"Failed to communicate with GitHub: {str(e)}")
        except requests.exceptions.RequestException as e:
            # An error message is displayed if a request error occurs
            messagebox.showerror("Request Error", f"An error occurred during upload: {str(e)}")
        except FileNotFoundError:
            # An error message is displayed if the selected file is not found
            messagebox.showerror("File Error", "The selected file could not be found.")
        except Exception as e:
            # A general error message is displayed for any unexpected error
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # The application is started
    app = GitHubUploaderApp()
    app.mainloop()

