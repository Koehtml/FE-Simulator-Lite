import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
import threading

class EnhancedPDFViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.images = []
        self.photo_images = []
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.create_widgets()
        
        # Show initial message
        self.show_load_message()
        
    def create_widgets(self):
        # Create canvas with scrollbar
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas for PDF display
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='white',
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Bind mouse wheel events specifically to this canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        
        # Bind click to load PDF
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def show_load_message(self):
        """Show message to load PDF"""
        self.canvas.delete("all")
        self.canvas.create_text(
            200, 150,
            text="Click here to load a PDF file",
            font=("Arial", 14),
            fill="gray"
        )
        
    def on_canvas_click(self, event):
        """Handle canvas click to load PDF"""
        if not self.pdf_document:
            self.load_pdf()
            
    def load_pdf(self):
        """Open file dialog and load PDF"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_pdf_file(file_path)
            
    def load_pdf_file(self, file_path):
        """Load PDF from file path"""
        try:
            # Load PDF in thread to avoid blocking UI
            def load_thread():
                try:
                    self.pdf_document = fitz.open(file_path)
                    self.total_pages = len(self.pdf_document)
                    self.current_page = 0
                    
                    # Update UI in main thread
                    self.after(0, self.display_current_page)
                    
                except Exception as e:
                    self.after(0, lambda: messagebox.showerror("Error", f"Failed to load PDF: {str(e)}"))
            
            thread = threading.Thread(target=load_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            
    def display_current_page(self):
        """Display the current page"""
        if not self.pdf_document:
            return
            
        try:
            # Get page
            page = self.pdf_document[self.current_page]
            
            # Calculate zoom to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Calculate zoom to fit
                page_rect = page.rect
                width_zoom = (canvas_width - 20) / page_rect.width
                height_zoom = (canvas_height - 20) / page_rect.height
                self.zoom_level = min(width_zoom, height_zoom) * 0.8  # 80% of fit
            
            # Render page
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas and display
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            
            # Keep reference
            self.current_photo = photo
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
            
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta == -120:  # scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:  # scroll up
            self.canvas.yview_scroll(-1, "units")
            
    def next_page(self):
        """Go to next page"""
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_current_page()
            
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level *= 1.2
        if self.pdf_document:
            self.display_current_page()
            
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level /= 1.2
        if self.pdf_document:
            self.display_current_page() 