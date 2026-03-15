import tkinter as tk
from tkinter import messagebox, scrolledtext, colorchooser, font as tkFont
import requests
from PIL import Image, ImageTk
import io

last_message_id = None
embed_color = 0x5865F2
dark_mode = False

LIGHT_THEME = {
    "bg": "SystemButtonFace",
    "fg": "black",
    "entry_bg": "white",
    "entry_fg": "black",
    "button_bg": "lightgray",
    "button_fg": "black",
    "preview_bg": "white",
}

DARK_THEME = {
    "bg": "#2C2F33",
    "fg": "white",
    "entry_bg": "#23272A",
    "entry_fg": "white",
    "button_bg": "#5865F2",
    "button_fg": "white",
    "preview_bg": "#2C2F33",
}
def choose_color():
    global embed_color
    color_code = colorchooser.askcolor(title="Choose Embed Color")
    if color_code[0] is not None:
        r, g, b = color_code[0]
        embed_color = (int(r) << 16) + (int(g) << 8) + int(b)
        color_button.config(bg=color_code[1])
        update_preview()

def get_webhook_url():
    url = webhook_entry.get().strip()
    if not url:
        messagebox.showwarning("Warning", "Webhook URL cannot be empty!")
        return None
    if "?wait=true" not in url:
        url += "?wait=true"
    return url

def test_webhook():
    url = get_webhook_url()
    if not url:
        return
    data = {"content": "It Works"}
    response = requests.post(url, json=data)
    if response.status_code in (200, 204):
        messagebox.showinfo("Webhook Test", "Webhook is valid")
    else:
        messagebox.showerror("Webhook Test", f"Failed: {response.status_code}\n{response.text}")

def send_message():
    global last_message_id
    url = get_webhook_url()
    if not url:
        return
    content = text_entry.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Warning", "Message cannot be empty!")
        return
    title = title_entry.get().strip() or "Message"
    img_url = img_entry.get().strip()

    if embed_var.get():
        embed_dict = {"title": title, "description": content, "color": embed_color}
        if img_url:
            embed_dict["image"] = {"url": img_url}
        data = {"embeds": [embed_dict]}
    else:
        data = {"content": content}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        last_message_id = response.json()["id"]
        messagebox.showinfo("Success", "Message sent!")
        text_entry.delete("1.0", tk.END)
        update_preview()
    else:
        messagebox.showerror("Error", f"Failed: {response.status_code}\n{response.text}")

def delete_last():
    global last_message_id
    url = get_webhook_url()
    if not url:
        return
    if not last_message_id:
        messagebox.showwarning("Warning", "No recent message to delete!")
        return
    delete_url = f"{url.split('?')[0]}/messages/{last_message_id}"
    response = requests.delete(delete_url)
    if response.status_code == 204:
        messagebox.showinfo("Deleted", "Last message deleted!")
        last_message_id = None
        update_preview()
    else:
        messagebox.showerror("Error", f"Failed: {response.status_code}\n{response.text}")

def fetch_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        img_data = response.content
        image = Image.open(io.BytesIO(img_data))
        image.thumbnail((200, 120))
        return ImageTk.PhotoImage(image)
    except Exception:
        return None

def update_preview(event=None):
    for widget in preview_frame.winfo_children():
        widget.destroy()

    if embed_var.get():
        title = title_entry.get().strip() or "Message"
        description = text_entry.get("1.0", tk.END).strip()
        img_url = img_entry.get().strip()
        hex_color = f"#{embed_color:06x}"

        theme = DARK_THEME if dark_mode else LIGHT_THEME

        main_frame = tk.Frame(preview_frame, bg=theme["preview_bg"])
        main_frame.pack(fill="both", expand=True)

        color_bar = tk.Frame(main_frame, bg=hex_color, width=6)
        color_bar.pack(side="left", fill="y")

        content_frame = tk.Frame(main_frame, bg=theme["preview_bg"])
        content_frame.pack(side="left", fill="both", expand=True, padx=(5, 2), pady=2)

        tk.Label(content_frame, text=title, font=("Arial", 10, "bold"),
                 bg=theme["preview_bg"], fg=theme["fg"]).pack(anchor="w")
        tk.Label(content_frame, text=description, wraplength=200, justify="left",
                 bg=theme["preview_bg"], fg=theme["fg"]).pack(anchor="w")

        if img_url:
            photo = fetch_image(img_url)
            if photo:
                content_frame.image = photo
                tk.Label(content_frame, image=photo, bg=theme["preview_bg"]).pack(anchor="w", pady=(2, 0))
            else:
                tk.Label(content_frame, text="[Image failed to load]", fg="red", bg=theme["preview_bg"]).pack(anchor="w")
    else:
        theme = DARK_THEME if dark_mode else LIGHT_THEME
        tk.Label(preview_frame, text="Embed preview disabled", fg="gray", bg=theme["preview_bg"]).pack()

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme(DARK_THEME if dark_mode else LIGHT_THEME)
    btn_theme.config(text="☀" if dark_mode else "🌙")
    update_preview()

def apply_theme(theme):
    root.configure(bg=theme["bg"])
    left_frame.configure(bg=theme["bg"])
    right_frame.configure(bg=theme["bg"])
    preview_frame.configure(bg=theme["preview_bg"])

    text_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
    title_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
    webhook_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
    img_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])

    send_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
    delete_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
    test_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
    color_button.configure(bg="#5865F2", fg="white")

    embed_check.configure(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["bg"])

root = tk.Tk()
root.title("Discord Webhook App")
root.geometry("560x260")
root.resizable(False, False)

left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="y", padx=5, pady=5)

text_entry = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=28, height=5)
text_entry.pack(fill="both", expand=False)

preview_frame = tk.Frame(left_frame, relief="solid", bd=1, height=120)
preview_frame.pack(fill="x", pady=(5, 0))
preview_frame.pack_propagate(False)

img_entry = tk.Entry(left_frame, width=40)
img_entry.pack(pady=(5, 0))
img_entry.insert(0, "image URL here")

send_button = tk.Button(right_frame, text="Send Message", width=15, command=send_message)
send_button.pack(pady=(5, 2))
delete_button = tk.Button(right_frame, text="Delete Last", width=15, command=delete_last)
delete_button.pack(pady=2)
test_button = tk.Button(right_frame, text="Test Webhook", width=15, command=test_webhook)
test_button.pack(pady=2)

embed_var = tk.BooleanVar()
embed_check = tk.Checkbutton(right_frame, text="Send as Embed", variable=embed_var, command=update_preview)
embed_check.pack(pady=2)

title_entry = tk.Entry(right_frame, width=18)
title_entry.pack(pady=2)
title_entry.insert(0, "Message")

webhook_entry = tk.Entry(right_frame, width=18)
webhook_entry.pack(pady=(2, 2))
webhook_entry.insert(0, "Webhook")

color_button = tk.Button(
    right_frame,
    text="Choose Embed Color",
    width=18,
    command=choose_color,
    bg="#5865F2",
    fg="white"
)
color_button.pack(pady=(2, 5))

btn_theme = tk.Button(root, text="🌙", command=toggle_theme, width=2, height=1)
btn_theme.place(relx=1.0, rely=1.0, x=-5, y=-5, anchor="se")

text_entry.bind("<KeyRelease>", update_preview)
title_entry.bind("<KeyRelease>", update_preview)
img_entry.bind("<KeyRelease>", update_preview)
embed_var.trace("w", update_preview)

apply_theme(LIGHT_THEME)
update_preview()

root.mainloop()
