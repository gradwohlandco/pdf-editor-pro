import PyPDF2
import fitz  # PyMuPDF
import customtkinter as ctk
from tkinter import filedialog, Scrollbar, Canvas, Frame
from PIL import Image
from customtkinter import CTkImage


class PDFEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Editor")
        self.geometry("1000x600")

        # IMPORTANT: echte Python-Liste (fix für dein Error)
        self.pages = []
        self.previews = []
        self.pdf_path = None

        # ---------------- UI ----------------
        self.load_pdf_button = ctk.CTkButton(
            self, text="Load PDF", command=self.load_pdf
        )
        self.load_pdf_button.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        ctk.CTkButton(
            self.button_frame, text="Merge PDFs", command=self.merge_pdfs
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            self.button_frame, text="Save PDF", command=self.save_pdf
        ).pack(side="left", padx=10)

        # ---------------- SCROLL AREA ----------------
        self.frame = Frame(self)
        self.frame.pack(fill="both", expand=True)

        self.canvas = Canvas(self.frame)
        self.scrollbar = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    # ---------------- LOAD PDF ----------------
    def load_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not self.pdf_path:
            return

        reader = PyPDF2.PdfReader(self.pdf_path)

        # FIX: echte Liste
        self.pages = list(reader.pages)

        self.previews = self.render_previews(self.pdf_path, len(self.pages))
        self.display_pages()

    # ---------------- PREVIEWS ----------------
    def render_previews(self, path, count):
        doc = fitz.open(path)
        previews = []

        for i in range(count):
            page = doc.load_page(i)
            pix = page.get_pixmap()

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((100, 100))

            previews.append(
                CTkImage(light_image=img, dark_image=img, size=(100, 100))
            )

        doc.close()
        return previews

    # ---------------- DISPLAY ----------------
    def display_pages(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i in range(len(self.pages)):
            self.display_page(i)

    def display_page(self, i):
        ctk.CTkLabel(
            self.scrollable_frame,
            image=self.previews[i],
            text=""
        ).grid(row=i, column=0, padx=10, pady=5)

        ctk.CTkLabel(
            self.scrollable_frame,
            text=f"Page {i + 1}"
        ).grid(row=i, column=1)

        ctk.CTkButton(
            self.scrollable_frame,
            text="↑",
            command=lambda i=i: self.move_up(i)
        ).grid(row=i, column=2)

        ctk.CTkButton(
            self.scrollable_frame,
            text="X",
            fg_color="red",
            command=lambda i=i: self.delete(i)
        ).grid(row=i, column=3)

        ctk.CTkButton(
            self.scrollable_frame,
            text="↓",
            command=lambda i=i: self.move_down(i)
        ).grid(row=i, column=4)

    # ---------------- ACTIONS ----------------
    def move_up(self, i):
        if i <= 0:
            return
        self.swap(i, i - 1)

    def move_down(self, i):
        if i >= len(self.pages) - 1:
            return
        self.swap(i, i + 1)

    def swap(self, i, j):
        self.pages[i], self.pages[j] = self.pages[j], self.pages[i]
        self.previews[i], self.previews[j] = self.previews[j], self.previews[i]
        self.display_pages()

    def delete(self, i):
        del self.pages[i]
        del self.previews[i]
        self.display_pages()

    # ---------------- SAVE ----------------
    def save_pdf(self):
        writer = PyPDF2.PdfWriter()

        for page in self.pages:
            writer.add_page(page)

        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            with open(path, "wb") as f:
                writer.write(f)

    # ---------------- MERGE ----------------
    def merge_pdfs(self):
        paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not paths:
            return

        for path in paths:
            reader = PyPDF2.PdfReader(path)

            pages = list(reader.pages)
            self.pages.extend(pages)

            self.previews.extend(
                self.render_previews(path, len(pages))
            )

        self.display_pages()


if __name__ == "__main__":
    app = PDFEditor()
    app.mainloop()